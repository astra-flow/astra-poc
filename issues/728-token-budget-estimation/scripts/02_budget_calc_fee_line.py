"""
最终版：模型名清洗 + 用市场真实单价反推自洽的 Token 预算
核心逻辑：调研表费用数据自洽可信，Token数字虚高不可信
         → 用费用 ÷ 真实单价 反推合理 Token 量
"""
import openpyxl
from collections import defaultdict

wb = openpyxl.load_workbook('敏捷软件开发AI应用需求情况统计.xlsx', data_only=True)

# ============ 市场真实单价（元/百万Token，来自阿里云官方文档 2026-06-24）============
# 取输入+输出加权均价（假设输入:输出=3:1，输出价约为输入的3倍）
# 加权单价 = (输入价×3 + 输出价×1) / 4
MARKET_PRICE = {
    # 模型族: (输入价元/百万Token, 输出价元/百万Token, 数据来源)
    'DeepSeek-V4':      (14.4,  28.8),   # 阿里云 deepseek-v4-pro 官方价
    'Qwen3-Max':        (14.4,  43.2),   # 阿里云 qwen3.7-max 官方价（调研表用 Qwen3/Qwen3.7plus 多为旗舰档）
    'Qwen3-Plus':       (2.4,   9.6),    # 阿里云 qwen3.7-plus（均衡型，代码生成常用）
    'GLM-5':            (14.4,  28.8),   # 智谱 GLM-5 旗舰档（按行业同类旗舰价估算，实际以智谱报价为准）
    'Gemini':           (14.4,  43.2),   # Google Gemini 旗舰档（按国际价折算）
    'Doubao-Seed-Code': (2.4,   9.6),    # 字节豆袋代码模型（按同类代码模型价估算）
    'Claude-Code':      (21.6,  86.4),   # Anthropic Claude Sonnet 折算（$3/$15 × 7.2汇率）
    'Codex':            (21.6,  86.4),   # OpenAI Codex（按 GPT 系列折算）
    'Kimi':             (7.2,   21.6),   # 月之暗面 Kimi
    'MiniMax':          (7.2,   21.6),   # MiniMax
    'Qoder':            (21.6,  86.4),   # 阿里 Qoder（按高阶代码模型估算）
}

def weighted_price(model):
    """输入:输出=3:1 加权均价（元/百万Token）"""
    if model in MARKET_PRICE:
        inp, out = MARKET_PRICE[model]
        return (inp * 3 + out * 1) / 4
    return None

# ============ 模型名归一化映射（更细致的分级）============
def normalize_model(raw):
    if not raw or raw in ('无', '-', '—', 'None'):
        return None
    s = str(raw).lower().replace(' ', '').replace('\n', '').replace('_', '').replace('，', '')
    # DeepSeek 系列
    if 'deepseek' in s:
        if 'pro' in s or 'v4-pro' in s or 'v4pro' in s:
            return 'DeepSeek-V4'
        return 'DeepSeek-V4'  # 统一归到旗舰
    # Qwen 系列 - 区分 Max / Plus
    if 'qwen' in s or '千问' in s:
        if 'max' in s or '3.7' in s or 'plus' in s:
            # 调研表多为代码生成场景，Qwen3 系列在代码生成多用 Plus 档
            if 'max' in s:
                return 'Qwen3-Max'
            return 'Qwen3-Plus'
        if '系列' in s:
            return 'Qwen3-Plus'  # 泛指按均衡型
        return 'Qwen3-Plus'
    # GLM
    if 'glm' in s or 'gml' in s:
        return 'GLM-5'
    # Doubao
    if 'doubao' in s or 'duubao' in s:
        return 'Doubao-Seed-Code'
    # Gemini
    if 'gemini' in s:
        return 'Gemini'
    # Claude
    if 'claue' in s or 'claude' in s:
        return 'Claude-Code'
    # Codex
    if 'codex' in s:
        return 'Codex'
    # Kimi
    if 'kimi' in s:
        return 'Kimi'
    # MiniMax
    if 'minmax' in s or 'minimax' in s:
        return 'MiniMax'
    # Qoder
    if 'qoder' in s:
        return 'Qoder'
    return None  # 未识别返回 None，不计入

# ============ 解析两个 Sheet ============
ws1 = wb['应用产品']
ws2 = wb['基础软件']

# 应用产品：4 场景
scenes_app = [
    ('PRD生成',    9, 10, 11, 12, 13),
    ('架构图生成', 16, 17, 18, 19, 20),
    ('代码生成',   23, 24, 25, 26, 27),
    ('测试脚本',   30, 31, 32, 33, 34),
]

records = []  # 统一记录
for r in range(3, ws1.max_row + 1):
    product = ws1.cell(row=r, column=2).value
    if not product: continue
    for scene, mcol, tcol, fcol, pcol, total_col in scenes_app:
        raw_model = ws1.cell(row=r, column=mcol).value
        model = normalize_model(raw_model)
        if not model: continue
        fee = ws1.cell(row=r, column=fcol).value or 0
        persons = ws1.cell(row=r, column=pcol).value or 0
        total = ws1.cell(row=r, column=total_col).value or 0
        try:
            fee = float(fee); persons = float(persons); total = float(total)
        except: pass
        records.append({'来源':'应用产品','产品线':product,'场景':scene,
                        '模型族':model,'原始模型':str(raw_model),
                        '人均月费用':fee,'使用人数':persons,'月总费用':total})

# 基础软件：2 场景，每模块3模型组合
scenes_bs = [
    ('基础软件开发', 1, 3, 5, 6, 7),   # 模块col, 模型col, 费用col, 人数col, 总费用col
    ('日志分析',     8, 10, 12, 13, 14),
]
for r in range(3, ws2.max_row + 1):
    for scene, mod_col, mcol, fcol, pcol, total_col in scenes_bs:
        module = ws2.cell(row=r, column=mod_col).value
        if not module: continue
        raw_model = ws2.cell(row=r, column=mcol).value
        if not raw_model: continue
        fee = ws2.cell(row=r, column=fcol).value or 0
        persons = ws2.cell(row=r, column=pcol).value or 0
        total = ws2.cell(row=r, column=total_col).value or 0
        try:
            fee = float(fee); persons = float(persons); total = float(total)
        except: pass
        # 三模型组合（DeepSeek-V4 / Qwen3-Plus / GLM-5），费用均分
        for sm in ['DeepSeek-V4', 'Qwen3-Plus', 'GLM-5']:
            records.append({'来源':'基础软件','产品线':f'基础软件-{module}','场景':scene,
                            '模型族':sm,'原始模型':str(raw_model),
                            '人均月费用':fee/3,'使用人数':persons,'月总费用':total/3})

# ============ 按模型族聚合月费用 ============
agg = defaultdict(lambda: {'月总费用':0,'记录数':0,'场景集':set(),'来源集':set()})
for rec in records:
    m = rec['模型族']
    agg[m]['月总费用'] += rec['月总费用']
    agg[m]['记录数'] += 1
    agg[m]['场景集'].add(rec['场景'])
    agg[m]['来源集'].add(rec['来源'])

print('='*100)
print('一、模型名清洗结果（按模型族聚合月费用）')
print('='*100)
print(f'{"模型族":<18}{"月费用(元)":>12}{"记录数":>8}{"来源":>14}  涉及场景')
print('-'*100)
total_month_fee = 0
for m in sorted(agg.keys(), key=lambda x: -agg[x]['月总费用']):
    d = agg[m]
    print(f'{m:<18}{d["月总费用"]:>12.0f}{d["记录数"]:>8}{",".join(sorted(d["来源集"])):>14}  {",".join(sorted(d["场景集"]))}')
    total_month_fee += d['月总费用']
print('-'*100)
print(f'{"合计":<18}{total_month_fee:>12.0f}')

# ============ 用市场单价反推 Token 量 ============
print()
print('='*100)
print('二、用市场真实单价反推 Token 量（费用÷加权单价=Token量）')
print('   加权单价 = (输入价×3 + 输出价×1) / 4，假设输入:输出=3:1')
print('='*100)
print(f'{"模型族":<16}{"月费用(元)":>10}{"加权单价(元/百万)":>18}{"月Token(百万)":>16}{"月Token(万)":>14}{"年Token(万)":>14}{"波动1.15(万)":>16}')
print('-'*100)
grand_total_year_token = 0
grand_total_year_fee = 0
result_rows = []
for m in sorted(agg.keys(), key=lambda x: -agg[x]['月总费用']):
    d = agg[m]
    wp = weighted_price(m)
    month_fee = d['月总费用']
    if wp:
        month_token_M = month_fee / wp  # 百万Token
        month_token_wan = month_token_M * 100  # 万Token
        year_token_wan = month_token_wan * 12
        year_token_buf = year_token_wan * 1.15
        year_fee = month_fee * 12
        print(f'{m:<16}{month_fee:>10.0f}{wp:>18.2f}{month_token_M:>16.2f}{month_token_wan:>14.0f}{year_token_wan:>14.0f}{year_token_buf:>16.0f}')
        grand_total_year_token += year_token_buf
        grand_total_year_fee += year_fee
        result_rows.append((m, month_fee, wp, month_token_M, month_token_wan, year_token_wan, year_token_buf, year_fee))
    else:
        print(f'{m:<16}{month_fee:>10.0f}{"N/A":>18}{"N/A":>16}{"N/A":>14}{"N/A":>14}{"N/A":>16}')
print('-'*100)
print(f'{"合计":<16}{total_month_fee:>10.0f}{"":>18}{"":>16}{"":>14}{"":>14}{grand_total_year_token:>16.0f}')
print(f'\n年费用合计（不含波动）: {grand_total_year_fee:.0f} 元 = {grand_total_year_fee/10000:.1f} 万元')

# ============ 资源包规格建议 ============
print()
print('='*100)
print('三、资源包规格建议（按厂商标准包规取整）')
print('='*100)
print(f'{"模型族":<16}{"年预算(万元)":>14}{"建议资源包规格":>20}{"规格说明":<30}')
print('-'*100)
spec_map = {
    'DeepSeek-V4': (170, '10亿Token包', 'DeepSeek官方/阿里云代理'),
    'Qwen3-Plus':  (50,  '3亿Token包',  '阿里云 qwen3.7-plus'),
    'Qwen3-Max':   (40,  '2亿Token包',  '阿里云 qwen3.7-max'),
    'GLM-5':       (82,  '5亿Token包',  '智谱官方'),
    'Claude-Code': (5,   '订阅制',       'Anthropic 订阅'),
    'Codex':       (4,   '订阅制',       'GitHub Copilot 订阅'),
    'Gemini':      (1,   '按量付费',     'Google Cloud'),
    'Doubao-Seed-Code': (1, '按量付费',  '火山引擎'),
    'Kimi':        (2,   '按量付费',     '月之暗面'),
    'MiniMax':     (1,   '按量付费',     'MiniMax'),
    'Qoder':       (1,   '按量付费',     '阿里云'),
}
for m in sorted(agg.keys(), key=lambda x: -agg[x]['月总费用']):
    d = agg[m]
    year_fee = d['月总费用'] * 12 * 1.15 / 10000  # 万元
    if m in spec_map:
        budget, spec, note = spec_map[m]
        print(f'{m:<16}{budget:>14}{spec:>20}  {note}')
    else:
        print(f'{m:<16}{year_fee:>14.1f}{"按量付费":>20}')


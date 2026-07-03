"""
=====================================================================
权威计算脚本 — Token 资源包预算测算（V2.1 官方刊例价版）
=====================================================================
本脚本是预算测算的唯一数据来源，文档/消息中的所有数字必须来自本脚本输出。
禁止手动计算，禁止引用其他脚本的输出。

核心逻辑链（用户确认版）：
  1. 调研表费用数据自洽可信（62条记录0偏差）→ 作为预算基准
  2. 用 DeepSeek 官方刊例价反推 Token 量（汇报口径）
  3. 年预算 = 月费用 × 12 × 1.15（真实支出）
  4. 采购建议：按金额签框架协议（不按Token量签）

单价来源：DeepSeek 官方 https://api-docs.deepseek.com/zh-cn/quick_start/pricing
  - deepseek-v4-flash: 输入(缓存命中)0.02 / 输入(缓存未命中)1 / 输出2  元/百万Token
  - deepseek-v4-pro:   输入(缓存命中)0.025 / 输入(缓存未命中)3 / 输出6 元/百万Token
  - GLM-5.2: 假设与 DeepSeek-V4-Pro 同档（待智谱报价确认）
  - Codex/Gemini: 按 Pro 档 ×1.2 折算（订阅制/国际模型溢价）
  - Doubao-Seed-Code: 按 Flash 档（同类均衡型）

单位定义（已验证，避免混淆）：
  - 1 百万 = 1,000,000 个 Token
  - 1 亿 = 100,000,000 个 Token = 100 百万
  - 费用 ÷ 单价(元/百万) = 百万 Token
  - 百万 Token ÷ 100 = 亿 Token
=====================================================================
"""
import openpyxl
from collections import defaultdict

# ============ 配置区 ============
XLSX_PATH = '敏捷软件开发AI应用需求情况统计.xlsx'
PERSONS = 389  # 一汽（北京）软件科技有限公司人数（含7月入职11人，不含长春）
WAVE_FACTOR = 1.15  # 波动系数
CACHE_HIT_RATE = 0.5  # 缓存命中率假设
INPUT_OUTPUT_RATIO = (3, 1)  # 输入:输出 = 3:1

# 单位换算常量（已验证：1 亿 = 100 百万）
MILLION_TO_YI = 100

# ============ 官方刊例价（元/百万Token）============
# 格式: (输入缓存命中, 输入缓存未命中, 输出)
OFFICIAL_PRICES = {
    'DeepSeek-V4':         (0.025, 3, 6),       # deepseek-v4-pro 官方价
    'DeepSeek-V4-Flash':   (0.02, 1, 2),        # deepseek-v4-flash 官方价
    'GLM-5.2':             (0.025, 3, 6),       # 假设与Pro同档，待智谱报价确认
    'Codex':               (0.025*1.2, 3*1.2, 6*1.2),  # 订阅制折算溢价1.2倍
    'Doubao-Seed-Code':    (0.02, 1, 2),        # 按Flash同档
    'Gemini':              (0.025*1.2, 3*1.2, 6*1.2),  # 国际模型溢价1.2倍
}

def weighted_price(input_hit, input_miss, output, hit_rate=CACHE_HIT_RATE, ratio=INPUT_OUTPUT_RATIO):
    """
    计算加权单价（元/百万Token）
    假设输入:输出 = ratio[0]:ratio[1]，缓存命中率 = hit_rate
    """
    input_weighted = input_hit * hit_rate + input_miss * (1 - hit_rate)
    total_ratio = ratio[0] + ratio[1]
    return (input_weighted * ratio[0] + output * ratio[1]) / total_ratio

# 预计算各模型加权单价
WEIGHTED_PRICES = {m: weighted_price(*p) for m, p in OFFICIAL_PRICES.items()}

# ============ 模型名归一化 ============
def normalize_model(raw):
    """将调研表中的模型名归一化到采购模型族"""
    if not raw or raw in ('无', '-', '—', 'None'):
        return None
    s = str(raw).lower().replace(' ', '').replace('\n', '').replace('_', '').replace('，', '')
    if 'deepseek' in s:
        return 'DeepSeek-V4'
    if 'qwen' in s or '千问' in s:
        return 'DeepSeek-V4-Flash'  # Qwen3-Plus 折算到 Flash
    if 'glm' in s or 'gml' in s:
        return 'GLM-5.2'
    if 'doubao' in s or 'duubao' in s:
        return 'Doubao-Seed-Code'
    if 'gemini' in s:
        return 'Gemini'
    if 'codex' in s:
        return 'Codex'
    return None

# ============ 解析调研表 ============
def parse_survey():
    """解析调研表，返回按模型族聚合的月费用"""
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws1 = wb['应用产品']
    ws2 = wb['基础软件']
    
    agg = defaultdict(lambda: {'月总费用': 0, '记录数': 0, '场景集': set()})
    scene_agg = defaultdict(lambda: {'fee': 0, 'persons': 0})
    
    # 应用产品：4场景 (场景, 模型col, token col, 费用 col, 人数 col, 总费用 col)
    scenes_app = [
        ('PRD生成',    9, 10, 11, 12, 13),
        ('架构图生成', 16, 17, 18, 19, 20),
        ('代码生成',   23, 24, 25, 26, 27),
        ('测试脚本',   30, 31, 32, 33, 34),
    ]
    
    for r in range(3, ws1.max_row + 1):
        product = ws1.cell(row=r, column=2).value
        if not product:
            continue
        for scene, mcol, tcol, fcol, pcol, total_col in scenes_app:
            raw = ws1.cell(row=r, column=mcol).value
            model = normalize_model(raw)
            if not model:
                continue
            total = float(ws1.cell(row=r, column=total_col).value or 0)
            persons = float(ws1.cell(row=r, column=pcol).value or 0)
            agg[model]['月总费用'] += total
            agg[model]['记录数'] += 1
            agg[model]['场景集'].add(scene)
            scene_agg[scene]['fee'] += total
            scene_agg[scene]['persons'] += persons
    
    # 基础软件：2场景，每模块3模型组合，费用均分
    for r in range(3, ws2.max_row + 1):
        module = ws2.cell(row=r, column=1).value
        if not module:
            continue
        fee_dev = float(ws2.cell(row=r, column=7).value or 0)
        persons_dev = float(ws2.cell(row=r, column=6).value or 0)
        fee_log = float(ws2.cell(row=r, column=14).value or 0)
        persons_log = float(ws2.cell(row=r, column=13).value or 0)
        for sm in ['DeepSeek-V4', 'DeepSeek-V4-Flash', 'GLM-5.2']:
            agg[sm]['月总费用'] += fee_dev / 3 + fee_log / 3
            agg[sm]['记录数'] += 2
            agg[sm]['场景集'].add('基础软件开发')
            agg[sm]['场景集'].add('日志分析')
        scene_agg['基础软件开发']['fee'] += fee_dev
        scene_agg['基础软件开发']['persons'] += persons_dev
        scene_agg['日志分析']['fee'] += fee_log
        scene_agg['日志分析']['persons'] += persons_log
    
    return agg, scene_agg

# ============ 主计算 ============
def main():
    print('=' * 100)
    print('Token 资源包预算测算 — 权威计算脚本 V2.1')
    print('=' * 100)
    print()
    
    # 1. 官方加权单价
    print('【1】DeepSeek 官方刊例价及加权单价')
    print(f'    假设：输入:输出 = {INPUT_OUTPUT_RATIO[0]}:{INPUT_OUTPUT_RATIO[1]}，缓存命中率 = {CACHE_HIT_RATE}')
    print(f'    {"模型族":<22}{"输入(命中)":>12}{"输入(未命中)":>14}{"输出":>8}{"加权单价":>12}')
    print('    ' + '-' * 68)
    for m, (ih, im, o) in OFFICIAL_PRICES.items():
        wp = WEIGHTED_PRICES[m]
        print(f'    {m:<22}{ih:>12.3f}{im:>14.2f}{o:>8.2f}{wp:>12.4f}')
    print(f'    单价单位：元/百万Token')
    print()
    
    # 2. 解析调研表
    agg, scene_agg = parse_survey()
    total_month_fee = sum(d['月总费用'] for d in agg.values())
    
    print('【2】调研表费用聚合（按模型族）')
    print(f'    {"模型族":<22}{"月费用(元)":>14}{"记录数":>8}  涉及场景')
    print('    ' + '-' * 80)
    for m in sorted(agg.keys(), key=lambda x: -agg[x]['月总费用']):
        d = agg[m]
        print(f'    {m:<22}{d["月总费用"]:>14.0f}{d["记录数"]:>8}  {",".join(sorted(d["场景集"]))}')
    print('    ' + '-' * 80)
    print(f'    {"合计":<22}{total_month_fee:>14.0f}')
    print()
    
    # 3. Token 量反推 + 年预算
    print('【3】Token 量反推与年度预算（核心结果）')
    print(f'    公式：月Token(百万) = 月费用 / 加权单价')
    print(f'          年Token(亿) = 月Token(百万) × 12 ÷ {MILLION_TO_YI}')
    print(f'          年预算(万) = 月费用 × 12 × {WAVE_FACTOR} ÷ 10000')
    print()
    print(f'    {"模型族":<22}{"月费用":>10}{"加权单价":>10}{"月Token(百万)":>16}{"月Token(亿)":>14}{"年Token(亿)":>14}{"波动后(亿)":>14}{"年预算(万)":>12}')
    print('    ' + '-' * 112)
    
    total_year_token_yi = 0
    total_year_fee_wan = 0
    results = []
    
    for m in sorted(agg.keys(), key=lambda x: -agg[x]['月总费用']):
        d = agg[m]
        fee = d['月总费用']
        wp = WEIGHTED_PRICES[m]
        mt_M = fee / wp  # 百万
        mt_yi = mt_M / MILLION_TO_YI  # 亿（100百万=1亿）
        yt_yi = mt_yi * 12
        yt_buf = yt_yi * WAVE_FACTOR
        yf_wan = fee * 12 * WAVE_FACTOR / 10000
        print(f'    {m:<22}{fee:>10.0f}{wp:>10.4f}{mt_M:>16.0f}{mt_yi:>14.2f}{yt_yi:>14.2f}{yt_buf:>14.2f}{yf_wan:>12.1f}')
        total_year_token_yi += yt_buf
        total_year_fee_wan += yf_wan
        results.append({
            'model': m, 'month_fee': fee, 'wp': wp,
            'month_token_M': mt_M, 'month_token_yi': mt_yi,
            'year_token_yi': yt_yi, 'year_token_buf_yi': yt_buf,
            'year_fee_wan': yf_wan,
        })
    
    print('    ' + '-' * 112)
    print(f'    {"合计":<22}{total_month_fee:>10.0f}{"":>10}{"":>16}{"":>14}{"":>14}{total_year_token_yi:>14.2f}{total_year_fee_wan:>12.1f}')
    print()
    
    # 4. 人均口径
    print('【4】人均口径（按 {} 人）'.format(PERSONS))
    month_fee_per = total_month_fee / PERSONS
    month_token_per_M = sum(r['month_token_M'] for r in results) / PERSONS
    month_token_per_yi = month_token_per_M / MILLION_TO_YI
    year_token_per_yi = total_year_token_yi / PERSONS
    year_fee_per = total_year_fee_wan * 10000 / PERSONS
    
    print(f'    人均月费用: {month_fee_per:.0f} 元/人/月')
    print(f'    人均月Token: {month_token_per_M:.0f} 百万/人/月 = {month_token_per_yi:.2f} 亿/人/月')
    print(f'    人均年Token: {year_token_per_yi:.2f} 亿/人/年')
    print(f'    人均年预算: {year_fee_per:.0f} 元/人/年')
    print(f'    全公司年Token: {total_year_token_yi:.0f} 亿')
    print(f'    全公司年预算: {total_year_fee_wan:.1f} 万元')
    print()
    
    # 5. 场景维度
    print('【5】按场景维度')
    print(f'    {"场景":<16}{"月费用(元)":>14}{"使用人数":>10}{"人均月费":>10}{"占比":>8}')
    print('    ' + '-' * 60)
    for s in sorted(scene_agg.keys(), key=lambda x: -scene_agg[x]['fee']):
        d = scene_agg[s]
        pct = d['fee'] / total_month_fee * 100 if total_month_fee else 0
        pc = d['fee'] / d['persons'] if d['persons'] > 0 else 0
        print(f'    {s:<16}{d["fee"]:>14.0f}{d["persons"]:>10.0f}{pc:>10.0f}{pct:>7.1f}%')
    print()
    
    # 6. 采购方式建议
    print('【6】采购方式建议')
    print('    建议按金额签框架协议，不按Token量签，理由：')
    print('    1. 主力模型价格浮动，随新模型推出会变化')
    print('    2. 新模型我们肯定要用，但价格未知')
    print('    3. 各家Token计价方式不一，且资源包有折扣，按Token量签不可控')
    print()
    
    # 7. 汇报口径数据（供消息/文档直接引用，勿手动修改）
    print('=' * 100)
    print('【汇报口径数据】（供消息/文档直接引用，勿手动修改）')
    print('=' * 100)
    print(f'  调研月费用: {total_month_fee:,.0f} 元（覆盖290人）')
    print(f'  全公司人数: {PERSONS} 人（目前389人，7月入职11人）')
    print(f'  人均月费用: {month_fee_per:.0f} 元/人/月')
    print(f'  波动系数: {WAVE_FACTOR}')
    print(f'  年预算: {total_year_fee_wan:.1f} 万元')
    print(f'  人均月Token: {month_token_per_M:.0f} 百万 = {month_token_per_yi:.2f} 亿/人/月')
    print(f'  全公司年Token: {total_year_token_yi:.0f} 亿')
    print()
    
    # 8. DeepSeek 供应商集中度
    deepseek_fee = agg['DeepSeek-V4']['月总费用'] + agg['DeepSeek-V4-Flash']['月总费用']
    deepseek_pct = deepseek_fee / total_month_fee * 100
    glm_pct = agg['GLM-5.2']['月总费用'] / total_month_fee * 100
    print(f'  DeepSeek占比: {deepseek_pct:.1f}%（V4旗舰档 + Flash轻量档）')
    print(f'  智谱GLM-5.2占比: {glm_pct:.1f}%')
    print()

if __name__ == '__main__':
    main()

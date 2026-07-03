"""
按调研表原始填报的 Token 量计算预算（对比版）
"""
import openpyxl
from collections import defaultdict

wb = openpyxl.load_workbook('敏捷软件开发AI应用需求情况统计.xlsx', data_only=True)
ws1 = wb['应用产品']; ws2 = wb['基础软件']

# 市场加权单价（元/百万Token）
MARKET_WP = {
    'DeepSeek-V4': 18.00,
    'Qwen3-Plus': 4.20,
    'GLM-5.2': 18.00,
    'Codex': 37.80,
    'Doubao-Seed-Code': 4.20,
    'Gemini': 21.60,
}

def norm(raw):
    if not raw or raw in ('无','-','—','None'): return None
    s=str(raw).lower().replace(' ','').replace('\n','').replace('_','').replace('，','')
    if 'deepseek' in s: return 'DeepSeek-V4'
    if 'qwen' in s or '千问' in s: return 'Qwen3-Plus'
    if 'glm' in s or 'gml' in s: return 'GLM-5.2'
    if 'doubao' in s or 'duubao' in s: return 'Doubao-Seed-Code'
    if 'gemini' in s: return 'Gemini'
    if 'codex' in s: return 'Codex'
    return None

# 应用产品 4 场景
scenes_app = [('PRD生成',9,10,11,12,13),('架构图生成',16,17,18,19,20),('代码生成',23,24,25,26,27),('测试脚本',30,31,32,33,34)]
# 字段：模型col, token col, 费用 col, 人数 col, 总费用 col

agg = defaultdict(lambda: {'token_M_人均月':0,'月总费用':0,'记录数':0,'token_M_月':0})

print('='*100)
print('一、应用产品：按填报 Token × 市场单价 推算预算')
print('   逻辑：月Token(人均) × 使用人数 = 月Token总量 → × 市场单价 = 月费用 → ×12×1.15 = 年预算')
print('='*100)
print(f'{"模型族":<16}{"月Token(人均)":>14}{"×人数":>8}{"=月Token(M)":>14}{"×单价":>10}{"=月费用(元)":>14}{"年预算(万)":>12}')
print('-'*100)

for r in range(3, ws1.max_row+1):
    p = ws1.cell(row=r,column=2).value
    if not p: continue
    for scene, mcol, tcol, fcol, pcol, total_col in scenes_app:
        raw = ws1.cell(row=r, column=mcol).value
        model = norm(raw)
        if not model: continue
        token = ws1.cell(row=r, column=tcol).value or 0
        persons = ws1.cell(row=r, column=pcol).value or 0
        try: token=float(token); persons=float(persons)
        except: pass
        # token 单位是 M/人/月
        month_token_M = token * persons  # 总月Token（百万）
        wp = MARKET_WP[model]
        month_fee_by_token = month_token_M * wp  # 元
        agg[model]['token_M_人均月'] += token
        agg[model]['月总费用'] += month_fee_by_token
        agg[model]['token_M_月'] += month_token_M
        agg[model]['记录数'] += 1

# 基础软件：每模块三模型组合，token 是组合总量，均分到三模型
for r in range(3, ws2.max_row+1):
    m = ws2.cell(row=r,column=1).value
    if not m: continue
    # 基础软件开发
    token_dev = ws2.cell(row=r, column=4).value or 0
    persons_dev = ws2.cell(row=r, column=6).value or 0
    # 日志分析
    token_log = ws2.cell(row=r, column=11).value or 0
    persons_log = ws2.cell(row=r, column=13).value or 0
    try:
        token_dev=float(token_dev); persons_dev=float(persons_dev)
        token_log=float(token_log); persons_log=float(persons_log)
    except: pass
    # 三模型均分
    for sm in ['DeepSeek-V4','Qwen3-Plus','GLM-5.2']:
        wp = MARKET_WP[sm]
        # 基础软件开发
        mt_dev = token_dev * persons_dev / 3
        mf_dev = mt_dev * wp
        # 日志分析
        mt_log = token_log * persons_log / 3
        mf_log = mt_log * wp
        agg[sm]['token_M_月'] += mt_dev + mt_log
        agg[sm]['月总费用'] += mf_dev + mf_log
        agg[sm]['记录数'] += 2

app_total_token_fee = 0
app_total_token_M = 0
for m in sorted(agg.keys(), key=lambda x:-agg[x]['月总费用']):
    d = agg[m]
    year_budget = d['月总费用'] * 12 * 1.15 / 10000
    print(f'{m:<16}{d["token_M_人均月"]:>14.0f}{d["记录数"]:>8}{d["token_M_月"]:>14.0f}{MARKET_WP[m]:>10.2f}{d["月总费用"]:>14.0f}{year_budget:>12.1f}')
    app_total_token_fee += d['月总费用']
    app_total_token_M += d['token_M_月']

print('-'*100)
year_total = app_total_token_fee * 12 * 1.15 / 10000
print(f'{"合计":<16}{"":>14}{"":>8}{app_total_token_M:>14.0f}{"":>10}{app_total_token_fee:>14.0f}{year_total:>12.1f}')

print()
print('='*100)
print('二、两种测算方式对比')
print('='*100)
# 费用主线（之前算的）
fee_line = {
    'DeepSeek-V4': 169.1,
    'Qwen3-Plus': 89.8,
    'GLM-5.2': 81.8,
    'Codex': 4.1,
    'Doubao-Seed-Code': 0.7,
    'Gemini': 0.5,
}
fee_total = sum(fee_line.values())

print(f'{"模型族":<16}{"费用主线年预算(万)":>20}{"Token主线年预算(万)":>22}{"倍数":>10}{"差异说明":<30}')
print('-'*100)
token_total = 0
for m in sorted(agg.keys(), key=lambda x:-agg[x]['月总费用']):
    d = agg[m]
    token_year = d['月总费用'] * 12 * 1.15 / 10000
    token_total += token_year
    fee_year = fee_line.get(m, 0)
    ratio = token_year / fee_year if fee_year > 0 else 0
    diff = "Token填报虚高" if token_year > fee_year else "基本一致"
    print(f'{m:<16}{fee_year:>20.1f}{token_year:>22.1f}{ratio:>10.1f}x  {diff}')
print('-'*100)
ratio_total = token_total / fee_total
print(f'{"合计":<16}{fee_total:>20.1f}{token_total:>22.1f}{ratio_total:>10.1f}x')
print()
print(f'费用主线总预算：{fee_total:.1f} 万元')
print(f'Token主线总预算：{token_total:.1f} 万元')
print(f'差额：{token_total - fee_total:.1f} 万元（Token 主线高出 {(ratio_total-1)*100:.0f}%）')

print()
print('='*100)
print('三、反推单价对比（解释为什么 Token 主线预算爆炸）')
print('='*100)
print(f'{"模型族":<16}{"市场加权单价":>14}{"Token主线反推单价":>20}{"虚高倍数":>10}')
print('-'*60)
# 调研表原始费用
orig_fee = {
    'DeepSeek-V4': 122567,
    'Qwen3-Plus': 65067,
    'GLM-5.2': 59267,
    'Codex': 2940,
    'Doubao-Seed-Code': 520,
    'Gemini': 360,
}
for m in sorted(agg.keys(), key=lambda x:-agg[x]['月总费用']):
    d = agg[m]
    market_wp = MARKET_WP[m]
    # 反推单价 = 调研原始费用 / Token总量
    if d['token_M_月'] > 0:
        reverse_wp = orig_fee[m] / d['token_M_月']
        ratio = market_wp / reverse_wp if reverse_wp > 0 else 0
        print(f'{m:<16}{market_wp:>14.2f}{reverse_wp:>20.4f}{ratio:>10.0f}x')

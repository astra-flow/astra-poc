"""
AI 应用使用情况调研数据清洗与聚合
目标：把混乱的模型名称归一化，按模型聚合 Token 消耗与费用，推算年度采购量
"""
import openpyxl
import re
from collections import defaultdict

wb = openpyxl.load_workbook('敏捷软件开发AI应用需求情况统计.xlsx', data_only=True)

# ============ 1. 模型名称归一化映射 ============
# 调研表里模型名极混乱，这里统一映射到采购资源包的"模型族"
def normalize_model(raw):
    if not raw or raw in ('无', '-', '—'):
        return None
    s = str(raw).lower().replace(' ', '').replace('\n', '').replace('_', '')
    # 拼写纠错 + 归一化
    if 'deepseek' in s or 'deepseekv4' in s:
        return 'DeepSeek-V4'
    if 'doubao' in s or 'duubao' in s:  # Duubao 是拼写错误
        return 'Doubao-Seed-Code'
    if 'qwen' in s or '千问' in s:
        return 'Qwen3'
    if 'glm' in s or 'gml' in s:  # GML 是 GLM 拼写错误
        return 'GLM-5'
    if 'gemini' in s:
        return 'Gemini'
    if 'chatgpt' in s or 'gpt' in s:
        return 'ChatGPT'
    if 'codex' in s:  # OpenAI Codex
        return 'Codex'
    if 'claue' in s or 'claude' in s:
        return 'Claude-Code'
    if 'kimi' in s:
        return 'Kimi'
    if 'minmax' in s or 'minimax' in s:
        return 'MiniMax'
    if 'qoder' in s:
        return 'Qoder'
    return f'其他({raw})'

# ============ 2. 解析应用产品 Sheet ============
ws1 = wb['应用产品']
# 模型使用记录：按 (模型族, 场景) 聚合
# 字段：token(M/月,人均)、费用(元/月,人均)、人数、月总费用
app_records = []  # list of dict
scenes_app = [
    ('PRD生成',  9, 10, 11, 12, 13),   # 模型col, token col, 费用 col, 人数 col, 总费用 col
    ('架构图生成', 16, 17, 18, 19, 20),
    ('代码生成',  23, 24, 25, 26, 27),
    ('测试脚本',  30, 31, 32, 33, 34),
]
for r in range(3, ws1.max_row + 1):
    product = ws1.cell(row=r, column=2).value
    if not product:
        continue
    for scene, mcol, tcol, fcol, pcol, total_col in scenes_app:
        raw_model = ws1.cell(row=r, column=mcol).value
        model = normalize_model(raw_model)
        if not model:
            continue
        token = ws1.cell(row=r, column=tcol).value or 0
        fee = ws1.cell(row=r, column=fcol).value or 0
        persons = ws1.cell(row=r, column=pcol).value or 0
        total = ws1.cell(row=r, column=total_col).value or 0
        # 处理多人多模型组合（如 "deepseekv4\nQwen" 拆成两家均摊）
        # 简化：若原始是组合，按模型族分别记录，token/费用按人数等分
        raw_str = str(raw_model)
        if '\n' in raw_str or ('，' in raw_str) or ('.' in raw_str and raw_str.count('\n')>0):
            # 组合模型，已在 normalize 中归一，这里按主模型记录（保守）
            pass
        try:
            token = float(token); fee = float(fee); persons = float(persons); total = float(total)
        except:
            pass
        app_records.append({
            'sheet': '应用产品', '产品线': product, '场景': scene,
            '模型族': model, '原始模型': raw_str,
            'token_M_人均月': token, '费用_人均月': fee,
            '使用人数': persons, '月总费用': total,
        })

# ============ 3. 解析基础软件 Sheet ============
ws2 = wb['基础软件']
# 基础软件开发：A-G 列；日志分析：H-N 列
# 注意：每个模块的模型是 "deepseek v4 pro\nQwen3.7 Max\nGLM5.x" 三家组合
# 调研表给出的是组合后总 token/费用，需要拆分到三个模型族
bs_records = []
scenes_bs = [
    ('基础软件开发', 1, 2, 3, 4, 5, 6, 7),   # 模块col, 是否AI, 模型, token, 费用, 人数, 总费用
    ('日志分析',     8, 9, 10, 11, 12, 13, 14),
]
for r in range(3, ws2.max_row + 1):
    for scene, mod_col, ai_col, mcol, tcol, fcol, pcol, total_col in scenes_bs:
        module = ws2.cell(row=r, column=mod_col).value
        if not module:
            continue
        raw_model = ws2.cell(row=r, column=mcol).value
        if not raw_model:
            continue
        token = ws2.cell(row=r, column=tcol).value or 0
        fee = ws2.cell(row=r, column=fcol).value or 0
        persons = ws2.cell(row=r, column=pcol).value or 0
        total = ws2.cell(row=r, column=total_col).value or 0
        # 三模型组合，均分 token 与费用
        # 拆成 DeepSeek-V4 / Qwen3 / GLM-5 各 1/3
        sub_models = ['DeepSeek-V4', 'Qwen3', 'GLM-5']
        for sm in sub_models:
            bs_records.append({
                'sheet': '基础软件', '产品线': f'基础软件-{module}', '场景': scene,
                '模型族': sm, '原始模型': raw_model,
                'token_M_人均月': float(token)/3 if token else 0,
                '费用_人均月': float(fee)/3 if fee else 0,
                '使用人数': float(persons) if persons else 0,
                '月总费用': float(total)/3 if total else 0,
            })

# ============ 4. 按模型族聚合 ============
all_records = app_records + bs_records
agg = defaultdict(lambda: {'token_M_月': 0, '月总费用': 0, '记录数': 0, '场景集': set()})
for rec in all_records:
    m = rec['模型族']
    # token_M_月 = 人均月token × 人数
    t = rec['token_M_人均月'] * rec['使用人数']
    agg[m]['token_M_月'] += t
    agg[m]['月总费用'] += rec['月总费用']
    agg[m]['记录数'] += 1
    agg[m]['场景集'].add(rec['场景'])

print('='*80)
print('按模型族聚合（月度）')
print('='*80)
print(f'{"模型族":<18}{"月Token(M)":>14}{"月费用(元)":>14}{"记录数":>8}{"涉及场景":<30}')
print('-'*80)
total_token = 0; total_fee = 0
for m in sorted(agg.keys(), key=lambda x: -agg[x]['月总费用']):
    d = agg[m]
    print(f'{m:<18}{d["token_M_月"]:>14.0f}{d["月总费用"]:>14.0f}{d["记录数"]:>8}  {",".join(sorted(d["场景集"]))[:28]}')
    total_token += d['token_M_月']; total_fee += d['月总费用']
print('-'*80)
print(f'{"合计":<18}{total_token:>14.0f}{total_fee:>14.0f}')

# ============ 5. 推算年度采购量 ============
print()
print('='*80)
print('年度采购量推算（按模型族）')
print('='*80)
# 公式：年采购量 = 月Token × 12 × 波动系数(1.3)  (单位：万Token)
# 月费用校验：年费用 ≈ 月费用 × 12（用于交叉验证资源包预算合理性）
print(f'{"模型族":<18}{"月Token(M)":>12}{"年Token(万)":>14}{"波动1.3后(万)":>16}{"现月费用":>10}{"现年费用":>10}')
print('-'*80)
for m in sorted(agg.keys(), key=lambda x: -agg[x]['月总费用']):
    d = agg[m]
    month_token_M = d['token_M_月']  # M = 百万
    year_token_wan = month_token_M * 12 * 100  # M→万: ×100
    year_token_wan_buf = year_token_wan * 1.3
    month_fee = d['月总费用']
    year_fee = month_fee * 12
    print(f'{m:<18}{month_token_M:>12.0f}{year_token_wan:>14.0f}{year_token_wan_buf:>16.0f}{month_fee:>10.0f}{year_fee:>10.0f}')

# ============ 6. 场景维度交叉 ============
print()
print('='*80)
print('按场景聚合（月度）')
print('='*80)
scene_agg = defaultdict(lambda: {'token_M_月': 0, '月总费用': 0, '模型集': set()})
for rec in all_records:
    s = rec['场景']
    t = rec['token_M_人均月'] * rec['使用人数']
    scene_agg[s]['token_M_月'] += t
    scene_agg[s]['月总费用'] += rec['月总费用']
    scene_agg[s]['模型集'].add(rec['模型族'])
print(f'{"场景":<16}{"月Token(M)":>14}{"月费用(元)":>14}{"占比":>8}  涉及模型')
print('-'*80)
for s in sorted(scene_agg.keys(), key=lambda x: -scene_agg[x]['月总费用']):
    d = scene_agg[s]
    pct = d['月总费用']/total_fee*100 if total_fee else 0
    print(f'{s:<16}{d["token_M_月"]:>14.0f}{d["月总费用"]:>14.0f}{pct:>7.1f}%  {",".join(sorted(d["模型集"]))}')

print()
print('='*80)
print('数据质量观察')
print('='*80)
print(f'应用产品记录数: {len(app_records)}')
print(f'基础软件记录数: {len(bs_records)} (原始21模块×2场景×3模型拆分)')
print(f'模型族数量: {len(agg)}')

print()
print('='*80)
print('费用自洽性校验：月总费用 vs 人均费用×人数')
print('='*80)
# 应用产品：列结构 (场景, 模型col, token col, 费用 col, 人数 col, 总费用 col)
mismatch = []
for r in range(3, ws1.max_row + 1):
    product = ws1.cell(row=r, column=2).value
    if not product: continue
    for scene, mcol, tcol, fcol, pcol, total_col in scenes_app:
        fee = ws1.cell(row=r, column=fcol).value
        persons = ws1.cell(row=r, column=pcol).value
        total = ws1.cell(row=r, column=total_col).value
        if fee and persons and total:
            expected = fee * persons
            if abs(expected - total) > 1 and total > 0:
                mismatch.append((product, scene, fee, persons, expected, total))
print(f'应用产品不自洽行数: {len(mismatch)}')
for m in mismatch[:5]:
    print(f'  {m}')

print()
print('='*80)
print('反推模型族单价（元/万Token）= 月费用 / (月Token(M)×100)')
print('说明：M=百万，万Token=M×100')
print('='*80)
print(f'{"模型族":<18}{"月Token(M)":>12}{"月费用(元)":>12}{"反推单价(元/万Token)":>22}{"市场参考价":>16}')
print('-'*80)
# 市场参考价（2026年公开报价大致区间，用于校验反推单价合理性）
market_ref = {
    'DeepSeek-V4': '0.8-2',
    'Qwen3': '0.5-4',
    'GLM-5': '0.5-2',
    'Codex': '订阅制',
    'Doubao-Seed-Code': '0.3-1',
    'Gemini': '0.7-1.5',
}
for m in sorted(agg.keys(), key=lambda x: -agg[x]['月总费用']):
    d = agg[m]
    t_m = d['token_M_月']
    fee = d['月总费用']
    if t_m > 0:
        # 万Token = M × 100; 单价 = 费用 / (M×100)
        unit = fee / (t_m * 100)
        print(f'{m:<18}{t_m:>12.0f}{fee:>12.0f}{unit:>22.4f}{market_ref.get(m,"-"):>16}')
    else:
        print(f'{m:<18}{t_m:>12.0f}{fee:>12.0f}{"N/A":>22}{market_ref.get(m,"-"):>16}')

print()
print('='*80)
print('应用产品单独聚合（剔除基础软件的巨量干扰）')
print('='*80)
app_agg = defaultdict(lambda: {'token_M_月': 0, '月总费用': 0, '记录数': 0})
for rec in app_records:
    m = rec['模型族']
    t = rec['token_M_人均月'] * rec['使用人数']
    app_agg[m]['token_M_月'] += t
    app_agg[m]['月总费用'] += rec['月总费用']
    app_agg[m]['记录数'] += 1
print(f'{"模型族":<18}{"月Token(M)":>14}{"月费用(元)":>14}{"记录数":>8}')
print('-'*60)
app_total_t = 0; app_total_f = 0
for m in sorted(app_agg.keys(), key=lambda x: -app_agg[x]['月总费用']):
    d = app_agg[m]
    print(f'{m:<18}{d["token_M_月"]:>14.0f}{d["月总费用"]:>14.0f}{d["记录数"]:>8}')
    app_total_t += d['token_M_月']; app_total_f += d['月总费用']
print('-'*60)
print(f'{"应用产品合计":<18}{app_total_t:>14.0f}{app_total_f:>14.0f}')

print()
print('='*80)
print('基础软件单独聚合')
print('='*80)
bs_agg = defaultdict(lambda: {'token_M_月': 0, '月总费用': 0, '记录数': 0})
for rec in bs_records:
    m = rec['模型族']
    t = rec['token_M_人均月'] * rec['使用人数']
    bs_agg[m]['token_M_月'] += t
    bs_agg[m]['月总费用'] += rec['月总费用']
    bs_agg[m]['记录数'] += 1
print(f'{"模型族":<18}{"月Token(M)":>14}{"月费用(元)":>14}{"记录数":>8}')
print('-'*60)
for m in sorted(bs_agg.keys(), key=lambda x: -bs_agg[x]['月总费用']):
    d = bs_agg[m]
    print(f'{m:<18}{d["token_M_月"]:>14.0f}{d["月总费用"]:>14.0f}{d["记录数"]:>8}')

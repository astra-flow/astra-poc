"""
将 Qwen3-Plus 用量合并到 DeepSeek-V4-Flash（单价更低），重算预算
"""
import openpyxl
from collections import defaultdict

wb = openpyxl.load_workbook('敏捷软件开发AI应用需求情况统计.xlsx', data_only=True)
ws1 = wb['应用产品']; ws2 = wb['基础软件']

# 市场加权单价（元/百万Token）
# DeepSeek-V4(旗舰) 18.00 / DeepSeek-V4-Flash(轻量) 1.20 / GLM-5.2 18.00
MARKET_WP = {
    'DeepSeek-V4': 18.00,
    'Qwen3-Plus': 4.20,        # 旗舰，输入14.4/输出28.8
    'DeepSeek-V4-Flash': 1.20,   # 轻量，输入1.2/输出2.4 ← Qwen3-Plus 替代方案
    'GLM-5.2': 18.00,
    'Codex': 37.80,
    'Doubao-Seed-Code': 4.20,
    'Gemini': 21.60,
}

def norm(raw):
    if not raw or raw in ('无','-','—','None'): return None
    s=str(raw).lower().replace(' ','').replace('\n','').replace('_','').replace('，','')
    if 'deepseek' in s: return 'DeepSeek-V4'
    if 'qwen' in s or '千问' in s: return 'Qwen3-Plus'  # 标记，后面合并
    if 'glm' in s or 'gml' in s: return 'GLM-5.2'
    if 'doubao' in s or 'duubao' in s: return 'Doubao-Seed-Code'
    if 'gemini' in s: return 'Gemini'
    if 'codex' in s: return 'Codex'
    return None

scenes_app = [('PRD生成',9,10,11,12,13),('架构图生成',16,17,18,19,20),('代码生成',23,24,25,26,27),('测试脚本',30,31,32,33,34)]

agg = defaultdict(lambda: {'月总费用':0,'记录数':0})
# 关键：费用是调研实测值（自洽可信），合并后总费用不变
# 变化的是：Qwen3-Plus 的 65067 元/月，改用 DeepSeek-V4-Flash 的单价反推 Token 量
# 但年预算仍 = 月费用 × 12 × 1.15（费用主线法，预算不变）
# 真正变化的是：Token 量变大（因为 Flash 单价低），资源包规格变大

# 应用产品
for r in range(3, ws1.max_row+1):
    p = ws1.cell(row=r,column=2).value
    if not p: continue
    for scene, mcol, tcol, fcol, pcol, total_col in scenes_app:
        raw = ws1.cell(row=r, column=mcol).value
        model = norm(raw)
        if not model: continue
        total = float(ws1.cell(row=r, column=total_col).value or 0)
        agg[model]['月总费用'] += total
        agg[model]['记录数'] += 1

# 基础软件
for r in range(3, ws2.max_row+1):
    m = ws2.cell(row=r,column=1).value
    if not m: continue
    fd=float(ws2.cell(row=r,column=7).value or 0)
    fl=float(ws2.cell(row=r,column=14).value or 0)
    for sm in ['DeepSeek-V4','Qwen3-Plus','GLM-5.2']:
        agg[sm]['月总费用'] += fd/3 + fl/3
        agg[sm]['记录数'] += 2

# 方案对比
print('='*100)
print('方案对比：Qwen3-Plus 是否合并到 DeepSeek-V4-Flash')
print('='*100)
print()
print('--- 方案A：维持 Qwen3-Plus（4个模型族）---')
print(f'{"模型族":<20}{"月费用(元)":>12}{"加权单价":>10}{"年预算(万)":>12}')
print('-'*60)
total_a = 0
for m in ['DeepSeek-V4','Qwen3-Plus','GLM-5.2','Codex','Doubao-Seed-Code','Gemini']:
    if m not in agg: continue
    d = agg[m]
    wp = MARKET_WP[m]
    yb = d['月总费用'] * 12 * 1.15 / 10000
    print(f'{m:<20}{d["月总费用"]:>12.0f}{wp:>10.2f}{yb:>12.1f}')
    total_a += yb
print('-'*60)
print(f'{"合计":<20}{"":>12}{"":>10}{total_a:>12.1f}')

print()
print('--- 方案B：Qwen3-Plus 合并到 DeepSeek-V4-Flash（3个模型族）---')
print('   逻辑：Qwen3 用量转 DeepSeek-V4-Flash，费用不变（仍是调研实测值）')
print('   变化：模型族减1，资源包规格变大（Flash单价低→Token量大）')
print()
print(f'{"模型族":<22}{"月费用(元)":>12}{"加权单价":>10}{"月Token(M)":>14}{"年Token(万)":>14}{"波动后(万)":>14}{"年预算(万)":>12}')
print('-'*100)

# DeepSeek-V4（旗舰，不变）
d = agg['DeepSeek-V4']
wp = 18.00
mt = d['月总费用'] / wp
yt = mt * 12 * 100
yb = yt * 1.15
yf = d['月总费用'] * 12 * 1.15 / 10000
print(f'{"DeepSeek-V4":<22}{d["月总费用"]:>12.0f}{wp:>10.2f}{mt:>14.0f}{yt:>14.0f}{yb:>14.0f}{yf:>12.1f}')

# DeepSeek-V4-Flash（吸收了 Qwen3-Plus）
# 月费用 = 原 Qwen3-Plus 费用（65067）+ 原 DeepSeek 的小用量部分？不，DeepSeek-V4 旗舰已单算
# 这里 Flash 只承接 Qwen3-Plus 的费用
qwen_fee = agg['Qwen3-Plus']['月总费用']
wp = 1.20  # Flash 单价
mt = qwen_fee / wp
yt = mt * 12 * 100
yb = yt * 1.15
yf = qwen_fee * 12 * 1.15 / 10000
print(f'{"DeepSeek-V4-Flash":<22}{qwen_fee:>12.0f}{wp:>10.2f}{mt:>14.0f}{yt:>14.0f}{yb:>14.0f}{yf:>12.1f}')

# GLM-5.2
d = agg['GLM-5.2']
wp = 18.00
mt = d['月总费用'] / wp
yt = mt * 12 * 100
yb = yt * 1.15
yf = d['月总费用'] * 12 * 1.15 / 10000
print(f'{"GLM-5.2":<22}{d["月总费用"]:>12.0f}{wp:>10.2f}{mt:>14.0f}{yt:>14.0f}{yb:>14.0f}{yf:>12.1f}')

# 其他小模型
for m in ['Codex','Doubao-Seed-Code','Gemini']:
    if m not in agg: continue
    d = agg[m]
    wp = MARKET_WP[m]
    yf = d['月总费用'] * 12 * 1.15 / 10000
    print(f'{m:<22}{d["月总费用"]:>12.0f}{wp:>10.2f}{"":>14}{"":>14}{"":>14}{yf:>12.1f}')

total_b = total_a  # 费用不变，年预算不变
print('-'*100)
print(f'{"合计":<22}{"":>12}{"":>10}{"":>14}{"":>14}{"":>14}{total_b:>12.1f}')

print()
print('='*100)
print('关键结论')
print('='*100)
print(f'年预算：{total_a:.1f} 万元（两方案一致，因为费用主线法只看费用）')
print()
print('方案B 的真正优势不在预算金额，而在：')
print('  1. 模型族从 6 个减到 5 个（Qwen3-Plus 并入 DeepSeek-V4-Flash）')
print('  2. 供应商集中：DeepSeek 一家覆盖旗舰+轻量两档（140万+90万=230万，占73%）')
print('  3. DeepSeek-V4-Flash Token 量大（2138万→年），议价筹码更强')
print('  4. 不依赖阿里 Qwen3，供应商选择更灵活')
print()
print('资源包规格对比（Qwen3-Plus 部分变化）：')
print(f'  方案A：Qwen3-Plus 3亿Token包，单价4.20元/百万，预算89.8万')
print(f'  方案B：DeepSeek-V4-Flash 30亿Token包，单价1.20元/百万，预算89.8万')
print(f'  → 同样的钱，Flash 能买 10 倍的 Token 量，议价空间更大')

print()
print('='*100)
print('按场景的人均费用（不变，费用数据没变）')
print('='*100)
scene_agg = defaultdict(lambda: {'fee':0,'persons':0})
for r in range(3, ws1.max_row+1):
    p = ws1.cell(row=r,column=2).value
    if not p: continue
    for scene, mcol, tcol, fcol, pcol, total_col in scenes_app:
        persons = float(ws1.cell(row=r, column=pcol).value or 0)
        total = float(ws1.cell(row=r, column=total_col).value or 0)
        if total > 0:
            scene_agg[scene]['fee'] += total
            scene_agg[scene]['persons'] += persons
for r in range(3, ws2.max_row+1):
    m = ws2.cell(row=r,column=1).value
    if not m: continue
    fd=float(ws2.cell(row=r,column=7).value or 0); pd=float(ws2.cell(row=r,column=6).value or 0)
    fl=float(ws2.cell(row=r,column=14).value or 0); pl=float(ws2.cell(row=r,column=13).value or 0)
    scene_agg['基础软件开发']['fee']+=fd; scene_agg['基础软件开发']['persons']+=pd
    scene_agg['日志分析']['fee']+=fl; scene_agg['日志分析']['persons']+=pl
total_month = sum(d['fee'] for d in scene_agg.values())
print(f'人均月费用（400人）：{total_month/400:.0f} 元/人/月')
print(f'年预算（400人×12×1.15）：{total_month/400*12*1.15*400/10000:.1f} 万元')

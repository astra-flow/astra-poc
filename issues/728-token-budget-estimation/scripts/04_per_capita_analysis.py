"""
人均月费用测算
"""
import openpyxl
from collections import defaultdict

wb = openpyxl.load_workbook('敏捷软件开发AI应用需求情况统计.xlsx', data_only=True)
ws1 = wb['应用产品']
ws2 = wb['基础软件']

# 应用产品：4 场景 (场景, 模型col, 费用col, 人数col, 总费用col)
scenes_app = [
    ('PRD生成',    9, 11, 12, 13),
    ('架构图生成', 16, 18, 19, 20),
    ('代码生成',   23, 25, 26, 27),
    ('测试脚本',   30, 32, 33, 34),
]

# 统计：人均月费用 = 月总费用 / 使用人数
# 关键：同一个产品线可能多人多场景，需要算"人月"概念
print('='*90)
print('一、应用产品：各产品线人均月费用（按产品线汇总）')
print('='*90)
print(f'{"产品线":<14}{"月总费用(元)":>14}{"使用人数":>10}{"人均月费(元)":>14}{"涉及场景数":>12}')
print('-'*90)

app_total_fee = 0
app_total_persons_set = set()  # 用产品线+人数去重统计总人数
app_rows = []
for r in range(3, ws1.max_row + 1):
    product = ws1.cell(row=r, column=2).value
    if not product: continue
    line_fee = 0
    line_persons_max = 0  # 同一产品线不同场景的人数可能重叠，取最大值作为保守估计
    scene_count = 0
    for scene, mcol, fcol, pcol, total_col in scenes_app:
        persons = ws1.cell(row=r, column=pcol).value or 0
        total = ws1.cell(row=r, column=total_col).value or 0
        try:
            persons = float(persons); total = float(total)
        except: pass
        if total > 0:
            line_fee += total
            scene_count += 1
            if persons > line_persons_max:
                line_persons_max = persons
    if line_fee > 0:
        per_capita = line_fee / line_persons_max if line_persons_max > 0 else 0
        app_rows.append((product, line_fee, line_persons_max, per_capita, scene_count))
        app_total_fee += line_fee

app_rows.sort(key=lambda x: -x[3])
for product, fee, persons, pc, sc in app_rows:
    print(f'{product:<14}{fee:>14.0f}{persons:>10.0f}{pc:>14.0f}{sc:>12}')

app_persons_sum = sum(x[2] for x in app_rows)
print('-'*90)
print(f'{"应用产品合计":<14}{app_total_fee:>14.0f}{app_persons_sum:>10.0f}{app_total_fee/app_persons_sum:>14.0f}')
print(f'  注：使用人数为各产品线最大场景人数之和（保守估计，实际可能有重叠）')

# 基础软件
print()
print('='*90)
print('二、基础软件：各模块人均月费用')
print('='*90)
print(f'{"模块":<18}{"月总费用(元)":>14}{"使用人数":>10}{"人均月费(元)":>14}')
print('-'*90)
bs_total_fee = 0
bs_total_persons = 0
bs_rows = []
for r in range(3, ws2.max_row + 1):
    module = ws2.cell(row=r, column=1).value
    if not module: continue
    # 基础软件开发 + 日志分析 两场景费用合计
    fee_dev = ws2.cell(row=r, column=7).value or 0
    persons_dev = ws2.cell(row=r, column=6).value or 0
    fee_log = ws2.cell(row=r, column=14).value or 0
    persons_log = ws2.cell(row=r, column=13).value or 0
    try:
        fee_dev = float(fee_dev); persons_dev = float(persons_dev)
        fee_log = float(fee_log); persons_log = float(persons_log)
    except: pass
    total_fee = fee_dev + fee_log
    # 两场景同模块人数通常相同
    persons = max(persons_dev, persons_log)
    per_capita = total_fee / persons if persons > 0 else 0
    bs_rows.append((module, total_fee, persons, per_capita))
    bs_total_fee += total_fee
    bs_total_persons += persons

bs_rows.sort(key=lambda x: -x[3])
for module, fee, persons, pc in bs_rows:
    print(f'{module:<18}{fee:>14.0f}{persons:>10.0f}{pc:>14.0f}')
print('-'*90)
print(f'{"基础软件合计":<18}{bs_total_fee:>14.0f}{bs_total_persons:>10.0f}{bs_total_fee/bs_total_persons:>14.0f}')

# 汇总
print()
print('='*90)
print('三、整体人均月费用汇总')
print('='*90)
grand_fee = app_total_fee + bs_total_fee
grand_persons = app_persons_sum + bs_total_persons
print(f'应用产品：月总费用 {app_total_fee:.0f} 元，使用人数 {app_persons_sum:.0f} 人，人均 {app_total_fee/app_persons_sum:.0f} 元/月')
print(f'基础软件：月总费用 {bs_total_fee:.0f} 元，使用人数 {bs_total_persons:.0f} 人，人均 {bs_total_fee/bs_total_persons:.0f} 元/月')
print(f'整体合计：月总费用 {grand_fee:.0f} 元，使用人数 {grand_persons:.0f} 人，人均 {grand_fee/grand_persons:.0f} 元/月')
print()
print(f'按年化（×12）：人均年费用 {grand_fee/grand_persons*12:.0f} 元/年')
print(f'按年化+波动1.15：人均年费用 {grand_fee/grand_persons*12*1.15:.0f} 元/年')

# 场景维度人均
print()
print('='*90)
print('四、按场景维度看人均月费用')
print('='*90)
scene_agg = defaultdict(lambda: {'fee':0, 'persons':0})
for r in range(3, ws1.max_row + 1):
    product = ws1.cell(row=r, column=2).value
    if not product: continue
    for scene, mcol, fcol, pcol, total_col in scenes_app:
        persons = ws1.cell(row=r, column=pcol).value or 0
        total = ws1.cell(row=r, column=total_col).value or 0
        try:
            persons = float(persons); total = float(total)
        except: pass
        if total > 0:
            scene_agg[scene]['fee'] += total
            scene_agg[scene]['persons'] += persons

# 基础软件两场景
for r in range(3, ws2.max_row + 1):
    module = ws2.cell(row=r, column=1).value
    if not module: continue
    fee_dev = float(ws2.cell(row=r, column=7).value or 0)
    persons_dev = float(ws2.cell(row=r, column=6).value or 0)
    fee_log = float(ws2.cell(row=r, column=14).value or 0)
    persons_log = float(ws2.cell(row=r, column=13).value or 0)
    scene_agg['基础软件开发']['fee'] += fee_dev
    scene_agg['基础软件开发']['persons'] += persons_dev
    scene_agg['日志分析']['fee'] += fee_log
    scene_agg['日志分析']['persons'] += persons_log

print(f'{"场景":<16}{"月总费用(元)":>14}{"使用人数":>10}{"人均月费(元)":>14}')
print('-'*60)
for s in sorted(scene_agg.keys(), key=lambda x: -scene_agg[x]['fee']):
    d = scene_agg[s]
    pc = d['fee']/d['persons'] if d['persons']>0 else 0
    print(f'{s:<16}{d["fee"]:>14.0f}{d["persons"]:>10.0f}{pc:>14.0f}')

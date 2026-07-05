"""
=====================================================================
Token 资源包供应商比价表生成脚本
=====================================================================
数据来源：
  - 官方刊例价基准：data_provider.py（统一数据源）
  - 供应商报价：各供应商填写的报价模板Excel

使用方式：
  python3 scripts/01_vendor_comparison.py

输出：
  - 控制台打印比价摘要
  - 生成 output/供应商比价表.xlsx
=====================================================================
"""
import os
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# 添加 scripts 目录到 path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from data_provider import get_all_data, MODEL_MAP, load_prices

# ============ 配置区 ============
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# 报价文件路径（供应商填写的报价模板）
QUOTE_DIR = '/Users/suwei/Documents/一汽软件/研发效能/效能工具/企业级AI平台'
QUOTE_FILES = {
    '阿里': os.path.join(QUOTE_DIR, '一汽集团_Token资源包报价_V1.0-阿里.xlsx'),
    '火山': os.path.join(QUOTE_DIR, 'Token资源包报价模板-一汽集团-火山20260703.xlsx'),
    # '腾讯': os.path.join(QUOTE_DIR, 'Token资源包报价模板-发送版-腾讯.xlsx'),
}

# ============ 样式 ============
title_font = Font(name='微软雅黑', size=14, bold=True, color='FFFFFF')
title_fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
header_font = Font(name='微软雅黑', size=10, bold=True, color='FFFFFF')
header_fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')
best_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
warn_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
normal_fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')

thin_border = Border(
    left=Side(style='thin', color='999999'),
    right=Side(style='thin', color='999999'),
    top=Side(style='thin', color='999999'),
    bottom=Side(style='thin', color='999999')
)
center = Alignment(horizontal='center', vertical='center', wrap_text=True)
left = Alignment(horizontal='left', vertical='center', wrap_text=True)


def get_official_prices_map():
    """从 data_provider 获取官方刊例价基准"""
    prices = load_prices()
    # 统一模型名格式（去掉空格和括号，便于匹配）
    official = {}
    for model_key, price_key in MODEL_MAP.items():
        p = prices[price_key]
        # 用多种名称格式作为 key，便于匹配
        official[model_key] = {'hit': p['input_hit'], 'miss': p['input_miss'], 'out': p['output']}
        # 也用带空格的格式
        if 'Pro' in model_key:
            official[model_key.replace('-Pro', ' (Pro)')] = official[model_key]
        if 'Flash' in model_key:
            official[model_key.replace('-Flash', ' Flash')] = official[model_key]
        if 'GLM' in model_key:
            official[model_key.replace('-', ' ')] = official[model_key]
    return official


def parse_quote(filepath, vendor_name):
    """解析单个供应商的报价Excel"""
    if not os.path.exists(filepath):
        print(f'⚠ 文件不存在: {filepath}（{vendor_name}）')
        return None
    
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb['Token资源包报价']
    
    result = {
        'vendor': vendor_name,
        'models': [],
        'plans': [],
    }
    
    # 解析模型单价（第14行是表头，从第15行开始）
    for r in range(15, 25):
        model_name = ws.cell(row=r, column=2).value
        if not model_name:
            continue
        model = {
            'name': model_name,
            'tier': ws.cell(row=r, column=3).value or '',
            'input_hit': ws.cell(row=r, column=4).value,
            'input_miss': ws.cell(row=r, column=5).value,
            'output': ws.cell(row=r, column=6).value,
            'package_type': ws.cell(row=r, column=7).value or '',
            'package_spec': ws.cell(row=r, column=8).value or '',
            'package_price': ws.cell(row=r, column=9).value,
            'discount': ws.cell(row=r, column=10).value or '',
            'remark': ws.cell(row=r, column=11).value or '',
        }
        result['models'].append(model)
    
    # 解析年度总价方案（第24行是表头，从第25行开始）
    for r in range(25, 30):
        plan_name = ws.cell(row=r, column=2).value
        if not plan_name:
            continue
        plan = {
            'name': plan_name,
            'token_total': ws.cell(row=r, column=3).value,
            'annual_price': ws.cell(row=r, column=4).value,
            'framework': ws.cell(row=r, column=5).value or '',
            'validity': ws.cell(row=r, column=6).value or '',
            'rollover': ws.cell(row=r, column=7).value or '',
            'excess_rate': ws.cell(row=r, column=8).value,
            'remark': ws.cell(row=r, column=9).value or '',
            'scene': ws.cell(row=r, column=10).value or '',
        }
        result['plans'].append(plan)
    
    return result


def generate_comparison():
    """生成比价表"""
    data = get_all_data()
    budget = data['total_year_fee_wan']
    official_prices = get_official_prices_map()
    
    # 解析所有供应商
    vendors = {}
    for name, filepath in QUOTE_FILES.items():
        vdata = parse_quote(filepath, name)
        if vdata:
            vendors[name] = vdata
            print(f'✓ 已解析 {name}：{len(vdata["models"])}个模型，{len(vdata["plans"])}个方案')
    
    if not vendors:
        print('❌ 没有找到任何报价文件')
        return
    
    # ============ Sheet 1: 年度总价对比 ============
    wb_out = openpyxl.Workbook()
    ws1 = wb_out.active
    ws1.title = '年度总价对比'
    
    ws1.merge_cells('A1:I1')
    c = ws1.cell(row=1, column=1, value='Token资源包供应商比价表 — 年度总价对比')
    c.font = title_font
    c.fill = title_fill
    c.alignment = center
    ws1.row_dimensions[1].height = 30
    
    headers = ['供应商', '方案', '年度Token总量(万亿)', '年度总价(万元)',
               f'vs预算{budget:.1f}万', '是否支持框架协议', '套餐有效期', '是否结转', '备注']
    for i, h in enumerate(headers):
        c = ws1.cell(row=3, column=i+1, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = center
        c.border = thin_border
    ws1.row_dimensions[3].height = 40
    
    row = 4
    all_plans = []
    for vname, vdata in vendors.items():
        for plan in vdata['plans']:
            price = plan['annual_price']
            token = plan['token_total']
            
            if price and isinstance(price, (int, float)):
                vs_budget = f'{(price - budget) / budget * 100:+.0f}%'
            else:
                vs_budget = '—'
            
            ws1.cell(row=row, column=1, value=vname).alignment = center
            ws1.cell(row=row, column=2, value=plan['name']).alignment = left
            ws1.cell(row=row, column=3, value=token).alignment = center
            ws1.cell(row=row, column=4, value=price).alignment = center
            ws1.cell(row=row, column=5, value=vs_budget).alignment = center
            ws1.cell(row=row, column=6, value=plan['framework']).alignment = center
            ws1.cell(row=row, column=7, value=plan['validity']).alignment = center
            ws1.cell(row=row, column=8, value=plan['rollover']).alignment = center
            ws1.cell(row=row, column=9, value=plan['remark'][:50] if plan['remark'] else '').alignment = left
            
            for col in range(1, 10):
                ws1.cell(row=row, column=col).border = thin_border
            
            all_plans.append((vname, plan['name'], price, row))
            row += 1
    
    # 标记最优和最贵
    valid_prices = [(p[0], p[2], p[3]) for p in all_plans if p[2] and isinstance(p[2], (int, float))]
    if valid_prices:
        best = min(valid_prices, key=lambda x: x[1])
        worst = max(valid_prices, key=lambda x: x[1])
        for col in range(1, 10):
            ws1.cell(row=best[2], column=col).fill = best_fill
            ws1.cell(row=worst[2], column=col).fill = warn_fill
    
    col_widths = [8, 35, 16, 14, 14, 16, 12, 10, 40]
    for i, w in enumerate(col_widths):
        ws1.column_dimensions[get_column_letter(i+1)].width = w
    
    # ============ Sheet 2: 模型单价对比 ============
    ws2 = wb_out.create_sheet('模型单价对比')
    
    ws2.merge_cells('A1:G1')
    c = ws2.cell(row=1, column=1, value='Token资源包供应商比价表 — 模型单价对比')
    c.font = title_font
    c.fill = title_fill
    c.alignment = center
    ws2.row_dimensions[1].height = 30
    
    all_models = set()
    for vdata in vendors.values():
        for m in vdata['models']:
            all_models.add(m['name'])
    all_models = sorted(all_models)
    
    vendor_names = list(vendors.keys())
    headers2 = ['模型名称', '档位', '官方输入(未命中)', '官方输出']
    for vn in vendor_names:
        headers2.extend([f'{vn}输入(未命中)', f'{vn}输出', f'{vn}vs官方'])
    
    for i, h in enumerate(headers2):
        c = ws2.cell(row=3, column=i+1, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = center
        c.border = thin_border
    ws2.row_dimensions[3].height = 40
    
    row = 4
    for model_name in all_models:
        official = official_prices.get(model_name, {})
        official_miss = official.get('miss', '—')
        official_out = official.get('out', '—')
        
        ws2.cell(row=row, column=1, value=model_name).alignment = left
        ws2.cell(row=row, column=2, value='').alignment = center
        ws2.cell(row=row, column=3, value=official_miss).alignment = center
        ws2.cell(row=row, column=4, value=official_out).alignment = center
        
        col = 5
        for vn in vendor_names:
            vdata = vendors[vn]
            model_data = None
            for m in vdata['models']:
                if m['name'] == model_name:
                    model_data = m
                    break
            
            if model_data:
                v_miss = model_data['input_miss']
                v_out = model_data['output']
                ws2.cell(row=row, column=col, value=v_miss).alignment = center
                ws2.cell(row=row, column=col+1, value=v_out).alignment = center
                
                if isinstance(v_miss, (int, float)) and isinstance(official_miss, (int, float)) and official_miss > 0:
                    ratio = v_miss / official_miss
                    ws2.cell(row=row, column=col+2, value=f'{ratio:.1f}x').alignment = center
                else:
                    ws2.cell(row=row, column=col+2, value='—').alignment = center
            else:
                ws2.cell(row=row, column=col, value='未提供').alignment = center
                ws2.cell(row=row, column=col+1, value='—').alignment = center
                ws2.cell(row=row, column=col+2, value='—').alignment = center
            
            col += 3
        
        for c_idx in range(1, col):
            ws2.cell(row=row, column=c_idx).border = thin_border
        row += 1
    
    col_widths2 = [20, 10, 14, 12] + [14, 12, 10] * len(vendor_names)
    for i, w in enumerate(col_widths2):
        ws2.column_dimensions[get_column_letter(i+1)].width = w
    
    # ============ Sheet 3: 结论汇总 ============
    ws3 = wb_out.create_sheet('结论汇总')
    ws3.column_dimensions['A'].width = 4
    ws3.column_dimensions['B'].width = 30
    ws3.column_dimensions['C'].width = 70
    
    ws3.merge_cells('A1:C1')
    c = ws3.cell(row=1, column=1, value='比价结论汇总')
    c.font = title_font
    c.fill = title_fill
    c.alignment = center
    ws3.row_dimensions[1].height = 30
    
    row = 3
    conclusions = [
        ('1', '最优方案', ''),
        ('2', '最贵方案', ''),
        ('3', f'vs预算{budget:.1f}万', ''),
        ('4', '模型覆盖', ''),
        ('5', '框架协议支持', ''),
        ('6', '待确认事项', ''),
    ]
    
    if valid_prices:
        best_plan = min(valid_prices, key=lambda x: x[1])
        worst_plan = max(valid_prices, key=lambda x: x[1])
        conclusions[0] = ('1', '最优方案', f'{best_plan[0]} - {best_plan[1]}：{best_plan[1]:.1f}万元')
        conclusions[1] = ('2', '最贵方案', f'{worst_plan[0]} - {worst_plan[1]}：{worst_plan[1]:.1f}万元')
        conclusions[2] = ('3', f'vs预算{budget:.1f}万',
                          f'最优方案{"低于" if best_plan[1] < budget else "高于"}预算{abs(best_plan[1]-budget)/budget*100:.0f}%')
    
    for seq, label, content in conclusions:
        ws3.cell(row=row, column=1, value=seq).alignment = center
        ws3.cell(row=row, column=2, value=label).font = Font(name='微软雅黑', size=10, bold=True)
        ws3.cell(row=row, column=2).fill = PatternFill(start_color='D6E4F0', end_color='D6E4F0', fill_type='solid')
        ws3.cell(row=row, column=2).alignment = center
        ws3.cell(row=row, column=2).border = thin_border
        c = ws3.cell(row=row, column=3, value=content)
        c.alignment = left
        c.border = thin_border
        ws3.row_dimensions[row].height = 30
        row += 1
    
    # 保存
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, '供应商比价表.xlsx')
    wb_out.save(output_path)
    print(f'\n✓ 比价表已生成: {output_path}')
    print(f'  Sheet1: 年度总价对比（{len(all_plans)}个方案）')
    print(f'  Sheet2: 模型单价对比（{len(all_models)}个模型）')
    print(f'  Sheet3: 结论汇总')


def print_summary():
    """控制台打印比价摘要"""
    data = get_all_data()
    budget = data['total_year_fee_wan']
    
    print('\n' + '='*100)
    print('供应商比价摘要')
    print('='*100)
    print(f'预算基准: {budget:.1f} 万元（来自 data_provider.py）')
    
    for name, filepath in QUOTE_FILES.items():
        vdata = parse_quote(filepath, name)
        if not vdata:
            continue
        print(f'\n【{name}】')
        print(f'  模型数: {len(vdata["models"])}')
        print(f'  方案数: {len(vdata["plans"])}')
        print(f'  方案明细:')
        for plan in vdata['plans']:
            price = plan['annual_price']
            if isinstance(price, (int, float)):
                vs = f'（vs预算{budget:.1f}万: {(price-budget)/budget*100:+.0f}%）'
            else:
                vs = ''
            print(f'    - {plan["name"]}: {price}万元{vs}')


if __name__ == '__main__':
    print_summary()
    print()
    generate_comparison()

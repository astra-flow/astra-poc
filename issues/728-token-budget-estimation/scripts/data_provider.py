"""
=====================================================================
数据提供模块 — 为 Jinja2 模板提供所有计算数据
=====================================================================
统一数据源：official_prices.json + 调研表
统一计算逻辑，供所有模板渲染使用
=====================================================================
"""
import json
import os
import openpyxl
from collections import defaultdict

# ============ 路径 ============
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PRICES_JSON = os.path.join(DATA_DIR, 'official_prices.json')
SEAT_PRICES_JSON = os.path.join(DATA_DIR, 'seat_prices.json')
SURVEY_XLSX = os.path.join(DATA_DIR, '敏捷软件开发AI应用需求情况统计.xlsx')

# ============ 参数 ============
WAVE_FACTOR = 1.15
CACHE_HIT_RATE = 0.5
INPUT_OUTPUT_RATIO = (3, 1)
MILLION_TO_YI = 100


def load_prices():
    """加载官方刊例价 JSON"""
    with open(PRICES_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['models']


def load_seat_prices():
    """加载席位费 JSON，展平为产品维度（每个产品一个 vendor 条目）"""
    with open(SEAT_PRICES_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    flat = {}
    for vk, vv in data['vendors'].items():
        vendor_name = vv['name']
        for prod in vv['products']:
            prod_key = f"{vendor_name} {prod['name']}"
            entry = {
                'name': f"{vendor_name} {prod['name']}",
                'vendor_name': vendor_name,
                'product_name': prod['name'],
                'type': prod['type'],
                'plans': prod['plans'],
                'pricing_url': prod.get('pricing_url', ''),
            }
            if prod.get('resource_pack'):
                entry['resource_pack'] = prod['resource_pack']
            if prod.get('free_token_monthly_m'):
                entry['free_token_monthly_m'] = prod['free_token_monthly_m']
            if prod.get('token_packs'):
                entry['token_packs'] = prod['token_packs']
            if prod.get('notes'):
                entry['notes'] = prod['notes']
            flat[prod_key] = entry
    return flat


def calc_seat_budget(persons, token_budget_wan, prefer_vpc=True, vendor_groups=None):
    """计算席位费预算及供应商对比

    规则：
    1. 席位费按指定策略选方案（prefer_vpc=True 优先 VPC，否则取最低价）
    2. 赠送积分按厂商积分售价折为钱数，扣减 Token 预算
    3. 支持供应商分组合并（如字节系 ArkClaw+Trae）
    4. 返回各供应商的席位费、赠送积分价值、净Token预算

    Args:
        persons: 总人数
        token_budget_wan: Token 资源包年预算（万元）
        prefer_vpc: 是否优先选 VPC 方案（默认 True）
        vendor_groups: 供应商分组列表，如 [{'name': '字节系', 'vendors': ['arkclaw', 'trae'], 'persons': 400}]
                       未分组的供应商单独列出
    """
    seat_data = load_seat_prices()
    vendors = seat_data  # 已展平，直接使用

    result = {
        'persons': persons,
        'token_budget_wan': token_budget_wan,
        'vendors': {},
        'groups': {},
        'lowest_seat_vendor': None,
        'lowest_seat_annual': None,
    }

    # 计算非开发场景人数（用于 Trae 扣减）
    # 日志分析场景 127 人，非开发人员，不需要 Trae
    wb = openpyxl.load_workbook(SURVEY_XLSX, data_only=True)
    ws2 = wb['基础软件']
    non_dev_persons = 0
    for r in range(3, ws2.max_row + 1):
        if _is_summary_row(ws2, r, 1):
            continue
        non_dev_persons += float(ws2.cell(row=r, column=13).value or 0)  # 日志分析人数
    non_dev_persons = int(non_dev_persons)

    # 各供应商席位人数（默认全部）
    seat_persons = {}
    for key in vendors:
        seat_persons[key] = persons

    for key, v in vendors.items():
        plans = v['plans']
        # 取该供应商最低价方案（跳过价格为 null 的私有版）
        priced_plans = {k: p for k, p in plans.items() if p.get('price_per_seat_month') is not None}
        if not priced_plans:
            continue

        # 先确定该产品席位人数（用于 VPC 门槛判断）
        product_name = v.get('product_name', '')
        if 'Trae' in product_name:
            sp = persons - non_dev_persons  # Trae 只给开发人员
        else:
            sp = persons

        # 按策略选方案
        if prefer_vpc:
            vpc_keys = [k for k in priced_plans if 'vpc' in k.lower() or 'vpc' in priced_plans[k].get('notes', '').lower()]
            if vpc_keys:
                best_plan_key = min(vpc_keys, key=lambda k: priced_plans[k]['price_per_seat_month'])
            else:
                best_plan_key = min(priced_plans.keys(), key=lambda k: priced_plans[k]['price_per_seat_month'])
        else:
            best_plan_key = min(priced_plans.keys(), key=lambda k: priced_plans[k]['price_per_seat_month'])
        best = priced_plans[best_plan_key]

        # 使用折后价（如果有）
        effective_price = best.get('discounted_price') or best['price_per_seat_month']

        seat_month = effective_price * sp
        seat_annual = seat_month * 12

        # 赠送积分价值：每月赠送 Credits × 人数 × 12 × 积分单价
        credits_monthly = best.get('credits_per_seat_month', 0) * sp
        credits_annual = credits_monthly * 12

        # 积分折现：用该厂商资源包单价
        rp = v.get('resource_pack')
        if rp:
            credit_value = credits_annual * rp['credit_unit_price']
        else:
            credit_value = 0

        # 净Token预算 = 原Token预算 - 赠送积分价值
        net_token_budget = token_budget_wan - credit_value / 10000

        # 免费 Token（如 ArkClaw 每月赠送 50M）
        free_token_value = 0
        if 'free_token_monthly_m' in v:
            free_token_value = v['free_token_monthly_m'] * sp * 12  # 年Token(M)

        # 所有方案明细（含VPC/私有版）
        all_plans = []
        for pk, plan in plans.items():
            pp = plan.get('price_per_seat_month')
            dp = plan.get('discounted_price')
            all_plans.append({
                'name': plan['name'],
                'price_per_seat_month': pp,
                'discounted_price': dp,
                'credits_per_seat_month': plan.get('credits_per_seat_month', 0),
                'min_seats': plan.get('min_seats', 1),
                'notes': plan.get('notes', ''),
                'is_priced': pp is not None,
                'seat_annual': (dp or pp) * sp * 12 if pp is not None else None,
            })

        result['vendors'][key] = {
            'name': v['name'],
            'vendor_name': v.get('vendor_name', ''),
            'product_name': product_name,
            'type': v['type'],
            'plan_name': best['name'],
            'price_per_seat_month': best['price_per_seat_month'],
            'credits_per_seat_month': best.get('credits_per_seat_month', 0),
            'min_seats': best.get('min_seats', 1),
            'seat_persons': sp,
            'seat_monthly': seat_month,
            'seat_annual': seat_annual,
            'credits_monthly': credits_monthly,
            'credits_annual': credits_annual,
            'credit_unit_price': rp['credit_unit_price'] if rp else None,
            'credit_value': credit_value,
            'free_token_monthly_m': v.get('free_token_monthly_m', 0),
            'free_token_value': free_token_value,
            'net_token_budget': net_token_budget,
            'total_annual': seat_annual + token_budget_wan * 10000,
            'notes': best.get('notes', ''),
            'all_plans': all_plans,
        }

    # 处理供应商分组（如字节系合并）
    if vendor_groups:
        for group in vendor_groups:
            gname = group['name']
            gvendors = group['vendors']
            gpersons = group.get('persons', persons)
            combined = {
                'name': gname,
                'type': group.get('type', '组合'),
                'plan_name': '合并',
                'price_per_seat_month': None,
                'seat_persons': gpersons,
                'seat_monthly': 0,
                'seat_annual': 0,
                'credits_monthly': 0,
                'credits_annual': 0,
                'credit_value': 0,
                'net_token_budget': token_budget_wan,
                'total_annual': token_budget_wan * 10000,
                'notes': '供应商组合',
                'all_plans': [],
                'sub_vendors': [],
            }
            for gk in gvendors:
                if gk in result['vendors']:
                    sv = result['vendors'][gk]
                    combined['seat_monthly'] += sv['seat_monthly']
                    combined['seat_annual'] += sv['seat_annual']
                    combined['credits_monthly'] += sv['credits_monthly']
                    combined['credits_annual'] += sv['credits_annual']
                    combined['credit_value'] += sv['credit_value']
                    combined['net_token_budget'] -= sv['credit_value'] / 10000
                    combined['total_annual'] += sv['seat_annual']
                    combined['sub_vendors'].append(sv)
            result['groups'][gname] = combined

    # 全家桶对比（以供应商维度合并）
    bundles = {}
    # 阿里云：Qoder CN（含数字员工）
    if '阿里云 Qoder CN' in result['vendors']:
        q = result['vendors']['阿里云 Qoder CN']
        bundles['aliyun'] = {
            'name': '阿里云全家桶',
            'type': 'AI编程+数字员工',
            'seat_annual': q['seat_annual'],
            'price_per_seat_month': q['price_per_seat_month'],
            'credits_monthly': q['credits_monthly'],
            'credit_value': q['credit_value'],
            'total_annual': q['total_annual'],
            'sub_vendors': [q],
        }
    # 腾讯云：WorkBuddy
    if '腾讯云 WorkBuddy' in result['vendors']:
        w = result['vendors']['腾讯云 WorkBuddy']
        bundles['tencent'] = {
            'name': '腾讯云全家桶',
            'type': 'AI编程+数字员工',
            'seat_annual': w['seat_annual'],
            'price_per_seat_month': w['price_per_seat_month'],
            'credits_monthly': w['credits_monthly'],
            'credit_value': w['credit_value'],
            'total_annual': w['total_annual'],
            'sub_vendors': [w],
        }
    # 火山引擎全家桶：ArkClaw + Trae
    if '字节系（火山引擎）' in result.get('groups', {}):
        g = result['groups']['字节系（火山引擎）']
        avg_price = g['seat_annual'] / 12 / persons if persons > 0 else 0
        bundles['volcengine'] = {
            'name': '火山引擎全家桶',
            'type': 'AI编程+数字员工',
            'seat_annual': g['seat_annual'],
            'price_per_seat_month': round(avg_price, 2),
            'credits_monthly': g['credits_monthly'],
            'credit_value': g['credit_value'],
            'total_annual': g['total_annual'],
            'sub_vendors': g['sub_vendors'],
        }
    result['bundles'] = bundles

    # 找最低席位费（仅比较有价格的方案）
    priced_vendors = {k: v for k, v in result['vendors'].items() if v['price_per_seat_month'] is not None}
    if priced_vendors:
        lowest = min(priced_vendors.items(), key=lambda x: x[1]['price_per_seat_month'])
        result['lowest_seat_vendor'] = lowest[1]['name']
        result['lowest_seat_price'] = lowest[1]['price_per_seat_month']
        result['lowest_seat_annual'] = lowest[1]['seat_annual']

    return result
    result['lowest_seat_vendor'] = lowest[1]['name']
    result['lowest_seat_price'] = lowest[1]['price_per_seat_month']
    result['lowest_seat_annual'] = lowest[1]['seat_annual']

    return result


def weighted_price(input_hit, input_miss, output,
                   hit_rate=CACHE_HIT_RATE, ratio=INPUT_OUTPUT_RATIO):
    """计算加权单价（元/百万Token）"""
    input_weighted = input_hit * hit_rate + input_miss * (1 - hit_rate)
    total_ratio = ratio[0] + ratio[1]
    return (input_weighted * ratio[0] + output * ratio[1]) / total_ratio


def normalize_model(raw):
    """将调研表中的模型名归一化到采购模型族"""
    if not raw or raw in ('无', '-', '—', 'None'):
        return 'DeepSeek-V4-Pro'
    s = str(raw).lower().replace(' ', '').replace('\n', '').replace('_', '').replace('，', '')
    if 'deepseek' in s:
        return 'DeepSeek-V4-Pro'
    if 'qwen' in s or '千问' in s:
        return 'DeepSeek-V4-Flash'
    if 'glm' in s or 'gml' in s:
        return 'GLM-5.2'
    if 'doubao' in s or 'duubao' in s:
        return 'Doubao-Seed-Code'
    if 'gemini' in s:
        return 'Gemini'
    if 'codex' in s:
        return 'Codex'
    return 'DeepSeek-V4-Pro'


# 采购模型族 → 官方价格 JSON 中的模型映射
MODEL_MAP = {
    'DeepSeek-V4-Pro':     'DeepSeek-V4-Pro',
    'DeepSeek-V4-Flash':   'DeepSeek-V4-Flash',
    'GLM-5.2':             'GLM-5.2',
    'Codex':               'Codex',
    'Doubao-Seed-Code':    'Doubao-Seed-Code',
    'Gemini':              'Gemini',
}


def _is_summary_row(ws, row, key_col):
    """判断是否为合计行：首列（A列）为空或为'合计'，且该行有数据（人数/费用列有值）"""
    a_val = ws.cell(row=row, column=1).value
    # 合计行特征：A列为空或为'合计'文本
    a_str = str(a_val).strip() if a_val is not None else ''
    if a_str not in ('', '合计'):
        return False
    # 如果 key_col 不是 A 列，检查关键字段是否为空
    if key_col != 1:
        key_val = ws.cell(row=row, column=key_col).value
        if key_val is not None:
            return False
    # 确认该行确实有数据（不是空行）
    for c in range(2, ws.max_column + 1):
        if ws.cell(row=row, column=c).value is not None:
            return True
    return False


def calc_persons():
    """从调研表数据行计算总人数（各场景人数求和），并与合计行对比校验"""
    wb = openpyxl.load_workbook(SURVEY_XLSX, data_only=True)
    ws1 = wb['应用产品']
    ws2 = wb['基础软件']
    ws3 = wb['其他业务']

    # 应用产品：从数据行累加各场景人数（跳过合计行）
    app_persons = 0
    summary_persons = {'p1': 0, 'p2': 0, 'p3': 0, 'p4': 0}
    for r in range(3, ws1.max_row + 1):
        if _is_summary_row(ws1, r, 2):  # 合计行：产品列为空
            # 记录合计行值用于校验
            summary_persons['p1'] = float(ws1.cell(row=r, column=12).value or 0)
            summary_persons['p2'] = float(ws1.cell(row=r, column=19).value or 0)
            summary_persons['p3'] = float(ws1.cell(row=r, column=26).value or 0)
            summary_persons['p4'] = float(ws1.cell(row=r, column=33).value or 0)
            continue
        p1 = float(ws1.cell(row=r, column=12).value or 0)
        p2 = float(ws1.cell(row=r, column=19).value or 0)
        p3 = float(ws1.cell(row=r, column=26).value or 0)
        p4 = float(ws1.cell(row=r, column=33).value or 0)
        summary_persons['p1'] -= p1
        summary_persons['p2'] -= p2
        summary_persons['p3'] -= p3
        summary_persons['p4'] -= p4
        app_persons += p1 + p2 + p3 + p4

    # 基础软件
    base_persons = 0
    base_summary = 0
    for r in range(3, ws2.max_row + 1):
        if _is_summary_row(ws2, r, 1):  # 合计行：模块列为空
            base_summary = float(ws2.cell(row=r, column=6).value or 0)
            continue
        base_persons += float(ws2.cell(row=r, column=6).value or 0)

    # 其他业务
    other_persons = 0
    other_summary = 0
    for r in range(2, ws3.max_row + 1):
        if _is_summary_row(ws3, r, 1):  # 合计行：团队列为空
            other_summary = float(ws3.cell(row=r, column=2).value or 0)
            continue
        other_persons += float(ws3.cell(row=r, column=2).value or 0)

    # 校验：数据行累加值应与合计行一致
    total = int(app_persons + base_persons + other_persons)
    summary_total = int(sum(summary_persons.values()) + base_summary + other_summary)
    if total != summary_total:
        print(f'⚠ 人数校验不一致: 数据行累加={total}, 合计行={summary_total}')
        print(f'  应用产品: 累加={app_persons}, 合计={sum(summary_persons.values())}')
        print(f'  基础软件: 累加={base_persons}, 合计={base_summary}')
        print(f'  其他业务: 累加={other_persons}, 合计={other_summary}')
    else:
        print(f'✓ 人数校验通过: 数据行累加={total} == 合计行={summary_total}')

    return total


def get_survey_meta():
    """从调研表提取元数据（产品线数、模块数、记录数、场景数等）"""
    wb = openpyxl.load_workbook(SURVEY_XLSX, data_only=True)
    ws1 = wb['应用产品']
    ws2 = wb['基础软件']
    ws3 = wb['其他业务']
    
    # 应用产品线（跳过合计行）
    product_lines = set()
    app_records = 0
    for r in range(3, ws1.max_row + 1):
        if _is_summary_row(ws1, r, 2):
            continue
        product = ws1.cell(row=r, column=2).value
        if product:
            product_lines.add(str(product).strip())
        # 统计各场景有模型数据的记录数
        for c in [9, 16, 23, 30]:
            if ws1.cell(row=r, column=c).value:
                app_records += 1
    
    # 基础软件模块（跳过合计行，每个模块有开发+日志分析2个场景）
    base_modules = set()
    base_records = 0
    for r in range(3, ws2.max_row + 1):
        if _is_summary_row(ws2, r, 1):
            continue
        module = ws2.cell(row=r, column=1).value
        if module:
            base_modules.add(str(module).strip())
            base_records += 2  # 每个模块有开发+日志分析2个场景
    
    # 场景列表（日志分析已合并到基础软件开发）
    scenes = ['PRD生成', '架构图生成', '代码生成', '测试脚本', '基础软件开发', '其他业务']
    
    # 覆盖人数（从数据行累加，与 calc_persons 一致）
    app_p = 0
    for r in range(3, ws1.max_row + 1):
        if _is_summary_row(ws1, r, 2):
            continue
        p1 = float(ws1.cell(row=r, column=12).value or 0)
        p2 = float(ws1.cell(row=r, column=19).value or 0)
        p3 = float(ws1.cell(row=r, column=26).value or 0)
        p4 = float(ws1.cell(row=r, column=33).value or 0)
        app_p += p1 + p2 + p3 + p4
    
    base_p = 0
    for r in range(3, ws2.max_row + 1):
        if _is_summary_row(ws2, r, 1):
            continue
        base_p += float(ws2.cell(row=r, column=6).value or 0)
    
    other_p = 0
    for r in range(2, ws3.max_row + 1):
        if _is_summary_row(ws3, r, 1):
            continue
        other_p += float(ws3.cell(row=r, column=2).value or 0)
    
    return {
        'product_lines': len(product_lines),
        'base_modules': len(base_modules),
        'app_records': app_records,
        'base_records': base_records,
        'total_records': app_records + base_records,
        'scenes': scenes,
        'scene_count': len(scenes),
        'survey_persons': int(app_p + base_p + other_p),
    }


def parse_survey():
    """解析调研表，返回按模型族聚合的月费用"""
    wb = openpyxl.load_workbook(SURVEY_XLSX, data_only=True)
    ws1 = wb['应用产品']
    ws2 = wb['基础软件']

    agg = defaultdict(lambda: {'月总费用': 0, '记录数': 0, '场景集': set()})
    scene_agg = defaultdict(lambda: {'fee': 0, 'persons': 0})

    scenes_app = [
        ('PRD生成',    9, 10, 11, 12, 13),
        ('架构图生成', 16, 17, 18, 19, 20),
        ('代码生成',   23, 24, 25, 26, 27),
        ('测试脚本',   30, 31, 32, 33, 34),
    ]

    for r in range(3, ws1.max_row + 1):
        if _is_summary_row(ws1, r, 2):
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

    for r in range(3, ws2.max_row + 1):
        if _is_summary_row(ws2, r, 1):
            continue
        fee_dev = float(ws2.cell(row=r, column=7).value or 0)
        persons_dev = float(ws2.cell(row=r, column=6).value or 0)
        fee_log = float(ws2.cell(row=r, column=14).value or 0)
        persons_log = float(ws2.cell(row=r, column=13).value or 0)
        for sm in ['DeepSeek-V4-Pro', 'DeepSeek-V4-Flash', 'GLM-5.2']:
            agg[sm]['月总费用'] += fee_dev / 3 + fee_log / 3
            agg[sm]['记录数'] += 2
            agg[sm]['场景集'].add('基础软件开发')
        # 日志分析合并到基础软件开发
        scene_agg['基础软件开发']['fee'] += fee_dev + fee_log
        scene_agg['基础软件开发']['persons'] += persons_dev + persons_log

    # 其他业务
    ws3 = wb['其他业务']
    other_total_fee = 0
    other_persons = 0
    for r in range(2, ws3.max_row + 1):
        if _is_summary_row(ws3, r, 1):
            continue
        persons = float(ws3.cell(row=r, column=2).value or 0)
        total = float(ws3.cell(row=r, column=4).value or 0)
        other_persons += persons
        other_total_fee += total
    for sm in ['DeepSeek-V4-Pro', 'DeepSeek-V4-Flash', 'GLM-5.2']:
        agg[sm]['月总费用'] += other_total_fee / 3
        agg[sm]['记录数'] += 1
        agg[sm]['场景集'].add('其他业务')
    scene_agg['其他业务']['fee'] += other_total_fee
    scene_agg['其他业务']['persons'] += other_persons

    return agg, scene_agg


def get_all_data():
    """获取所有计算数据，供模板使用"""
    prices = load_prices()
    agg, scene_agg = parse_survey()
    PERSONS = calc_persons()
    survey_meta = get_survey_meta()

    # 预计算加权单价
    wp_map = {}
    for model_key, price_key in MODEL_MAP.items():
        p = prices[price_key]
        wp_map[model_key] = weighted_price(p['input_hit'], p['input_miss'], p['output'])

    total_month_fee = sum(d['月总费用'] for d in agg.values())
    total_year_fee_wan = total_month_fee * 12 * WAVE_FACTOR / 10000
    total_year_fee_yuan = total_year_fee_wan * 10000

    # 按模型计算
    results = []
    total_year_token_yi = 0
    for model in sorted(agg.keys(), key=lambda x: -agg[x]['月总费用']):
        d = agg[model]
        fee = d['月总费用']
        wp = wp_map[model]
        mt_M = fee / wp
        mt_yi = mt_M / MILLION_TO_YI
        yt_yi = mt_yi * 12
        yt_buf = yt_yi * WAVE_FACTOR
        yf_wan = fee * 12 * WAVE_FACTOR / 10000
        yf_yuan = fee * 12 * WAVE_FACTOR
        total_year_token_yi += yt_buf

        p = prices[MODEL_MAP[model]]
        results.append({
            'model': model,
            'fee': fee,
            'wp': wp,
            'mt_M': mt_M,
            'mt_yi': mt_yi,
            'yt_yi': yt_yi,
            'yt_buf': yt_buf,
            'yf_wan': yf_wan,
            'yf_yuan': yf_yuan,
            'input_hit': p['input_hit'],
            'input_miss': p['input_miss'],
            'output': p['output'],
            'vendor': p['vendor'],
            'tier': p['tier'],
            'source_url': p['source_url'],
            'scenes': ', '.join(sorted(d['场景集'])),
            'records': d['记录数'],
        })

    # 按波动后Token量排序（用于占比计算）
    results_sorted = sorted(results, key=lambda x: -x['yt_buf'])
    for r in results_sorted:
        r['pct'] = r['yt_buf'] / total_year_token_yi * 100

    # 场景维度
    scenes = []
    for s in sorted(scene_agg.keys(), key=lambda x: -scene_agg[x]['fee']):
        d = scene_agg[s]
        pct = d['fee'] / total_month_fee * 100
        pc = d['fee'] / d['persons'] if d['persons'] > 0 else 0
        scenes.append({
            'name': s,
            'fee': d['fee'],
            'persons': d['persons'],
            'per_person': pc,
            'pct': pct,
        })

    # 人均口径
    month_fee_per = total_month_fee / PERSONS
    total_month_tokens_M = sum(r['mt_M'] for r in results)
    overall_wp = total_month_fee / total_month_tokens_M if total_month_tokens_M > 0 else 0
    month_token_per_M = total_month_tokens_M / PERSONS
    month_token_per_yi = month_token_per_M / MILLION_TO_YI
    year_token_per_yi = total_year_token_yi / PERSONS
    year_fee_per = total_year_fee_wan * 10000 / PERSONS

    # 供应商集中度
    deepseek_fee = sum(r['fee'] for r in results if 'DeepSeek' in r['model'])
    glm_fee = sum(r['fee'] for r in results if 'GLM' in r['model'])
    other_fee = total_month_fee - deepseek_fee - glm_fee

    # 官方刊例价表
    official_prices_table = []
    for model_key, price_key in MODEL_MAP.items():
        p = prices[price_key]
        wp = wp_map[model_key]
        official_prices_table.append({
            'model': model_key,
            'vendor': p['vendor'],
            'tier': p['tier'],
            'input_hit': p['input_hit'],
            'input_miss': p['input_miss'],
            'output': p['output'],
            'wp': wp,
            'source_url': p['source_url'],
        })

    # 席位费预算（字节系合并：ArkClaw + Trae）
    vendor_groups = [
        {
            'name': '字节系（火山引擎）',
            'type': 'AI编程助手+数字员工平台',
            'vendors': ['火山引擎 ArkClaw 企业版', '火山引擎 Trae CN'],
            'persons': PERSONS,
        }
    ]
    seat_budget = calc_seat_budget(PERSONS, total_year_fee_wan, vendor_groups=vendor_groups)

    return {
        'prices': prices,
        'results': results_sorted,
        'scenes': scenes,
        'total_month_fee': total_month_fee,
        'total_year_fee_wan': total_year_fee_wan,
        'total_year_fee_yuan': total_year_fee_yuan,
        'total_year_token_yi': total_year_token_yi,
        'PERSONS': PERSONS,
        'month_fee_per': month_fee_per,
        'month_token_per_M': month_token_per_M,
        'month_token_per_yi': month_token_per_yi,
        'year_token_per_yi': year_token_per_yi,
        'year_fee_per': year_fee_per,
        'WAVE_FACTOR': WAVE_FACTOR,
        'overall_wp': overall_wp,
        'CACHE_HIT_RATE': CACHE_HIT_RATE,
        'INPUT_OUTPUT_RATIO': INPUT_OUTPUT_RATIO,
        'MILLION_TO_YI': MILLION_TO_YI,
        'deepseek_fee': deepseek_fee,
        'glm_fee': glm_fee,
        'other_fee': other_fee,
        'official_prices_table': official_prices_table,
        'survey_meta': survey_meta,
        'seat_budget': seat_budget,
        'generated_at': '2026-07-05',
    }


if __name__ == '__main__':
    # 测试输出
    data = get_all_data()
    print(f"总人数: {data['PERSONS']}")
    print(f"月总费用: {data['total_month_fee']:,.0f}")
    print(f"年预算: {data['total_year_fee_wan']:.1f} 万")
    print(f"年Token: {data['total_year_token_yi']:,.0f} 亿")
    print(f"人均月费用: {data['month_fee_per']:.0f} 元")
    print()
    for r in data['results']:
        print(f"  {r['model']:<22} {r['pct']:5.1f}%  {r['yt_buf']:>8.0f}亿  {r['yf_wan']:>6.1f}万")

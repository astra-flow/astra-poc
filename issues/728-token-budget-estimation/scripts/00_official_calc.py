"""
=====================================================================
权威计算脚本 — Token 资源包预算测算（控制台输出版）
=====================================================================
数据来源：data_provider.py（统一数据源）
功能：控制台打印预算测算结果，供人工核对

使用方式：
  python3 scripts/00_official_calc.py

注意：本脚本不直接读取数据文件，所有数据来自 data_provider.py
=====================================================================
"""
import os
import sys

# 添加 scripts 目录到 path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from data_provider import get_all_data


def main():
    data = get_all_data()
    
    print('=' * 100)
    print('Token 资源包预算测算 — 权威计算脚本')
    print('=' * 100)
    print()
    
    # 1. 官方加权单价
    print('【1】官方刊例价及加权单价')
    print(f'    假设：输入:输出 = {data["INPUT_OUTPUT_RATIO"][0]}:{data["INPUT_OUTPUT_RATIO"][1]}，'
          f'缓存命中率 = {data["CACHE_HIT_RATE"]}')
    print(f'    {"模型族":<22}{"输入(命中)":>12}{"输入(未命中)":>14}{"输出":>8}{"加权单价":>12}')
    print('    ' + '-' * 68)
    for p in data['official_prices_table']:
        print(f'    {p["model"]:<22}{p["input_hit"]:>12.3f}{p["input_miss"]:>14.2f}'
              f'{p["output"]:>8.2f}{p["wp"]:>12.4f}')
    print(f'    单价单位：元/百万Token')
    print()
    
    # 2. 调研表费用聚合
    print('【2】调研表费用聚合（按模型族）')
    print(f'    {"模型族":<22}{"月费用(元)":>14}{"记录数":>8}  涉及场景')
    print('    ' + '-' * 80)
    for r in data['results']:
        print(f'    {r["model"]:<22}{r["fee"]:>14,.0f}{r["records"]:>8}  {r["scenes"]}')
    print('    ' + '-' * 80)
    print(f'    {"合计":<22}{data["total_month_fee"]:>14,.0f}')
    print()
    
    # 3. Token 量反推 + 年预算
    print('【3】Token 量反推与年度预算（核心结果）')
    print(f'    公式：月Token(百万) = 月费用 / 加权单价')
    print(f'          年Token(亿) = 月Token(百万) × 12 ÷ {data["MILLION_TO_YI"]}')
    print(f'          年预算(万) = 月费用 × 12 × {data["WAVE_FACTOR"]} ÷ 10000')
    print()
    print(f'    {"模型族":<22}{"月费用":>10}{"加权单价":>10}{"月Token(百万)":>16}'
          f'{"月Token(亿)":>14}{"年Token(亿)":>14}{"波动后(亿)":>14}{"年预算(万)":>12}')
    print('    ' + '-' * 112)
    
    for r in data['results']:
        print(f'    {r["model"]:<22}{r["fee"]:>10,.0f}{r["wp"]:>10.4f}'
              f'{r["mt_M"]:>16,.0f}{r["mt_yi"]:>14.2f}{r["yt_yi"]:>14.2f}'
              f'{r["yt_buf"]:>14,.0f}{r["yf_wan"]:>12.1f}')
    
    print('    ' + '-' * 112)
    print(f'    {"合计":<22}{data["total_month_fee"]:>10,.0f}{"":>10}{"":>16}{"":>14}{"":>14}'
          f'{data["total_year_token_yi"]:>14,.0f}{data["total_year_fee_wan"]:>12.1f}')
    print()
    
    # 4. 人均口径
    print(f'【4】人均口径（按 {data["PERSONS"]} 人）')
    print(f'    人均月费用: {data["month_fee_per"]:.2f} 元/人/月')
    print(f'    人均月Token: {data["month_token_per_M"]:.0f} 百万/人/月 = '
          f'{data["month_token_per_yi"]:.2f} 亿/人/月')
    print(f'    人均年Token: {data["year_token_per_yi"]:.2f} 亿/人/年')
    print(f'    人均年预算: {data["year_fee_per"]:.2f} 元/人/年')
    print(f'    全公司年Token: {data["total_year_token_yi"]:,.0f} 亿')
    print(f'    全公司年预算: {data["total_year_fee_wan"]:.2f} 万元')
    print()
    
    # 5. 场景维度
    print('【5】按场景维度')
    print(f'    {"场景":<16}{"月费用(元)":>14}{"使用人数":>10}{"人均月费":>10}{"占比":>8}')
    print('    ' + '-' * 60)
    for s in data['scenes']:
        print(f'    {s["name"]:<16}{s["fee"]:>14,.2f}{s["persons"]:>10.0f}'
              f'{s["per_person"]:>10.2f}{s["pct"]:>7.1f}%')
    print()
    
    # 6. 采购方式建议
    print('【6】采购方式建议')
    print('    建议按金额签框架协议，不按Token量签，理由：')
    print('    1. 主力模型价格浮动，随新模型推出会变化')
    print('    2. 新模型我们肯定要用，但价格未知')
    print('    3. 各家Token计价方式不一，且资源包有折扣，按Token量签不可控')
    print()
    
    # 汇报口径数据
    print('=' * 100)
    print('【汇报口径数据】（供消息/文档直接引用，勿手动修改）')
    print('=' * 100)
    print(f'  调研月费用: {data["total_month_fee"]:,.2f} 元')
    print(f'  全公司人数: {data["PERSONS"]} 人')
    print(f'  人均月费用: {data["month_fee_per"]:.2f} 元/人/月')
    print(f'  业务增长率: {data["WAVE_FACTOR"]}')
    print(f'  年预算: {data["total_year_fee_wan"]:.2f} 万元')
    print(f'  人均月Token: {data["month_token_per_M"]:.0f} 百万 = '
          f'{data["month_token_per_yi"]:.2f} 亿/人/月')
    print(f'  全公司年Token: {data["total_year_token_yi"]:,.0f} 亿')
    print()
    
    # 供应商集中度
    deepseek_pct = data['deepseek_fee'] / data['total_month_fee'] * 100
    glm_pct = data['glm_fee'] / data['total_month_fee'] * 100
    print(f'  DeepSeek占比: {deepseek_pct:.1f}%（V4旗舰档 + Flash轻量档）')
    print(f'  智谱GLM-5.2占比: {glm_pct:.1f}%')
    print()

    # 7. 席位费预算
    sb = data['seat_budget']
    print('【7】席位费预算 — AI编程助手及数字员工平台')
    print(f'    总人数: {sb["persons"]} 人')
    print(f'    最低席位费: {sb["lowest_seat_vendor"]} {sb["lowest_seat_price"]}元/席位/月')
    print()
    print(f'    {"供应商":<22}{"方案":<20}{"席位人数":>8}{"席位单价":>10}{"年席位费":>12}{"月Credits":>12}{"积分价值":>12}{"净Token预算":>12}{"年度总预算":>12}')
    print('    ' + '-' * 120)
    for k, v in sb['vendors'].items():
        pp = v['price_per_seat_month']
        # 如果有折后价，显示折后价
        has_discount = any(p.get('discounted_price') for p in v.get('all_plans', []) if p.get('is_priced'))
        price_str = f'{pp}元/月'
        print(f'    {v["name"]:<22}{v["plan_name"]:<20}{v["seat_persons"]:>6}人'
              f'{price_str:>10}'
              f'{v["seat_annual"]:>10,.2f}元{v["credits_monthly"]:>10,.0f}'
              f'{v["credit_value"]:>10,.2f}元{v["net_token_budget"]:>10.2f}万'
              f'{v["total_annual"]:>10,.2f}元')
    print()
    # 供应商分组
    if sb.get('groups'):
        print(f'    {"分组合并":<22}{"年席位费":>12}{"积分价值":>12}{"净Token预算":>12}{"年度总预算":>12}')
        print('    ' + '-' * 70)
        for gname, g in sb['groups'].items():
            print(f'    {gname:<22}{g["seat_annual"]:>10,.2f}元{g["credit_value"]:>10,.2f}元'
                  f'{g["net_token_budget"]:>10.2f}万{g["total_annual"]:>10,.2f}元')
    print()
    # 全家桶对比（AI Coding + 数字员工一体）
    if sb.get('bundles'):
        print(f'    {"全家桶对比（AI编程+数字员工）":<30}{"年席位费":>12}{"席位单价":>10}')
        print('    ' + '-' * 55)
        for bk, b in sb['bundles'].items():
            pp = f'{b["price_per_seat_month"]}元/月' if b.get('price_per_seat_month') else '—'
            print(f'    {b["name"]:<30}{b["seat_annual"]:>10,.2f}元{pp:>10}')
            for sv in b.get('sub_vendors', []):
                print(f'      ├ {sv["name"]:<28}{sv["seat_annual"]:>10,.2f}元')
    print()
    print(f'    注：Trae 仅覆盖开发人员（排除日志分析场景 127 人），席位={sb["vendors"]["火山引擎 Trae CN"]["seat_persons"]}人')
    print(f'    注：净Token预算 = 原Token预算({sb["token_budget_wan"]:.2f}万) - 赠送积分折现')
    print(f'    注：ArkClaw每月赠送50M免费Token，未折算为金额')


if __name__ == '__main__':
    main()

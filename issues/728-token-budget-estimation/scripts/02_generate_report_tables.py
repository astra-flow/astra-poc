"""
=====================================================================
Token 资源包预算测算 — 表格快速预览脚本
=====================================================================
数据来源：data_provider.py（统一数据源）
功能：快速生成所有汇报表格的 markdown 内容，供控制台预览

使用方式：
  python3 scripts/02_generate_report_tables.py

输出：
  - 控制台打印所有表格（markdown 格式）
  - 生成 output/report_tables.md

注意：完整文档渲染请使用 03_render_reports.py（Jinja2 模板）
=====================================================================
"""
import os
import sys
from datetime import datetime

# 添加 scripts 目录到 path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from data_provider import get_all_data


def main():
    data = get_all_data()
    
    lines = []
    lines.append(f'<!-- 自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M")} -->')
    lines.append('')
    
    # ========== 表1：AI 应用需求统计一览表 ==========
    lines.append('## 表1：AI 应用需求统计一览表')
    lines.append('')
    lines.append('> 三区域：①模型及占比 ②官方刊例价 ③Token 需求及价格')
    lines.append('')
    lines.append('| 主力模型 | 预算占比 | 输入(缓存命中) | 输入(缓存未命中) | 输出 | 加权单价 | 月Token(亿) | 年Token(亿) | 波动后(亿) | 月费用(元) | 年预算(万元) |')
    lines.append('|---------|:-------:|:-------------:|:---------------:|:---:|:--------:|:-----------:|:-----------:|:----------:|:---------:|:------------:|')
    
    for r in data['results']:
        lines.append(
            f"| {r['model']} | {r['pct']:.1f}% | {r['input_hit']} | {r['input_miss']} | "
            f"{r['output']} | {r['wp']:.4f} | {r['mt_yi']:.2f} | {r['yt_yi']:,.0f} | "
            f"{r['yt_buf']:,.0f} | {r['fee']:,.0f} | {r['yf_wan']:.1f} |"
        )
    
    lines.append(
        f"| **合计** | **100%** | — | — | — | — | — | — | **{data['total_year_token_yi']:,.0f}** | "
        f"**{data['total_month_fee']:,.0f}** | **{data['total_year_fee_wan']:.1f}** |"
    )
    lines.append('')
    
    # ========== 表2：Token 预算表 ==========
    lines.append('## 表2：Token 预算表')
    lines.append('')
    lines.append('> 两区域：①官方刊例价 ②Token 预算')
    lines.append('')
    lines.append('| 主力模型 | 预算占比 | 输入(命中) | 输入(未命中) | 输出 | 月Token(亿) | 年Token(亿) | 波动后(亿) | 人均月Token | 年预算(万元) |')
    lines.append('|---------|:-------:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|')
    
    for r in data['results']:
        per_person = r['mt_yi'] / data['PERSONS']
        lines.append(
            f"| {r['model']} | {r['pct']:.1f}% | {r['input_hit']} | {r['input_miss']} | "
            f"{r['output']} | {r['mt_yi']:.0f} | {r['yt_yi']:,.0f} | {r['yt_buf']:,.0f} | "
            f"{per_person:.2f}亿 | {r['yf_wan']:.1f} |"
        )
    
    total_per_person = sum(r['mt_yi'] for r in data['results']) / data['PERSONS']
    lines.append(
        f"| **合计** | **100%** | — | — | — | **{sum(r['mt_yi'] for r in data['results']):.0f}** | "
        f"**{sum(r['yt_yi'] for r in data['results']):,.0f}** | **{data['total_year_token_yi']:,.0f}** | "
        f"**{total_per_person:.2f}亿** | **{data['total_year_fee_wan']:.1f}** |"
    )
    lines.append('')
    lines.append(f'> 人均月 Token = {total_per_person:.2f} 亿/人/月（按 {data["PERSONS"]} 人）；'
                 f'人均年预算 = {data["year_fee_per"]:,.0f} 元/人/年。')
    lines.append('')
    
    # ========== 表3：各厂商官方刊例价汇总 ==========
    lines.append('## 表3：各厂商官方刊例价汇总（元/百万Token）')
    lines.append('')
    lines.append('| 模型 | 厂商 | 档位 | 输入(缓存命中) | 输入(缓存未命中) | 输出 | 加权单价 | 来源 |')
    lines.append('|------|------|------|:---:|:---:|:---:|:---:|------|')
    
    for p in data['official_prices_table']:
        lines.append(
            f"| {p['model']} | {p['vendor']} | {p['tier']} | {p['input_hit']} | {p['input_miss']} | "
            f"{p['output']} | {p['wp']:.4f} | [{p['vendor']}定价页]({p['source_url']}) |"
        )
    lines.append('')
    
    # ========== 人均口径 ==========
    lines.append('## 人均口径')
    lines.append('')
    lines.append(f'| 指标 | 数值 |')
    lines.append(f'|------|:----:|')
    lines.append(f'| 月总费用 | {data["total_month_fee"]:,.0f} 元 |')
    lines.append(f'| 人均月费用 | **{data["month_fee_per"]:.0f} 元/人/月** |')
    lines.append(f'| 年预算（含波动系数） | **{data["total_year_fee_wan"]:.1f} 万元** |')
    lines.append(f'| 年 Token 总量（参考） | **{data["total_year_token_yi"]:,.0f} 亿** |')
    lines.append('')
    
    # ========== 按场景维度 ==========
    lines.append('## 按场景维度')
    lines.append('')
    lines.append('| 场景 | 月费用(元) | 使用人数 | 人均月费(元) | 占比 |')
    lines.append('|------|:---------:|:-------:|:----------:|:---:|')
    for s in data['scenes']:
        lines.append(f'| {s["name"]} | {s["fee"]:,.0f} | {s["persons"]:.0f} | {s["per_person"]:.0f} | {s["pct"]:.1f}% |')
    lines.append(f'| **合计** | **{data["total_month_fee"]:,.0f}** | — | — | 100% |')
    lines.append('')
    
    # ========== 输出 ==========
    output_text = '\n'.join(lines)
    print(output_text)
    
    OUTPUT_DIR = os.path.join(os.path.dirname(SCRIPTS_DIR), 'output')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_file = os.path.join(OUTPUT_DIR, 'report_tables.md')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(output_text)
    print(f'\n✅ 已生成: {out_file}')


if __name__ == '__main__':
    main()

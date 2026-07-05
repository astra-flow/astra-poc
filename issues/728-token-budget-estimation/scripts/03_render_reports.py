"""
=====================================================================
渲染脚本 — 使用 Jinja2 模板生成所有输出文档（统一入口）
=====================================================================
统一数据源：data_provider.py
统一模板目录：templates/
统一输出目录：output/

使用方式：
  # 一次性生成全部文档
  python3 scripts/03_render_reports.py --all

  # 分步骤生成单个文档
  python3 scripts/03_render_reports.py --doc 1   # 预算测算说明
  python3 scripts/03_render_reports.py --doc 2   # 预算汇报
  python3 scripts/03_render_reports.py --doc 3   # 供应商询价

  # 查看帮助
  python3 scripts/03_render_reports.py --help

输出文件：
  - output/01_预算测算说明.md
  - output/02_预算汇报.md
  - output/03_供应商询价.md
=====================================================================
"""
import argparse
import os
import sys
import jinja2
from datetime import datetime

# ============ 路径 ============
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# 添加 scripts 到 sys.path
sys.path.insert(0, SCRIPTS_DIR)

from data_provider import get_all_data


# ============ 文档配置 ============
DOCUMENTS = {
    1: {
        'name': '预算测算说明',
        'template': '01_预算测算说明.md.j2',
        'output': '01_预算测算说明.md',
        'desc': '完整的以内部需求调研为基础的预算测算模型',
    },
    2: {
        'name': '预算汇报',
        'template': '02_预算汇报.md.j2',
        'output': '02_预算汇报.md',
        'desc': '管理层汇报版，预算测算的提炼与总结',
    },
    3: {
        'name': '供应商询价',
        'template': '03_供应商询价.md.j2',
        'output': '03_供应商询价.md',
        'desc': '供应商询价报告，含报价模板',
    },
}


def render_template(template_name, output_name, data):
    """渲染单个模板"""
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )
    
    # 注册 Jinja2 filter
    env.filters['sum'] = lambda items, attribute=None: sum(getattr(i, attribute, 0) if attribute else i for i in items)
    
    template = env.get_template(template_name)
    rendered = template.render(**data)
    
    output_path = os.path.join(OUTPUT_DIR, output_name)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered)
    
    return output_path, len(rendered)


def main():
    parser = argparse.ArgumentParser(
        description='AI 平台预算测算文档渲染脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            '文档列表：\n'
            '  1 - 预算测算说明（完整测算模型）\n'
            '  2 - 预算汇报（管理层汇报版）\n'
            '  3 - 供应商询价（询价报告）\n\n'
            '示例：\n'
            '  python3 scripts/03_render_reports.py --all     # 生成全部\n'
            '  python3 scripts/03_render_reports.py --doc 1    # 仅生成预算测算说明\n'
            '  python3 scripts/03_render_reports.py --doc 2 3  # 生成预算汇报+供应商询价'
        )
    )
    parser.add_argument('--all', action='store_true', help='生成全部文档')
    parser.add_argument('--doc', nargs='+', type=int, help='指定要生成的文档编号（1-3），可多个')
    
    args = parser.parse_args()
    
    # 如果没有参数，显示帮助
    if not args.all and not args.doc:
        parser.print_help()
        return
    
    # 确定要生成的文档
    if args.all:
        doc_ids = list(DOCUMENTS.keys())
    else:
        doc_ids = []
        for did in args.doc:
            if did not in DOCUMENTS:
                print(f'❌ 无效的文档编号: {did}（有效范围: 1-{len(DOCUMENTS)}）')
                return
            doc_ids.append(did)
    
    print('=' * 60)
    print('AI 平台预算测算文档渲染脚本')
    print('=' * 60)
    print()
    
    # 获取数据
    print('📊 获取计算数据...')
    data = get_all_data()
    # 更新生成日期
    data['generated_at'] = datetime.now().strftime('%Y-%m-%d')
    print(f'   总人数: {data["PERSONS"]}')
    print(f'   年预算: {data["total_year_fee_wan"]:.1f} 万')
    print(f'   年Token: {data["total_year_token_yi"]:,.0f} 亿')
    print()
    
    # 渲染文档
    print(f'📝 渲染文档（{len(doc_ids)} 个）...')
    print()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for did in doc_ids:
        doc = DOCUMENTS[did]
        print(f'  [{did}] {doc["name"]}')
        print(f'      模板: {doc["template"]}')
        print(f'      说明: {doc["desc"]}')
        
        try:
            output_path, size = render_template(doc['template'], doc['output'], data)
            print(f'      ✅ {doc["output"]} ({size} 字符)')
        except Exception as e:
            print(f'      ❌ 渲染失败: {e}')
        print()
    
    print('=' * 60)
    print(f'✅ 完成，共生成 {len(doc_ids)} 个文档')
    print(f'   输出目录: {OUTPUT_DIR}')
    print('=' * 60)


if __name__ == '__main__':
    main()

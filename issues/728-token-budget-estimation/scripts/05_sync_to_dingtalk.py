"""
=====================================================================
钉钉知识库同步脚本 — 将生成的文档同步到钉钉知识库
=====================================================================
功能：通过 dws CLI 将 output/ 下的三份文档同步到钉钉知识库指定文件夹

使用方式：
  # 先生成文档（如果还没生成）
  python3 scripts/03_render_reports.py --all

  # 同步全部文档到钉钉
  python3 scripts/05_sync_to_dingtalk.py --all

  # 同步指定文档
  python3 scripts/05_sync_to_dingtalk.py --doc 1 2

  # 仅查看已同步文档列表
  python3 scripts/05_sync_to_dingtalk.py --list

  # 生成+同步一步到位
  python3 scripts/03_render_reports.py --all && python3 scripts/05_sync_to_dingtalk.py --all

依赖：dws CLI（已安装并认证）

缓存：output/.dingtalk_sync_cache.json 记录文档 nodeId，支持增量更新
=====================================================================
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime

# ============ 路径 ============
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
CACHE_FILE = os.path.join(OUTPUT_DIR, '.dingtalk_sync_cache.json')

# ============ 钉钉配置 ============
TARGET_FOLDER_ID = "YQBnd5ExVEGzgBYrTgqLNmPE8yeZqMmz"  # 竞标材料文件夹

# 文档配置
DOCUMENTS = {
    1: {'name': 'AI平台资源包预算测算说明', 'file': '01_预算测算说明.md'},
    2: {'name': 'AI平台预算汇报', 'file': '02_预算汇报.md'},
    3: {'name': 'AI平台供应商询价报告', 'file': '03_供应商询价.md'},
}


def run_dws(args, parse_json=True):
    """执行 dws CLI 命令"""
    cmd = ['dws'] + args + ['--yes']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode != 0:
        raise RuntimeError(f'dws 命令失败: {" ".join(cmd)}\nstderr: {result.stderr}\nstdout: {result.stdout}')
    
    if parse_json:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {'raw': result.stdout}
    return result.stdout


def load_cache():
    """加载同步缓存"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_cache(cache):
    """保存同步缓存"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def create_document(name, file_path, folder_id):
    """通过 dws CLI 创建文档"""
    result = run_dws([
        'doc', 'create',
        '--name', name,
        '--folder', folder_id,
        '--content-file', file_path,
        '--content-format', 'markdown',
    ])
    
    # 提取 nodeId
    node_id = None
    if isinstance(result, dict):
        node_id = result.get('nodeId') or result.get('node_id')
        if not node_id and 'result' in result:
            node_id = result['result'].get('nodeId') or result['result'].get('node_id')
    
    return node_id, result


def update_document(node_id, file_path):
    """通过 dws CLI 更新文档（覆盖模式）"""
    run_dws([
        'doc', 'update',
        '--node', node_id,
        '--content-file', file_path,
        '--content-format', 'markdown',
        '--mode', 'overwrite',
    ])
    return True


def strip_front_matter(content):
    """去掉 Markdown 文件头的 YAML front matter（--- ... ---）"""
    if content.startswith('---'):
        end = content.find('\n---', 3)
        if end != -1:
            # 跳过 front matter 和后面的空行
            content = content[end + 4:].lstrip('\n')
    return content


def sync_document(doc_id, cache):
    """同步单个文档到钉钉"""
    doc = DOCUMENTS[doc_id]
    file_path = os.path.join(OUTPUT_DIR, doc['file'])
    
    if not os.path.exists(file_path):
        print(f'  ❌ 文件不存在: {file_path}')
        print(f'     请先运行: python3 scripts/03_render_reports.py --all')
        return False
    
    # 读取文件并去掉 front matter
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = strip_front_matter(content)
    
    # 写到临时文件
    tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
    tmp_file.write(content)
    tmp_file.close()
    sync_file_path = tmp_file.name
    
    cache_key = str(doc_id)
    
    # 检查缓存中是否有 nodeId
    if cache_key in cache and cache[cache_key].get('nodeId'):
        node_id = cache[cache_key]['nodeId']
        print(f'  📝 更新文档: {doc["name"]} (nodeId: {node_id[:16]}...)')
        try:
            update_document(node_id, sync_file_path)
            cache[cache_key]['updated'] = datetime.now().isoformat()
            print(f'  ✅ 更新成功')
        except Exception as e:
            print(f'  ⚠ 更新失败，尝试重新创建: {e}')
            node_id, _ = create_document(doc['name'], sync_file_path, TARGET_FOLDER_ID)
            if node_id:
                cache[cache_key] = {
                    'nodeId': node_id,
                    'name': doc['name'],
                    'updated': datetime.now().isoformat(),
                    'url': f"https://alidocs.dingtalk.com/i/nodes/{node_id}",
                }
                print(f'  ✅ 重新创建成功 (nodeId: {node_id})')
            else:
                print(f'  ❌ 创建失败')
                return False
    else:
        print(f'  📝 创建文档: {doc["name"]}')
        node_id, raw = create_document(doc['name'], sync_file_path, TARGET_FOLDER_ID)
        if node_id:
            cache[cache_key] = {
                'nodeId': node_id,
                'name': doc['name'],
                'updated': datetime.now().isoformat(),
                'url': f"https://alidocs.dingtalk.com/i/nodes/{node_id}",
            }
            print(f'  ✅ 创建成功 (nodeId: {node_id})')
            print(f'  🔗 {cache[cache_key]["url"]}')
        else:
            print(f'  ❌ 创建失败，dws 返回: {raw}')
            return False
    
    # 清理临时文件
    try:
        os.unlink(sync_file_path)
    except OSError:
        pass
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='同步预算测算文档到钉钉知识库（通过 dws CLI）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            '文档列表：\n'
            '  1 - 预算测算说明\n'
            '  2 - 预算汇报\n'
            '  3 - 供应商询价\n\n'
            '示例：\n'
            '  python3 scripts/05_sync_to_dingtalk.py --all    # 同步全部\n'
            '  python3 scripts/05_sync_to_dingtalk.py --doc 1   # 仅同步预算测算说明\n'
            '  python3 scripts/05_sync_to_dingtalk.py --list    # 查看已同步文档\n\n'
            '完整流程：\n'
            '  python3 scripts/03_render_reports.py --all && python3 scripts/05_sync_to_dingtalk.py --all'
        )
    )
    parser.add_argument('--all', action='store_true', help='同步全部文档')
    parser.add_argument('--doc', nargs='+', type=int, help='指定要同步的文档编号（1-3）')
    parser.add_argument('--list', action='store_true', help='查看已同步文档列表')
    
    args = parser.parse_args()
    
    if not args.all and not args.doc and not args.list:
        parser.print_help()
        return
    
    cache = load_cache()
    
    # 查看列表
    if args.list:
        print('=' * 60)
        print('已同步文档列表')
        print('=' * 60)
        if not cache:
            print('  （暂无同步记录）')
        else:
            for doc_id_str, info in sorted(cache.items()):
                doc_id = int(doc_id_str)
                doc = DOCUMENTS.get(doc_id, {})
                print(f'  [{doc_id}] {info.get("name", doc.get("name", "?"))}')
                print(f'      nodeId: {info.get("nodeId", "?")}')
                print(f'      URL: {info.get("url", "?")}')
                print(f'      更新时间: {info.get("updated", "?")}')
                print()
        return
    
    # 检查 dws 是否可用
    try:
        run_dws(['auth', 'status'], parse_json=False)
    except Exception as e:
        print(f'❌ dws CLI 不可用，请先运行 dws auth login')
        print(f'   错误: {e}')
        return
    
    # 确定要同步的文档
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
    print('同步文档到钉钉知识库')
    print('=' * 60)
    print(f'  目标文件夹: 竞标材料 ({TARGET_FOLDER_ID})')
    print()
    
    # 同步文档
    print(f'📝 同步文档（{len(doc_ids)} 个）...')
    print()
    
    success_count = 0
    for doc_id in doc_ids:
        doc = DOCUMENTS[doc_id]
        print(f'  [{doc_id}] {doc["name"]}')
        if sync_document(doc_id, cache):
            success_count += 1
        print()
    
    # 保存缓存
    save_cache(cache)
    
    print('=' * 60)
    print(f'✅ 完成，成功同步 {success_count}/{len(doc_ids)} 个文档')
    if success_count > 0:
        print(f'   缓存文件: {CACHE_FILE}')
        print(f'   查看文档: python3 scripts/05_sync_to_dingtalk.py --list')
    print('=' * 60)


if __name__ == '__main__':
    main()

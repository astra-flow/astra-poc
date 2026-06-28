"""CLI 入口 — ``python -m poc``。

支持三种子命令：

- ``python -m poc run <issue>`` — 运行指定 Issue 的 POC
- ``python -m poc status [issue]`` — 查看 POC 执行进度
- ``python -m poc list`` — 列出所有注册的 POC
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from poc._discovery import discover_pocs
from poc._runner import PocRunner
from poc._status import print_status_table


def _resolve_poc_root() -> Path:
    """返回 POC 根目录（即 ``poc/``，src/ 的父目录）。"""
    return Path(__file__).resolve().parent.parent.parent


def _cmd_run(args: argparse.Namespace, poc_root: Path) -> None:
    """执行 ``python -m poc run <issue>``。"""
    registry = discover_pocs(poc_root)

    if args.issue not in registry:
        print(f"⚠️ 未找到 Issue #{args.issue} 的 POC")
        print(f"   已注册: {', '.join(f'#{k}' for k in registry)}")
        sys.exit(1)

    poc_cls = registry[args.issue]
    # 子类通过实现类方法 from_issue() 提供工厂能力
    poc_instance = poc_cls.from_issue(args.issue)
    runner = PocRunner(poc_instance)
    runner.run_all()


def _cmd_status(args: argparse.Namespace, poc_root: Path) -> None:
    """执行 ``python -m poc status [issue]``。"""
    registry = discover_pocs(poc_root)
    print_status_table(registry, poc_root, single_issue=args.issue)


def _cmd_list(args: argparse.Namespace, poc_root: Path) -> None:
    """执行 ``python -m poc list``。"""
    _ = args
    registry = discover_pocs(poc_root)

    print(f"\n已注册 POC ({len(registry)} 个):")
    print(f"{'─' * 50}")
    for issue_num, cls in registry.items():
        module_path = sys.modules.get(cls.__module__, "")
        print(f"  #{issue_num:<6} {cls.__name__:<25} {module_path}")
    print()


def main() -> None:
    """CLI 入口函数。"""
    poc_root = _resolve_poc_root()

    parser = argparse.ArgumentParser(
        prog="python -m poc",
        description="Astra POC Framework — 通用 POC 验证框架",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── run ──
    run_p = sub.add_parser("run", help="运行指定 Issue 的 POC")
    run_p.add_argument("issue", type=int, help="GitHub Issue 编号")
    run_p.add_argument("--batch", help="仅运行指定批次")
    run_p.add_argument("--evaluate", action="store_true", help="仅评估已有产出物")
    run_p.add_argument("--clean", action="store_true", help="清空产出物")
    run_p.add_argument("--daemon", action="store_true", help="后台运行")

    # ── status ──
    status_p = sub.add_parser("status", help="查看 POC 执行进度")
    status_p.add_argument("issue", nargs="?", type=int, default=None, help="Issue 编号（可选，不传则查看全部）")

    # ── list ──
    sub.add_parser("list", help="列出所有注册的 POC")

    args = parser.parse_args()

    if args.command == "run":
        _cmd_run(args, poc_root)
    elif args.command == "status":
        _cmd_status(args, poc_root)
    elif args.command == "list":
        _cmd_list(args, poc_root)


if __name__ == "__main__":
    main()

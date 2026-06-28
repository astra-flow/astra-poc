#!/usr/bin/env python3
"""向后兼容入口 — 保持 ``python3 poc.py`` 独立运行能力。

此文件模拟旧版 poc.py 的 CLI 接口，内部使用 PocImageGen。
仅用于过渡期兼容，新项目应使用 ``python -m poc run 686``。
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── 将项目根目录加入 sys.path ──
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from poc.run.runner import PocRunner

# 用 runpy 运行本地 poc.py 获取 PocImageGen 类
# 避免与已安装的 poc 框架包名冲突
import runpy
_poc_ns = runpy.run_path(str(_PROJECT_ROOT / "issue-686-ai-diagram-demo" / "poc.py"))
PocImageGen = _poc_ns["PocImageGen"]


def main() -> None:
    """模拟旧版 CLI 入口。"""
    poc = PocImageGen.from_issue(686)
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = set(a for a in sys.argv[1:] if a.startswith("--"))

    if "--clean" in flags:
        poc.clean()
        return

    if "--status" in flags:
        from poc.run.status import check_poc_status, print_status_table
        from poc.run.discovery import discover_pocs

        poc_root = Path(__file__).resolve().parent
        registry = discover_pocs(poc_root)
        print_status_table(registry, poc_root, single_issue=686)
        return

    runner = PocRunner(poc)
    runner.run_all()


if __name__ == "__main__":
    main()

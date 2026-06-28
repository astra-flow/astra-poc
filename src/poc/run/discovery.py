"""POC 自动发现与注册 — discover_pocs()。

扫描 ``poc/issues/<N>-*/poc.py`` 目录，自动采集 PocBase 子类注册表。

约定：
    - 目录名必须匹配 ``<数字>-`` 前缀（如 ``686-ai-diagram-demo``）
    - 目录下必须存在 ``poc.py`` 文件
    - ``poc.py`` 中必须定义且仅定义一个 PocBase 子类
"""

from __future__ import annotations

import inspect
import re
import runpy
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poc.base.poc import PocBase


def discover_pocs(poc_root: Path) -> dict[int, type[PocBase]]:
    """扫描 poc_root/issues/ 下所有 ``<N>-*/poc.py``，返回注册表。

    Args:
        poc_root: POC 根目录（如 ``poc/`` 的绝对路径）。

    Returns:
        ``{issue_number: PocBase_subclass}`` 映射，按 issue_number 升序排列。

    Raises:
        ValueError: 如果 poc_root 不存在。
    """
    if not poc_root.is_dir():
        raise ValueError(f"POC 根目录不存在: {poc_root}")

    issues_dir = poc_root / "issues"
    if not issues_dir.is_dir():
        return {}

    from poc.base.poc import PocBase  # noqa: F811

    registry: dict[int, type[PocBase]] = {}

    for d in sorted(issues_dir.iterdir()):
        if not d.is_dir():
            continue
        # 匹配 "<数字>-<描述>" 格式（如 "686-ai-diagram-demo"）
        match = re.match(r"(\d+)-", d.name)
        if not match:
            continue
        poc_module_path = d / "poc.py"
        if not poc_module_path.is_file():
            continue

        issue_number = int(match.group(1))
        poc_cls = _load_poc_class(poc_module_path, PocBase)
        if poc_cls is not None:
            registry[issue_number] = poc_cls

    return dict(sorted(registry.items()))


def _load_poc_class(
    module_path: Path,
    base_class: type,
) -> type | None:
    """动态导入模块并查找 PocBase 子类。

    使用 runpy.run_path() 执行 poc.py，避免 sys.path/包名冲突问题。
    POC 目录名含连字符（issue-686-ai-diagram-demo），不能作为 Python 包名，
    因此无法用常规 import 方式加载。

    Args:
        module_path: poc.py 文件路径。
        base_class: 基类类型（PocBase）。

    Returns:
        找到的 PocBase 子类，若未找到则返回 None。
    """
    # 将 POC 目录加入 sys.path，使其内部 import 能解析同目录模块
    parent_dir = str(module_path.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # 执行 poc.py，捕获全局命名空间
    globals_dict = runpy.run_path(str(module_path))

    candidates: list[type] = []
    for obj in globals_dict.values():
        if not inspect.isclass(obj):
            continue
        if obj is base_class:
            continue
        if not issubclass(obj, base_class):
            continue
        if inspect.isabstract(obj):
            continue
        candidates.append(obj)

    if len(candidates) >= 1:
        return candidates[0]
    return None

"""POC 自动发现与注册 — discover_pocs()。

扫描 ``poc/issue-<N>-*/poc.py`` 目录，自动采集 PocBase 子类注册表。

约定：
    - 目录名必须匹配 ``issue-<数字>`` 模式
    - 目录下必须存在 ``poc.py`` 文件
    - ``poc.py`` 中必须定义且仅定义一个 PocBase 子类
"""

from __future__ import annotations

import importlib.util
import inspect
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poc.base.poc_base import PocBase


def discover_pocs(poc_root: Path) -> dict[int, type[PocBase]]:
    """扫描 poc_root 下的所有 ``issue-<N>-*/poc.py``，返回注册表。

    Args:
        poc_root: POC 根目录（通常是 ``poc/`` 的绝对路径）。

    Returns:
        ``{issue_number: PocBase_subclass}`` 映射，按 issue_number 升序排列。

    Raises:
        ValueError: 如果 poc_root 不存在。
    """
    if not poc_root.is_dir():
        raise ValueError(f"POC 根目录不存在: {poc_root}")

    from poc.base.poc_base import PocBase  # noqa: F811

    registry: dict[int, type[PocBase]] = {}

    for d in sorted(poc_root.iterdir()):
        if not d.is_dir():
            continue
        match = re.match(r"issue-(\d+)", d.name)
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

    Args:
        module_path: poc.py 文件路径。
        base_class: 基类类型（PocBase）。

    Returns:
        找到的 PocBase 子类，若未找到则返回 None。
    """
    module_name = f"_poc_discovered_{module_path.parent.name}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        return None

    # 将模块父目录加入 sys.path，使其内部 import 正常工作
    parent_dir = str(module_path.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    candidates: list[type] = [
        obj
        for _, obj in inspect.getmembers(module, inspect.isclass)
        if (
            issubclass(obj, base_class)
            and obj is not base_class
            and not inspect.isabstract(obj)
        )
    ]

    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        # 取第一个非抽象子类
        return candidates[0]
    return None

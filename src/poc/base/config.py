"""POC 配置基类 — PocConfig。

所有 POC 的配置信息由此数据类承载，子类可扩展 specific 字段。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PocConfig:
    """POC 配置基类（不可变）。

    框架只读取 issue_number / output_dir / log_dir 等通用字段。
    子类通过继承添加特定字段，例如 ``ImageGenConfig(PocConfig)``。

    Attributes:
        issue_number: 关联的 GitHub Issue 编号。
        output_dir: 产出物输出目录路径（字符串形式）。
        log_dir: 日志输出目录路径（字符串形式）。
    """

    issue_number: int
    output_dir: str = "output"
    log_dir: str = "logs"

    @property
    def output_path(self) -> Path:
        """产出物目录的 Path 对象。"""
        return Path(self.output_dir)

    @property
    def log_path(self) -> Path:
        """日志目录的 Path 对象。"""
        return Path(self.log_dir)

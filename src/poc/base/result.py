"""POC 执行结果类型 — PocResult、BatchResult。

所有 POC 的 run() 方法返回 PocResult，框架据此生成评估和报告。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BatchResult:
    """单批次的执行结果。

    Attributes:
        batch_name: 批次名称（如 ``"batch_1"``、``"batch_2"``）。
        success: 该批次是否全部成功。
        artifacts: 产出物路径列表（如生成的图片路径、数据文件路径）。
        metrics: 该批次的自定义度量指标。
        error: 失败时的错误信息（可选）。
    """

    batch_name: str
    success: bool
    artifacts: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class PocResult:
    """POC 完整执行结果。

    Attributes:
        success: 是否所有批次均成功。
        batches: 各批次的执行结果列表。
        summary_metrics: 全局汇总度量指标。
    """

    success: bool
    batches: list[BatchResult] = field(default_factory=list)
    summary_metrics: dict[str, Any] = field(default_factory=dict)

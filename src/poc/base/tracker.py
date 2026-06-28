"""执行阶段成功率追踪器 — StatsTracker。

零外部依赖，适用于任意 POC 场景的 API 调用 / 步骤成功率统计。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import strftime
from typing import Final


@dataclass
class StatsRecord:
    """单条执行记录。

    Attributes:
        stage: 阶段名称（如 ``"generate_api"``、``"evaluate"``）。
        success: 是否成功。
        detail: 详细信息（如错误原因、状态码）。
        timestamp: 记录时间戳（``HH:MM:SS`` 格式）。
    """

    stage: str
    success: bool
    detail: str = ""
    timestamp: str = ""


class StatsTracker:
    """追踪各阶段 API 调用 / 步骤成功率。

    用法::

        tracker = StatsTracker()
        tracker.record("generate_api", True, "batch_1/img_1")
        tracker.record("generate_api", False, "batch_1/img_2 timeout")
        tracker.print_summary()
    """

    def __init__(self) -> None:
        self._records: list[StatsRecord] = []

    def record(self, stage: str, success: bool, detail: str = "") -> None:
        """记录一次执行结果。

        Args:
            stage: 阶段名称。
            success: 是否成功。
            detail: 详细信息（可选）。
        """
        self._records.append(
            StatsRecord(
                stage=stage,
                success=success,
                detail=detail,
                timestamp=strftime("%H:%M:%S"),
            )
        )

    def summary(self) -> dict[str, dict[str, int | float]]:
        """按阶段统计失败率。

        Returns:
            {
                "generate_api": {"total": 10, "fail": 2, "rate": 20.0},
                "evaluate":     {"total": 5,  "fail": 0, "rate": 0.0},
            }
        """
        stages: set[str] = {r.stage for r in self._records}
        result: dict[str, dict[str, int | float]] = {}
        for s in sorted(stages):
            total: int = sum(1 for r in self._records if r.stage == s)
            fail: int = sum(
                1 for r in self._records if r.stage == s and not r.success
            )
            rate: float = round(fail / total * 100, 1) if total > 0 else 0.0
            result[s] = {"total": total, "fail": fail, "rate": rate}
        return result

    def print_summary(self) -> None:
        """以可视化的方式打印失败率统计。"""
        s = self.summary()
        total_all: int = sum(v["total"] for v in s.values())  # type: ignore[assignment]
        fail_all: int = sum(v["fail"] for v in s.values())  # type: ignore[assignment]
        rate_all: float = (
            round(fail_all / total_all * 100, 1) if total_all > 0 else 0.0
        )

        print(f"\n{'=' * 60}", flush=True)
        print("📊 本轮失败率统计", flush=True)
        print(f"{'=' * 60}", flush=True)

        for stage, v in s.items():
            bar_width: int = max(1, 10 - int(v["rate"]))
            bar: str = "█" * bar_width + "░" * min(9, int(v["rate"]))
            print(
                f"  {stage:20s} total={v['total']:3d} "
                f"fail={v['fail']:3d} rate={v['rate']:5.1f}% {bar}",
                flush=True,
            )

        print(f"  {'─' * 50}", flush=True)
        print(
            f"  {'综合':20s} total={total_all:3d} "
            f"fail={fail_all:3d} rate={rate_all:5.1f}%",
            flush=True,
        )
        print(f"{'=' * 60}", flush=True)

    @property
    def records(self) -> list[StatsRecord]:
        """所有记录的只读视图。"""
        return list(self._records)

"""POC 编排执行器 — PocRunner。

遍历 POC 生命周期：setup() → run() → evaluate() → report()。
聚合 StatsTracker 并输出进度。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poc.base.poc import PocBase
    from poc.base.result import PocResult


class PocRunner:
    """POC 编排执行器。

    按序调用 PocBase 的生命周期方法，并捕获异常确保追踪完整性。

    用法::

        poc = MyPoc(config)
        runner = PocRunner(poc)
        result = runner.run_all()
    """

    def __init__(self, poc: PocBase) -> None:
        self._poc = poc

    def run_all(self) -> PocResult:
        """完整执行 POC 生命周期。

        Returns:
            PocResult 执行结果。
        """
        # 1. Setup
        print(f"\n{'=' * 60}", flush=True)
        print(f"🔧 POC #{self._poc.config.issue_number} — 初始化", flush=True)
        print(f"{'=' * 60}", flush=True)
        self._poc.setup()

        # 2. Run
        print(f"\n{'=' * 60}", flush=True)
        print(f"🚀 POC #{self._poc.config.issue_number} — 执行", flush=True)
        print(f"{'=' * 60}", flush=True)
        result = self._poc.run()

        # 3. Evaluate
        print(f"\n{'=' * 60}", flush=True)
        print(f"📊 POC #{self._poc.config.issue_number} — 评估", flush=True)
        print(f"{'=' * 60}", flush=True)
        evaluation = self._poc.evaluate(result)

        # 4. Report
        print(f"\n{'=' * 60}", flush=True)
        print(f"📝 POC #{self._poc.config.issue_number} — 报告", flush=True)
        print(f"{'=' * 60}", flush=True)
        self._poc.report(result, evaluation)

        # 5. Tracker summary
        self._poc.tracker.print_summary()

        return result

    def dry_run(self) -> None:
        """预览 POC 配置，不实际执行。"""
        print(f"\nPOC #{self._poc.config.issue_number} — 配置预览", flush=True)
        print(f"  Config: {self._poc.config}", flush=True)
        print(f"  Tracker records: {len(self._poc.tracker.records)}", flush=True)

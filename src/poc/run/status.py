"""POC 进度查看与汇总 — 检查各 POC 的产出物和评估状态。

支持单 POC 详查和全局汇总两种模式。
"""

from __future__ import annotations

import json
import os
import signal
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poc.base.poc import PocBase


def check_poc_status(poc_dir: Path, poc_cls: type[PocBase]) -> dict:
    """检查单个 POC 的执行状态。

    通过检查 output/ 目录下的产物判断进度。

    Args:
        poc_dir: POC 实例目录。
        poc_cls: PocBase 子类（当前仅用于类型标识，未使用）。

    Returns:
        ``{"issue": N, "name": str, "batches": [...], "running": bool}``
    """
    _ = poc_cls  # 保留供未来扩展
    output_dir = poc_dir / "output"
    log_dir = poc_dir / "logs"

    # 检查后台进程
    pid_file = log_dir / "poc.pid"
    running = False
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, signal.SIG_DFL)  # 信号 0 只检查进程是否存在
            running = True
        except (ValueError, OSError, ProcessLookupError):
            pid_file.unlink(missing_ok=True)

    # 检查根级评估报告
    root_report = output_dir / "evaluation_report.json"
    has_root_report = root_report.exists()

    # 检查各批次产出物
    batches: list[dict] = []
    if output_dir.is_dir():
        for batch_dir in sorted(output_dir.iterdir()):
            if not batch_dir.is_dir():
                continue
            png_files = sorted(batch_dir.glob("*.png"))
            has_report = has_root_report  # 根级报告存在即视为所有批次已有报告

            # 检查 batch 级独立报告
            if not has_report:
                report_file = batch_dir / "evaluation_report.json"
                has_report = report_file.exists()

            vision_llm_count = 0
            if has_report and has_root_report:
                try:
                    data = json.loads(root_report.read_text())
                    # 统计含 VisionLLMSingleEvaluator.verdict 的条目
                    vision_llm_count = sum(
                        1
                        for e in data
                        if isinstance(e, dict)
                        and "VisionLLMSingleEvaluator" in e
                        and isinstance(e["VisionLLMSingleEvaluator"], dict)
                        and "verdict" in e["VisionLLMSingleEvaluator"]
                    )
                except Exception:
                    pass

            batches.append(
                {
                    "name": batch_dir.name,
                    "images": len(png_files),
                    "has_report": has_report,
                    "vision_llm_count": vision_llm_count,
                }
            )

    return {
        "running": running,
        "batches": batches,
    }


def print_status_table(
    registry: dict[int, type[PocBase]],
    poc_root: Path,
    single_issue: int | None = None,
) -> None:
    """打印 POC 进度表格。

    Args:
        registry: POC 注册表。
        poc_root: POC 根目录。
        single_issue: 指定 Issue 编号，仅查看单个 POC。
    """
    if single_issue is not None:
        if single_issue not in registry:
            print(f"⚠️ 未找到 Issue #{single_issue} 的 POC")
            return
        items = {single_issue: registry[single_issue]}
    else:
        items = registry

    print(f"\n{'=' * 60}")
    print(f"📊 POC 执行进度{'总览' if single_issue is None else f' — #{single_issue}'}")
    print(f"{'=' * 60}")

    if not items:
        print("\n  (无已注册 POC)")
        return

    print(f"\n{'Issue':<8} {'批次':<10} {'图片':>5} {'评估':>6} {'LLM':>8}  状态")
    print(f"{'─'*8} {'─'*10} {'─'*5} {'─'*6} {'─'*8}  {'─'*10}")

    for issue_num, cls in items.items():
        # 从 issues/ 下匹配 <N>-<desc> 目录
        issues_dir = poc_root / "issues"
        poc_dir = None
        if issues_dir.is_dir():
            import re as _re
            for d in issues_dir.iterdir():
                if d.is_dir() and _re.match(rf"{issue_num}-", d.name):
                    poc_dir = d
                    break
        if poc_dir is None:
            poc_dir = poc_root / f"issue-{issue_num}"
        status = check_poc_status(poc_dir, cls)

        if not status["batches"]:
            print(f"{issue_num:<8} {'—':<10} {'0':>5} {'❌':>6} {'❌':>8}  {'⏳ 未开始'}")
            continue

        running_mark = "🟢" if status["running"] else "⚪"
        for b in status["batches"]:
            report_mark = "✅" if b["has_report"] else "❌"
            n = b["images"]
            vllm = b["vision_llm_count"]
            llm_mark = "✅" if vllm >= n else (f"🔄{vllm}/{n}" if vllm > 0 else "❌")
            if n == 0 and not b["has_report"]:
                batch_status = "⏳ 未开始"
            elif status["running"] and not b["has_report"]:
                batch_status = "🔄 生成中"
            elif status["running"]:
                batch_status = "🔄 进行中"
            elif b["has_report"] and vllm >= n:
                batch_status = "✅ 完成"
            elif b["has_report"]:
                batch_status = "✅ 已生成"
            else:
                batch_status = "⚪ 已完成"
            print(
                f"{issue_num:<8} {b['name']:<10} {b['images']:>5} "
                f"{report_mark:>6} {llm_mark:>8}  {batch_status}"
            )

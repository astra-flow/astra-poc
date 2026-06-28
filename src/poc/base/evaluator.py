"""组合评估器 — CompositeEvaluator + SingleEvaluator Protocol。

评估器采用 Protocol 模式，任意实现了 ``evaluate(artifact_path: str) -> dict``
的对象均可作为评估器，通过 CompositeEvaluator 组合执行。
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class SingleEvaluator(Protocol):
    """单个评估器的协议接口。

    任何实现了 ``evaluate(artifact_path: str) -> dict`` 的可调用对象
    均可作为评估器使用，无需继承特定基类。
    """

    def evaluate(self, artifact_path: str) -> dict:
        """对单个产出物进行评估。

        Args:
            artifact_path: 产出物路径。

        Returns:
            评估结果字典，结构由具体实现定义。
        """
        ...


class CompositeEvaluator:
    """组合多个评估器，按顺序执行并聚合结果。

    评估器类型不限，可以是：
    - PIL 图片质量分析
    - 视觉 LLM 评分
    - 数据正确性校验
    - API 响应时间检测
    - 任意自定义评估逻辑

    用法::

        evaluator = CompositeEvaluator([
            PillowEvaluator(),
            VisionLLMEvaluator(config=cfg),
        ])
        results = evaluator.evaluate_all(["img_1.png", "img_2.png"])
    """

    def __init__(self, evaluators: list[SingleEvaluator]) -> None:
        self._evaluators = list(evaluators)

    def evaluate_all(self, artifact_paths: list[str]) -> list[dict]:
        """对所有产出物执行全量评估。

        Args:
            artifact_paths: 产出物路径列表。

        Returns:
            评估结果列表，每项对应一个产出物的全量评估。
        """
        results: list[dict] = []
        for path in artifact_paths:
            item: dict[str, object] = {"artifact": path}
            for evaluator in self._evaluators:
                try:
                    item[evaluator.__class__.__name__] = evaluator.evaluate(path)
                except Exception as exc:
                    item[evaluator.__class__.__name__] = {
                        "error": str(exc),
                    }
            results.append(item)
        return results

    @property
    def evaluators(self) -> list[SingleEvaluator]:
        """注册的评估器列表（只读）。"""
        return list(self._evaluators)

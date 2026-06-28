"""POC 抽象基类 — PocBase[T]。

所有 POC 必须继承 PocBase 并实现其生命周期方法。
使用泛型 ``TConfig`` 绑定具体配置类型，确保类型安全。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from poc.base.config import PocConfig
from poc.base.result import PocResult
from poc.base.tracker import StatsTracker

TConfig = TypeVar("TConfig", bound=PocConfig)


class PocBase(ABC, Generic[TConfig]):
    """所有 POC 的抽象基类。

    子类必须实现以下生命周期方法：

    1. ``setup()`` — 初始化资源、校验依赖
    2. ``run()`` — 执行核心验证逻辑
    3. ``evaluate()`` — 对 run() 产出的结果进行评估
    4. ``report()`` — 生成可读报告

    用法::

        class MyPoc(PocBase[MyConfig]):
            def setup(self) -> None:
                ...

            def run(self) -> PocResult:
                ...

            def evaluate(self, result: PocResult) -> dict:
                ...

            def report(self, result: PocResult, evaluation: dict) -> None:
                ...
    """

    def __init__(self, config: TConfig) -> None:
        self.config = config
        self.tracker = StatsTracker()

    @classmethod
    def from_issue(cls, issue_number: int) -> "PocBase[TConfig]":
        """根据 Issue 编号创建 POC 实例的工厂方法。

        子类应覆盖此方法以提供自己的配置构造逻辑。
        默认实现抛出 NotImplementedError。

        Args:
            issue_number: GitHub Issue 编号。

        Returns:
            PocBase 子类实例。
        """
        raise NotImplementedError(
            f"{cls.__name__} 未实现 from_issue() 类方法"
        )

    @abstractmethod
    def setup(self) -> None:
        """初始化环境、校验凭证 / 依赖是否就绪。

        在 run() 之前由 PocRunner 自动调用。
        若环境不满足条件，应抛出异常终止执行。
        """
        ...

    @abstractmethod
    def run(self) -> PocResult:
        """执行核心 POC 逻辑，返回结构化结果。

        Returns:
            包含各批次执行结果的 PocResult 对象。
        """
        ...

    @abstractmethod
    def evaluate(self, result: PocResult) -> dict:
        """对 run() 产出的结果进行质量评估。

        Args:
            result: run() 返回的执行结果。

        Returns:
            评估报告字典（结构由子类定义）。
        """
        ...

    @abstractmethod
    def report(self, result: PocResult, evaluation: dict) -> None:
        """生成可读报告。

        可将报告输出到控制台、保存为文件、或上传到 GitHub Issue。
        """

    def cleanup(self) -> None:
        """释放资源（可选覆盖）。

        在 POC 执行完毕后由 PocRunner 调用。
        默认实现为空，子类可覆盖以释放 HTTP Session 等资源。
        """
        """
        ...

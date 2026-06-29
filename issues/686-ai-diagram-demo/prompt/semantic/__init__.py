"""
语义 Builder — 图表类型专属的原语构建器

每个 Builder 输出结构化 Prompt 文本片段，供 PromptBuilder 总装器组装。
支持通过 ``+`` 运算符组合多个片段。
"""

from .sequence import Phase, Swimlane
from .annotation import Anchored

__all__ = ["Phase", "Swimlane", "Anchored"]

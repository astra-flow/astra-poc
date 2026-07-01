"""
语义 Builder — 图表类型专属的原语构建器

每个 Builder 输出结构化 Prompt 文本片段，供 PromptBuilder 总装器组装。
支持通过 ``+`` 运算符组合多个片段。
"""

from .sequence import Phase, Swimlane, SequenceBuilder
from .annotation import Anchored, AnnotationBuilder
from .container import ContainerBuilder
from .matrix import MatrixBuilder
from .radial import RadialBuilder
from .connector import ConnectorBuilder, Connector
from .boundary import BoundaryBoxBuilder, BoundaryBox
from .chart import Chart, Row

__all__ = [
    "Phase", "Swimlane", "SequenceBuilder",
    "Anchored", "AnnotationBuilder",
    "ContainerBuilder",
    "MatrixBuilder",
    "RadialBuilder",
    "ConnectorBuilder", "Connector",
    "BoundaryBoxBuilder", "BoundaryBox",
    "Chart", "Row",
]

__all__ = ["Phase", "Swimlane", "SequenceBuilder", "Anchored", "Chart", "Row"]

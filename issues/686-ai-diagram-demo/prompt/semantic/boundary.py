"""
BoundaryBoxBuilder — 边界框原语

用虚线/实线边界框表达系统边界/分组归属。
替代连线的"边界"语义。
"""

from __future__ import annotations

from typing import Optional


class BoundaryBox:
    """边界框 — 虚线/实线边界框。

    Attributes:
        label: 边界框标签。
        border_style: 边框样式（solid / dashed / dotted）。
        border_color: 边框颜色。
        bg_color: 背景色（通常为透明或极浅色）。
        children: 内部包含的元素列表。
    """

    def __init__(
        self,
        label: str,
        border_style: str = "dashed",
        border_color: str = "#8E8E93",
        bg_color: str = "透明",
        children: Optional[list[str]] = None,
    ) -> None:
        self.label = label
        self.border_style = border_style
        self.border_color = border_color
        self.bg_color = bg_color
        self.children = children or []


class BoundaryBoxBuilder:
    """边界框原语构建器。

    每个方法返回一段 Prompt 文本片段，描述一种边界框布局。
    """

    @staticmethod
    def system_boundary(
        label: str,
        components: list[str],
        border_color: str = "#8E8E93",
        dashed: bool = True,
    ) -> str:
        """系统边界 — 虚线框包裹一组组件。

        Args:
            label: 边界框标签。
            components: 内部组件列表。
            border_color: 边框颜色。
            dashed: 是否虚线。

        Returns:
            Prompt 文本片段。
        """
        style = "虚线" if dashed else "实线"
        items = "、".join(f"'{c}'" for c in components)
        return (
            f"{border_color}色{style}边界框'{label}'"
            f"：内部包含{len(components)}个组件——{items}"
        )

    @staticmethod
    def zone(
        label: str,
        components: list[str],
        bg_color: str = "#F9F9FB",
        border_color: str = "#D0D5DD",
    ) -> str:
        """区域边界 — 浅色背景区域包裹一组组件。

        Args:
            label: 区域标签。
            components: 内部组件列表。
            bg_color: 区域背景色。
            border_color: 区域边框色。

        Returns:
            Prompt 文本片段。
        """
        items = "、".join(f"'{c}'" for c in components)
        return (
            f"{bg_color}背景、{border_color}边框的区域'{label}'"
            f"：包含{len(components)}个组件——{items}"
        )

    @staticmethod
    def legend_box(
        label: str,
        items: list[tuple[str, str, str]],
        border_color: str = "#D0D5DD",
    ) -> str:
        """图例框 — 带颜色说明的图例区域。

        Args:
            label: 图例框标题。
            items: 图例项列表，每项为 (颜色描述, 符号, 含义)。
            border_color: 边框颜色。

        Returns:
            Prompt 文本片段。
        """
        lines = [f"{border_color}边框的图例框'{label}'："]
        for color_desc, symbol, meaning in items:
            lines.append(f"  {color_desc}的'{symbol}'表示'{meaning}'")
        return "\n".join(lines)

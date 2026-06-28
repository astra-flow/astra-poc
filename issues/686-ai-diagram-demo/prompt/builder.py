"""
PromptBuilder 总装器 — 组装语义 Builder + 美学 Builder + 布局规则 + 跨层锚定。

输出完整 Prompt 文本，可直接用于 ARK API 调用。
"""

from __future__ import annotations

from typing import Optional, Union


class LayoutRule:
    """布局规则 — 宏观布局 + 微观布局两层。

    Attributes:
        direction: 排列方向（horizontal / vertical）。
        align: 对齐方式（center / left / right）。
        margin: 间距描述（如 "均衡"、"紧凑"、"宽松"）。
        whitespace: 留白比描述（如 "充足"、"适中"、"紧凑"）。
    """

    def __init__(
        self,
        direction: str = "horizontal",
        align: str = "center",
        margin: str = "均衡",
        whitespace: str = "充足",
    ) -> None:
        self.direction = direction
        self.align = align
        self.margin = margin
        self.whitespace = whitespace

    def build(self) -> str:
        """输出布局规则的 Prompt 描述。"""
        parts = []
        if self.direction == "horizontal":
            parts.append("从左到右水平排列")
        else:
            parts.append("从上到下垂直排列")
        parts.append(f"{self.align}对齐")
        parts.append(f"间距{self.margin}")
        parts.append(f"留白{self.whitespace}")
        return "，".join(parts)


class IconPicker:
    """图标选择器 — 语义选型 + 美学定风格。

    Attributes:
        type_name: 图标类型（如 database, server, user, gear, cloud）。
        style: 图标风格（line / fill / dual）。
        size: 图标尺寸（small / medium / large）。
        color: 图标颜色（色号）。
    """

    def __init__(
        self,
        type_name: str,
        style: str = "line",
        size: str = "small",
        color: str = "#8E8E93",
    ) -> None:
        self.type_name = type_name
        self.style = style
        self.size = size
        self.color = color

    def build(self) -> str:
        """输出图标描述的 Prompt 片段。"""
        style_map = {"line": "线性", "fill": "填充", "dual": "双色"}
        size_map = {"small": "小型", "medium": "中型", "large": "大型"}
        return (
            f"{size_map.get(self.size, self.size)}"
            f"{style_map.get(self.style, self.style)}"
            f"图标'{self.type_name}'，{self.color}色"
        )


class PromptBuilder:
    """Prompt 总装器。

    接收语义 Builder + 美学 Builder + 布局规则 + 图标选择器的输出，
    组装为完整的 Prompt 文本。

    用法::

        prompt = PromptBuilder(
            semantic=container_builder_output,
            aesthetic=StylePreset.consulting(),
            layout=LayoutRule(),
        ).build()
    """

    def __init__(
        self,
        semantic: str = "",
        aesthetic: str = "",
        layout: Optional[LayoutRule] = None,
        icons: Optional[list[IconPicker]] = None,
        title_text: str = "",
        no_line: bool = True,
    ) -> None:
        self.semantic = semantic
        self.aesthetic = aesthetic
        self.layout = layout or LayoutRule()
        self.icons = icons or []
        self.title_text = title_text
        self.no_line = no_line

    def build(self) -> str:
        """组装完整 Prompt。

        Returns:
            完整的 Prompt 文本，可直接用于 ARK API 调用。
        """
        sections = []

        # 1. 图类型声明 + 基础风格
        if self.aesthetic:
            sections.append(self.aesthetic)

        # 2. 语义内容
        if self.semantic:
            sections.append(self.semantic)

        # 3. 布局规则
        sections.append(self.layout.build())

        # 4. 图标
        for icon in self.icons:
            sections.append(icon.build())

        # 5. 无连线约束
        if self.no_line:
            sections.append("完全不要连接线或箭头")

        return "\n\n".join(sections)

    @classmethod
    def assemble(
        cls,
        semantic_parts: list[str],
        aesthetic_parts: Optional[list[str]] = None,
        **kwargs,
    ) -> "PromptBuilder":
        """便捷组装方法 — 直接传入语义片段列表和美学片段列表。

        Args:
            semantic_parts: 语义 Builder 输出的片段列表。
            aesthetic_parts: 美学 Builder 输出的片段列表。
            **kwargs: 传递给 PromptBuilder 的其他参数。

        Returns:
            PromptBuilder 实例。
        """
        semantic = "\n\n".join(semantic_parts)
        aesthetic = "\n\n".join(aesthetic_parts) if aesthetic_parts else ""
        return cls(semantic=semantic, aesthetic=aesthetic, **kwargs)

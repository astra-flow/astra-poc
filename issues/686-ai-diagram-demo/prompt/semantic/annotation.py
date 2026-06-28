"""
AnnotationBuilder — 标注化原语

用数值/等级/颜色标注元信息。
替代连线的"附加信息"语义。
"""

from __future__ import annotations

from typing import Optional


class Anchored:
    """跨层锚定引用 — 数据归属在源层，通过 at_step 锚定到目标层。

    核心原则：归属优先于对齐。
    Anchored 属于源层（如 Swimlane），通过 at_step 引用目标层索引。

    Attributes:
        text: 锚定文本。
        at_step: 锚定到的步骤索引（0-based）。
        position: 锚定位置（below / above / inside）。
    """

    def __init__(
        self,
        text: str,
        at_step: int,
        position: str = "below",
    ) -> None:
        self.text = text
        self.at_step = at_step
        self.position = position


class AnnotationBuilder:
    """标注化原语构建器。

    每个方法返回一段 Prompt 文本片段，描述一种标注方式。
    """

    @staticmethod
    def value_label(
        items: list[tuple[str, str]],
        prefix: str = "下方标注",
    ) -> str:
        """数值标注 — 在元素下方标注数值/时效。

        Args:
            items: 标注列表，每项为 (元素名, 标注值)。
            prefix: 标注前缀。

        Returns:
            Prompt 文本片段。
        """
        parts = [f"{prefix}："]
        for name, value in items:
            parts.append(f"  {name}：'{value}'")
        return "\n".join(parts)

    @staticmethod
    def level(
        levels: list[tuple[str, str, str, str]],
    ) -> str:
        """等级标注 — 阶梯式等级描述。

        Args:
            levels: 等级列表，每项为 (等级名, 颜色, 描述, 包含内容)。

        Returns:
            Prompt 文本片段。
        """
        lines = []
        for name, color, desc, content in levels:
            lines.append(
                f"'{name}'使用{color}色，{desc}：{content}"
            )
        return "\n".join(lines)

    @staticmethod
    def color_code(
        items: list[tuple[str, str, str]],
    ) -> str:
        """颜色编码标注 — 用颜色区分不同类型。

        Args:
            items: 编码列表，每项为 (类别, 颜色, 内容)。

        Returns:
            Prompt 文本片段。
        """
        lines = []
        for category, color, content in items:
            lines.append(
                f"{category}使用{color}色：{content}"
            )
        return "\n".join(lines)

    @staticmethod
    def emotion_curve(
        phases: list[tuple[str, str]],
    ) -> str:
        """情绪曲线标注 — 各阶段的情绪值描述。

        Args:
            phases: 阶段列表，每项为 (阶段名, 情绪描述)。

        Returns:
            Prompt 文本片段。
        """
        parts = ["每个阶段下方标注情绪曲线："]
        for name, emotion in phases:
            parts.append(f"  {name}→{emotion}")
        return "\n".join(parts)

    @staticmethod
    def anchored_list(
        label: str,
        items: list[Anchored | str],
        bg_color: str = "#F0F2F5",
    ) -> str:
        """锚定列表 — 底部泳道/汇总区，包含锚定到具体阶段的条目。

        Args:
            label: 区域标签。
            items: 条目列表，可以是普通字符串或 Anchored 对象。
            bg_color: 区域背景色。

        Returns:
            Prompt 文本片段。
        """
        lines = [f"{bg_color}背景：'{label}'"]
        for item in items:
            if isinstance(item, Anchored):
                pos_cn = {"below": "下方", "above": "上方", "inside": "内部"}.get(
                    item.position, item.position
                )
                lines.append(
                    f"  - 阶段{item.at_step + 1}{pos_cn}：'{item.text}'"
                )
            else:
                lines.append(f"  - '{item}'")
        return "\n".join(lines)

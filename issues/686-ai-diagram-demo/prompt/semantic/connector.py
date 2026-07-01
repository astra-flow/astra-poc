"""
ConnectorBuilder — 连接线原语

用箭头/连线/路径表达关系。
替代连线的"关系"语义。
注意：POC 结论是"无连线版效果最好"，此原语主要用于需要显式表达连接关系的场景。
"""

from __future__ import annotations

from typing import Optional


class Connector:
    """连接线 — 两个元素之间的连线。

    Attributes:
        from_label: 起点标签。
        to_label: 终点标签。
        arrow_style: 箭头样式（solid / dashed / dotted / double）。
        label: 连线上的标签文字。
        color: 连线颜色。
    """

    def __init__(
        self,
        from_label: str,
        to_label: str,
        arrow_style: str = "solid",
        label: str = "",
        color: str = "#8E8E93",
    ) -> None:
        self.from_label = from_label
        self.to_label = to_label
        self.arrow_style = arrow_style
        self.label = label
        self.color = color


class ConnectorBuilder:
    """连接线原语构建器。

    每个方法返回一段 Prompt 文本片段，描述一种连接关系。
    """

    @staticmethod
    def arrow(
        from_label: str,
        to_label: str,
        label: str = "",
        color: str = "#8E8E93",
        dashed: bool = False,
    ) -> str:
        """箭头连接 — 从 A 指向 B 的箭头。

        Args:
            from_label: 起点标签。
            to_label: 终点标签。
            label: 连线上的标签文字。
            color: 连线颜色。
            dashed: 是否虚线。

        Returns:
            Prompt 文本片段。
        """
        style = "虚线" if dashed else "实线"
        label_part = f"，标签'{label}'" if label else ""
        return (
            f"从'{from_label}'到'{to_label}'的{style}{color}色箭头{label_part}"
        )

    @staticmethod
    def bidirectional(
        a_label: str,
        b_label: str,
        label: str = "",
        color: str = "#8E8E93",
    ) -> str:
        """双向连接 — A 和 B 之间的双向箭头。

        Args:
            a_label: A 标签。
            b_label: B 标签。
            label: 连线上的标签文字。
            color: 连线颜色。

        Returns:
            Prompt 文本片段。
        """
        label_part = f"，标签'{label}'" if label else ""
        return (
            f"'{a_label}'和'{b_label}'之间的双向{color}色箭头{label_part}"
        )

    @staticmethod
    def flow(
        steps: list[tuple[str, str, str]],
        color: str = "#8E8E93",
    ) -> str:
        """流程连接 — 多个步骤之间的顺序箭头。

        Args:
            steps: 步骤列表，每项为 (起点, 终点, 标签)。
            color: 连线颜色。

        Returns:
            Prompt 文本片段。
        """
        lines = [f"以下{len(steps)}条{color}色箭头按顺序连接："]
        for i, (frm, to, label) in enumerate(steps):
            label_part = f"（'{label}'）" if label else ""
            lines.append(f"  {i+1}. '{frm}' → '{to}'{label_part}")
        return "\n".join(lines)

    @staticmethod
    def return_arrow(
        from_label: str,
        to_label: str,
        label: str = "驳回→返回",
        color: str = "#E8A0A0",
    ) -> str:
        """返回箭头 — 从某步骤返回上一步骤的箭头。

        Args:
            from_label: 起点标签。
            to_label: 终点标签。
            label: 连线上的标签文字。
            color: 连线颜色。

        Returns:
            Prompt 文本片段。
        """
        return (
            f"从'{from_label}'返回到'{to_label}'的{color}色虚线箭头，标签'{label}'"
        )

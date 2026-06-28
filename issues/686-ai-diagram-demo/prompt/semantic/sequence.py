"""
SequenceBuilder — 序列化原语

用线性/分支/闭环表达时序流程关系。
替代连线的"时序/流程"语义。
"""

from __future__ import annotations

from typing import Optional


class Phase:
    """序列中的一个阶段/步骤。

    Attributes:
        name: 阶段名称。
        items: 阶段包含的组件列表。
        bg_color: 阶段容器背景色。
        annotations: 锚定到该阶段的标注列表（如机会点、时效）。
    """

    def __init__(
        self,
        name: str,
        items: Optional[list[str]] = None,
        bg_color: str = "#F0F2F5",
        annotations: Optional[list[str]] = None,
    ) -> None:
        self.name = name
        self.items = items or []
        self.bg_color = bg_color
        self.annotations = annotations or []


class SequenceBuilder:
    """序列化原语构建器。

    每个方法返回一段 Prompt 文本片段，描述一种序列布局。
    """

    @staticmethod
    def linear(
        title: str,
        steps: list[Phase],
        direction: str = "horizontal",
        bottom_layer: Optional[str] = None,
    ) -> str:
        """线性序列 — 从左到右或从上到下的步骤流。

        Args:
            title: 序列标题。
            steps: 阶段列表。
            direction: 排列方向（horizontal / vertical）。
            bottom_layer: 底部泳道/汇总区描述（可选）。
            bottom_layer: 底部泳道/汇总区描述（可选）。

        Returns:
            Prompt 文本片段。
        """
        direction_cn = "从左到右水平排列" if direction == "horizontal" else "从上到下垂直排列"
        lines = [f"顶部深蓝灰色大标题'{title}'，居中显示"]
        lines.append(f"横向{len(steps)}个阶段（{direction_cn}，每个阶段一个容器框）：")

        for i, step in enumerate(steps):
            items = "、".join(f"'{c}'" for c in step.items) if step.items else ""
            base = f"阶段{i + 1}（{step.bg_color}背景）：'{step.name}'"
            if items:
                base += f" - 包含{items}"
            lines.append(base)
            for ann in step.annotations:
                lines.append(f"  ↳ 下方标注'{ann}'")

        if bottom_layer:
            lines.append(bottom_layer)

        return "\n".join(lines)

    @staticmethod
    def branch(
        title: str,
        branches: list[tuple[str, list[str]]],
        bg_color: str = "#F0F2F5",
    ) -> str:
        """分支序列 — 多分支对比布局。

        Args:
            title: 标题。
            branches: 分支列表，每项为 (分支名, 标签列表)。
            bg_color: 容器背景色。

        Returns:
            Prompt 文本片段。
        """
        lines = [f"顶部深蓝灰色大标题'{title}'，居中显示"]
        lines.append("从上到下垂直排列，每行一个容器框：")

        for i, (name, tags) in enumerate(branches):
            tag_str = "、".join(f"'{t}'" for t in tags)
            lines.append(
                f"第{i + 1}行（{bg_color}背景）：'{name}' - 标签：{tag_str}"
            )

        return "\n".join(lines)

    @staticmethod
    def loop(
        title: str,
        steps: list[Phase],
        return_point: int,
        return_label: str = "驳回→返回",
    ) -> str:
        """闭环序列 — 带返回路径的流程。

        Args:
            title: 标题。
            steps: 步骤列表。
            return_point: 返回目标步骤索引（0-based）。
            return_label: 返回路径标签。

        Returns:
            Prompt 文本片段。
        """
        lines = [f"顶部深蓝灰色大标题'{title}'，居中显示"]
        lines.append("从左到右水平排列的步骤卡片：")

        for i, step in enumerate(steps):
            items = "、".join(f"'{c}'" for c in step.items) if step.items else ""
            base = f"步骤{i + 1}（{step.bg_color}背景）：'{step.name}'"
            if items:
                base += f" - 包含{items}"
            lines.append(base)

        lines.append(
            f"在步骤{len(steps)}下方有一个浅红色小卡片"
            f"'{return_label}步骤{return_point + 1}'"
        )

        return "\n".join(lines)

"""
SequenceBuilder — 序列化原语

用线性/分支/闭环表达时序流程关系。
替代连线的"时序/流程"语义。
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .annotation import Anchored


class Swimlane:
    """泳道/层 — 阶段下方的独立行。

    Attributes:
        label: 泳道名称标签。
        items: 泳道内容列表（字符串或 Anchored 对象）。
        bg_color: 泳道背景色。
    """

    def __init__(
        self,
        label: str,
        items: Optional[list[str | "Anchored"]] = None,
        bg_color: str = "#F0F2F5",
    ) -> None:
        self.label = label
        self.items = items or []
        self.bg_color = bg_color


class Phase:
    """序列中的一个阶段/步骤。

    Attributes:
        name: 阶段名称。
        items: 阶段包含的组件列表。
        bg_color: 阶段容器背景色。
        emotion: 情绪等级（高/较高/中等/较低/低），自动映射为背景色。
        annotations: 锚定到该阶段的标注列表（如机会点、时效）。
    """

    # 情绪→背景色映射
    EMOTION_COLORS = {
        "很高": "#D4E8D4",   # 深绿
        "高": "#E0F0E0",     # 浅绿
        "较高": "#E8F0E0",   # 黄绿
        "中等": "#F0F0E0",   # 米黄
        "较低": "#F5E8D8",   # 浅橙
        "低": "#F5D8D8",     # 浅红
        "很低": "#F0C8C8",   # 粉红
    }

    def __init__(
        self,
        name: str,
        items: Optional[list[str]] = None,
        bg_color: str = "#F0F2F5",
        emotion: Optional[str] = None,
        annotations: Optional[list[str]] = None,
    ) -> None:
        self.name = name
        self.items = items or []
        self.bg_color = self.EMOTION_COLORS.get(emotion, bg_color) if emotion else bg_color
        self.emotion = emotion
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
        top_swimlanes: Optional[list[Swimlane]] = None,
        bottom_swimlanes: Optional[list[Swimlane]] = None,
    ) -> str:
        """线性序列 — 从左到右或从上到下的步骤流，支持顶部/底部泳道。

        Args:
            title: 序列标题。
            steps: 阶段列表。
            direction: 排列方向（horizontal / vertical）。
            top_swimlanes: 顶部泳道列表（如情绪曲线）。
            bottom_swimlanes: 底部泳道列表（如机会点）。

        Returns:
            Prompt 文本片段。
        """
        direction_cn = "从左到右水平排列" if direction == "horizontal" else "从上到下垂直排列"
        lines = [f"顶部深蓝灰色大标题'{title}'，居中显示"]

        # 顶部泳道（如情绪曲线）
        if top_swimlanes:
            for lane in top_swimlanes:
                lane_items = []
                for item in lane.items:
                    if isinstance(item, str):
                        lane_items.append(f"'{item}'")
                    else:
                        pos_cn = {"below": "下方", "above": "上方", "inside": "内部"}.get(
                            getattr(item, "position", "below"), "下方"
                        )
                        lane_items.append(
                            f"阶段{getattr(item, 'at_step', 0) + 1}{pos_cn}：'{getattr(item, 'text', '')}'"
                        )
                items_str = "、".join(lane_items)
                lines.append(
                    f"{lane.bg_color}背景的泳道'{lane.label}'：{items_str}"
                )

        # 阶段
        lines.append(f"横向{len(steps)}个阶段（{direction_cn}，每个阶段一个容器框）：")
        for i, step in enumerate(steps):
            items = "、".join(f"'{c}'" for c in step.items) if step.items else ""
            base = f"阶段{i + 1}（{step.bg_color}背景）：'{step.name}'"
            if items:
                base += f" - 包含{items}"
            lines.append(base)
            for ann in step.annotations:
                lines.append(f"  ↳ 下方标注'{ann}'")

        # 底部泳道（如机会点）
        if bottom_swimlanes:
            for lane in bottom_swimlanes:
                lane_items = []
                for item in lane.items:
                    if isinstance(item, str):
                        lane_items.append(f"'{item}'")
                    else:
                        pos_cn = {"below": "下方", "above": "上方", "inside": "内部"}.get(
                            getattr(item, "position", "below"), "下方"
                        )
                        lane_items.append(
                            f"阶段{getattr(item, 'at_step', 0) + 1}{pos_cn}：'{getattr(item, 'text', '')}'"
                        )
                items_str = "、".join(lane_items)
                lines.append(
                    f"{lane.bg_color}背景的泳道'{lane.label}'：{items_str}"
                )

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

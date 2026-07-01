"""
SequenceBuilder — 序列化原语

用线性/分支/闭环表达时序流程关系。
替代连线的"时序/流程"语义。
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .annotation import Anchored
    from ..icon import IconPicker
    from ..aesthetic.tokens import DesignTokens


class Swimlane:
    """泳道/层 — 阶段下方的独立行。

    Attributes:
        label: 泳道名称标签。
        items: 泳道内容列表（字符串、Anchored 或 IconPicker 对象）。
        bg_color: 泳道背景色。
        display_mode: 展示模式。
            - "text"（默认）：文字列表
            - "color_block"：色块序列（如情绪曲线）
            - "icon"：图标序列（items 中可传入 IconPicker 对象）
            - "bar"：柱状/进度条
        label_position: 标签在泳道中的位置。
            - "left"（默认）：泳道左侧标注
            - "top_center"：泳道上方居中
            - "top_left"：泳道上方居左
            - "inside"：泳道内部左上角
            - "none"：不显示标签
    """

    def __init__(
        self,
        label: str,
        items: Optional[list[Union[str, "Anchored", "IconPicker"]]] = None,
        bg_color: str = "#F0F2F5",
        display_mode: str = "text",
        label_position: str = "left",
    ) -> None:
        self.label = label
        self.items = items or []
        self.bg_color = bg_color
        self.display_mode = display_mode
        self.label_position = label_position


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
    所有颜色/样式通过 DesignTokens 注入，不再硬编码。
    """

    def __init__(self, tokens: Optional["DesignTokens"] = None) -> None:
        self.tokens = tokens

    @staticmethod
    def _item_str(item: Union[str, "Anchored", "IconPicker"]) -> str:
        """将泳道条目转为 Prompt 字符串。"""
        from ..icon import IconPicker as _IconPicker
        if isinstance(item, _IconPicker):
            return item.build()
        if isinstance(item, str):
            return f"'{item}'"
        # Anchored
        pos_cn = {"below": "下方", "above": "上方", "inside": "内部"}.get(
            getattr(item, "position", "below"), "下方"
        )
        return f"阶段{getattr(item, 'at_step', 0) + 1}{pos_cn}：'{getattr(item, 'text', '')}'"

    def _lane_label(self, lane: "Swimlane") -> str:
        """生成泳道标签前缀。"""
        pos_map = {
            "left": f"，左侧标注'{lane.label}'标签",
            "top_center": f"，上方居中显示'{lane.label}'标签",
            "top_left": f"，上方居左显示'{lane.label}'标签",
            "inside": f"，内部左上角标注'{lane.label}'标签",
            "none": "",
        }
        suffix = pos_map.get(lane.label_position, pos_map["left"])
        return f"{lane.bg_color}背景的泳道{suffix}"

    def _resolve_title(self, title: str) -> str:
        """根据 DesignTokens 生成标题行。"""
        if self.tokens:
            return f"顶部{self.tokens.title_color}{self.tokens.title_size}标题'{title}'，居中显示"
        return f"顶部深蓝灰色大标题'{title}'，居中显示"

    def _resolve_card_bg(self, index: int) -> str:
        """根据 DesignTokens 循环获取阶段卡片背景色。"""
        if self.tokens and self.tokens.card_bg_cycle:
            cycle = self.tokens.card_bg_cycle
            return cycle[index % len(cycle)]
        return "#F0F2F5"

    def _resolve_return_card(self) -> str:
        """根据 DesignTokens 获取返回卡片颜色。"""
        if self.tokens:
            return self.tokens.return_card_color
        return "浅红色"

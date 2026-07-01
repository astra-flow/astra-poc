"""
Chart — 自由组合图表模型。

核心设计原则：
- 图表 = 标题 + 任意行（Row）的自由组合
- 每行可以是泳道行、阶段行、标注行等
- 行之间自动编号、自动对齐
- 图表类型（客户旅程、分支对比等）只是预设约束，不是硬编码

用法::

    chart = Chart(title='客户旅程地图', tokens=t)
    chart.add_swimlane_row(emotion_lane)
    chart.add_phase_row(steps)
    chart.add_swimlane_row(opportunity_lane)
    prompt = chart.build()
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .annotation import Anchored
    from ..icon import IconPicker
    from ..aesthetic.tokens import DesignTokens

from .sequence import Swimlane, Phase, SequenceBuilder


class Row:
    """图表中的一行。

    Attributes:
        row_type: 行类型（"swimlane" / "phase"）。
        data: 行数据（Swimlane 或 Phase 列表）。
        label: 行描述标签（如 "顶部泳道区"、"业务阶段泳道区"）。
    """

    def __init__(
        self,
        row_type: str,
        data: Union[list[Swimlane], list[Phase]],
        label: str = "",
    ) -> None:
        self.row_type = row_type
        self.data = data
        self.label = label


class Chart:
    """自由组合图表 — 标题 + 任意行序列。

    行可以自由增删改排序，每行自动编号、自动对齐。
    """

    def __init__(
        self,
        title: str = "",
        tokens: Optional["DesignTokens"] = None,
        direction: str = "horizontal",
    ) -> None:
        self.title = title
        self.tokens = tokens
        self.direction = direction
        self._rows: list[Row] = []
        self._builder = SequenceBuilder(tokens=tokens)

    # ── 行操作 ──

    def add_swimlane_row(
        self,
        lanes: Union[Swimlane, list[Swimlane]],
        label: str = "",
    ) -> "Chart":
        """添加一个泳道行。

        Args:
            lanes: 一个或多个泳道。
            label: 行描述标签（自动生成，可覆盖）。

        Returns:
            self，支持链式调用。
        """
        if isinstance(lanes, Swimlane):
            lanes = [lanes]
        row_label = label or f"{'、'.join(l.label for l in lanes)}泳道区"
        self._rows.append(Row("swimlane", lanes, row_label))
        return self

    def add_phase_row(
        self,
        phases: Union[Phase, list[Phase]],
        label: str = "",
    ) -> "Chart":
        """添加一个阶段行。

        Args:
            phases: 一个或多个阶段。
            label: 行描述标签（自动生成，可覆盖）。

        Returns:
            self，支持链式调用。
        """
        if isinstance(phases, Phase):
            phases = [phases]
        row_label = label or f"{len(phases)}个阶段泳道区"
        self._rows.append(Row("phase", phases, row_label))
        return self

    def insert_row(self, index: int, row: Row) -> "Chart":
        """在指定位置插入行。"""
        self._rows.insert(index, row)
        return self

    def remove_row(self, index: int) -> "Chart":
        """移除指定行。"""
        if 0 <= index < len(self._rows):
            self._rows.pop(index)
        return self

    def clear_rows(self) -> "Chart":
        """清空所有行。"""
        self._rows.clear()
        return self

    @property
    def rows(self) -> list[Row]:
        """获取所有行的只读视图。"""
        return list(self._rows)

    # ── 构建 ──

    def build(self) -> str:
        """构建完整 Prompt。

        Returns:
            完整的 Prompt 文本片段。
        """
        if not self._rows:
            return ""

        lines = [self._builder._resolve_title(self.title)]
        n_rows = len(self._rows)

        # 确定列数（取阶段行的最大阶段数）
        n_cols = 0
        for row in self._rows:
            if row.row_type == "phase":
                n_cols = max(n_cols, len(row.data))

        # ── 整体布局骨架声明 ──
        row_labels = [f"第{i+1}行{r.label}" for i, r in enumerate(self._rows)]
        lines.append(
            f"整体布局：从上到下分为{n_rows}行泳道——{'、'.join(row_labels)}。"
            + (f"每列纵向对齐，第idx列对应阶段idx（idx=1..{n_cols}）。" if n_cols > 0 else "")
        )

        # ── 逐行输出 ──
        for row_idx, row in enumerate(self._rows):
            row_num = row_idx + 1

            if row.row_type == "swimlane":
                lines.append(
                    f"第{row_num}行（{row.label}，横向通栏，每个泳道横跨所有阶段上方）："
                )
                for lane in row.data:
                    if not isinstance(lane, Swimlane):
                        continue
                    label_prefix = self._builder._lane_label(lane)
                    if lane.display_mode == "color_block":
                        blocks = []
                        for i in range(n_cols):
                            if i < len(lane.items):
                                item = lane.items[i]
                                if isinstance(item, str):
                                    blocks.append(f"阶段{i+1}列：{item}")
                                else:
                                    blocks.append(f"阶段{i+1}列：{getattr(item, 'text', '')}")
                        items_str = "、".join(blocks)
                        lines.append(f"  {label_prefix}（色块序列，每列一个色块）：{items_str}")
                    elif lane.display_mode == "icon":
                        items_str = "、".join(
                            self._builder._item_str(i) for i in lane.items
                        )
                        lines.append(f"  {label_prefix}（图标序列，每列一个图标，纵向对齐到下方阶段）：{items_str}")
                    else:
                        lane_items = [self._builder._item_str(item) for item in lane.items]
                        items_str = "、".join(lane_items)
                        lines.append(f"  {label_prefix}：{items_str}")

            elif row.row_type == "phase":
                direction_cn = "从左到右水平排列" if self.direction == "horizontal" else "从上到下垂直排列"
                lines.append(
                    f"第{row_num}行（{row.label}，{direction_cn}，每个阶段一个容器框，横向通栏横跨所有阶段）："
                )
                for i, phase in enumerate(row.data):
                    if not isinstance(phase, Phase):
                        continue
                    items = "、".join(f"'{c}'" for c in phase.items) if phase.items else ""
                    bg = self._builder._resolve_card_bg(i)
                    base = f"  阶段{i + 1}列（{bg}背景）：'{phase.name}'"
                    if items:
                        base += f" - 包含{items}"
                    lines.append(base)
                    for ann in phase.annotations:
                        lines.append(f"    ↳ 下方标注'{ann}'")

        return "\n".join(lines)

    # ── 便捷预设 ──

    @classmethod
    def customer_journey(
        cls,
        title: str,
        steps: list[Phase],
        emotion_lane: Swimlane,
        opportunity_lane: Optional[Swimlane] = None,
        tokens: Optional["DesignTokens"] = None,
    ) -> "Chart":
        """客户旅程地图预设 — 情绪曲线 + 阶段 + 机会点。"""
        chart = cls(title=title, tokens=tokens)
        chart.add_swimlane_row(emotion_lane, label="顶部泳道区")
        chart.add_phase_row(steps, label="业务阶段泳道区")
        if opportunity_lane:
            chart.add_swimlane_row(opportunity_lane, label="底部泳道区")
        return chart

    @classmethod
    def branch_comparison(
        cls,
        title: str,
        branches: list[tuple[str, list[str]]],
        tokens: Optional["DesignTokens"] = None,
    ) -> "Chart":
        """分支对比预设 — 多行分支对比。"""
        chart = cls(title=title, tokens=tokens, direction="vertical")
        for name, tags in branches:
            phase = Phase(name, items=tags)
            chart.add_phase_row(phase, label=f"'{name}'分支")
        return chart

    @classmethod
    def approval_flow(
        cls,
        title: str,
        steps: list[Phase],
        return_point: int,
        return_label: str = "驳回→返回",
        tokens: Optional["DesignTokens"] = None,
    ) -> "Chart":
        """审批流程预设 — 阶段 + 驳回返回卡片。"""
        chart = cls(title=title, tokens=tokens)
        chart.add_phase_row(steps, label="审批阶段泳道区")
        chart._return_info = (len(steps), return_point, return_label)
        return chart

    # ── 构建 ──

    def build(self) -> str:
        """构建完整 Prompt。

        Returns:
            完整的 Prompt 文本片段。
        """
        if not self._rows:
            return ""

        lines = [self._builder._resolve_title(self.title)]
        n_rows = len(self._rows)

        # 确定列数（取阶段行的最大阶段数）
        n_cols = 0
        for row in self._rows:
            if row.row_type == "phase":
                n_cols = max(n_cols, len(row.data))

        # ── 整体布局骨架声明 ──
        row_labels = [f"第{i+1}行{r.label}" for i, r in enumerate(self._rows)]
        lines.append(
            f"整体布局：从上到下分为{n_rows}行泳道——{'、'.join(row_labels)}。"
            + (f"每列纵向对齐，第idx列对应阶段idx（idx=1..{n_cols}）。" if n_cols > 0 else "")
        )

        # ── 逐行输出 ──
        for row_idx, row in enumerate(self._rows):
            row_num = row_idx + 1

            if row.row_type == "swimlane":
                lines.append(
                    f"第{row_num}行（{row.label}，横向通栏，每个泳道横跨所有阶段上方）："
                )
                for lane in row.data:
                    if not isinstance(lane, Swimlane):
                        continue
                    label_prefix = self._builder._lane_label(lane)
                    if lane.display_mode == "color_block":
                        blocks = []
                        for i in range(n_cols):
                            if i < len(lane.items):
                                item = lane.items[i]
                                if isinstance(item, str):
                                    blocks.append(f"阶段{i+1}列：{item}")
                                else:
                                    blocks.append(f"阶段{i+1}列：{getattr(item, 'text', '')}")
                        items_str = "、".join(blocks)
                        lines.append(f"  {label_prefix}（色块序列，每列一个色块）：{items_str}")
                    elif lane.display_mode == "icon":
                        items_str = "、".join(
                            self._builder._item_str(i) for i in lane.items
                        )
                        lines.append(f"  {label_prefix}（图标序列，每列一个图标，纵向对齐到下方阶段）：{items_str}")
                    else:
                        lane_items = [self._builder._item_str(item) for item in lane.items]
                        items_str = "、".join(lane_items)
                        lines.append(f"  {label_prefix}：{items_str}")

            elif row.row_type == "phase":
                direction_cn = "从左到右水平排列" if self.direction == "horizontal" else "从上到下垂直排列"
                lines.append(
                    f"第{row_num}行（{row.label}，{direction_cn}，每个阶段一个容器框，横向通栏横跨所有阶段）："
                )
                for i, phase in enumerate(row.data):
                    if not isinstance(phase, Phase):
                        continue
                    items = "、".join(f"'{c}'" for c in phase.items) if phase.items else ""
                    bg = self._builder._resolve_card_bg(i)
                    base = f"  阶段{i + 1}列（{bg}背景）：'{phase.name}'"
                    if items:
                        base += f" - 包含{items}"
                    lines.append(base)
                    for ann in phase.annotations:
                        lines.append(f"    ↳ 下方标注'{ann}'")

        # ── 审批流程返回卡片（如有） ──
        if hasattr(self, '_return_info'):
            n, rp, rl = self._return_info
            rc = self._builder._resolve_return_card()
            lines.append(f"在步骤{n}下方有一个{rc}小卡片'{rl}步骤{rp + 1}'")

        return "\n".join(lines)

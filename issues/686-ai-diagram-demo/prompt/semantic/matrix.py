"""
MatrixBuilder — 矩阵化原语

用二维矩阵表达交叉分类关系。
替代连线的"交叉关联"语义。
"""

from __future__ import annotations

from typing import Optional


class MatrixBuilder:
    """矩阵化原语构建器。

    每个方法返回一段 Prompt 文本片段，描述一种矩阵布局。
    """

    @staticmethod
    def quadrant_matrix(
        title: str,
        x_label: str,
        y_label: str,
        quadrants: list[tuple[str, str, str, list[str]]],
    ) -> str:
        """2x2 象限矩阵 — 十字分割 + 四色象限。

        Args:
            title: 标题。
            x_label: 横轴标签。
            y_label: 纵轴标签。
            quadrants: 象限列表，每项为 (位置, 名称, 背景色, 项目列表)。
              位置: tl / tr / bl / br

        Returns:
            Prompt 文本片段。
        """
        pos_map = {
            "tl": "左上",
            "tr": "右上",
            "bl": "左下",
            "br": "右下",
        }
        lines = [f"顶部深蓝灰色大标题'{title}'，居中显示"]
        lines.append(
            f"使用2x2四象限布局，细灰色十字分割线。"
            f"横轴标签'{x_label}'，纵轴标签'{y_label}'。"
        )

        for position, name, bg, items in quadrants:
            pos_cn = pos_map.get(position, position)
            item_str = "、".join(f"'{i}'" for i in items)
            lines.append(
                f"{pos_cn}象限（{bg}背景）：'{name}'"
                f" - 包含{item_str}"
            )

        return "\n".join(lines)

    @staticmethod
    def time_priority(
        title: str,
        time_phases: list[tuple[str, str, list[str]]],
        priority_layers: list[tuple[str, str, list[str]]],
    ) -> str:
        """时间×优先级矩阵 — 用户故事地图布局。

        Args:
            title: 标题。
            time_phases: 时间阶段列表，每项为 (阶段名, 背景色, 故事列表)。
            priority_layers: 优先级分层列表，每项为 (层名, 背景色, 故事列表)。

        Returns:
            Prompt 文本片段。
        """
        lines = [f"顶部深蓝灰色大标题'{title}'，居中显示"]
        lines.append("横向为用户活动阶段（从左到右）：")

        for name, bg, stories in time_phases:
            s = "、".join(f"'{st}'" for st in stories)
            lines.append(f"  {bg}背景：'{name}' - 包含{s}")

        lines.append("纵向为优先级分层（从上到下）：")
        for name, bg, stories in priority_layers:
            s = "、".join(f"'{st}'" for st in stories)
            lines.append(f"  {bg}背景：'{name}' - 包含{s}")

        return "\n".join(lines)

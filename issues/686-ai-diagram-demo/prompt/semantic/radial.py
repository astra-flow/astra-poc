"""
RadialBuilder — 辐射化原语

用中心辐射/多轴表达关系。
替代连线的"中心-外围"关系语义。
"""

from __future__ import annotations

from typing import Optional


class RadialBuilder:
    """辐射化原语构建器。

    每个方法返回一段 Prompt 文本片段，描述一种辐射布局。
    """

    @staticmethod
    def center_radial(
        title: str,
        center: str,
        center_color: str = "#4A6FA5",
        branches: Optional[list[tuple[str, list[str]]]] = None,
        bg_color: str = "#F0F2F5",
    ) -> str:
        """中心辐射 — 中心圆形 + 辐射分支 + 嵌套子节点。

        Args:
            title: 标题。
            center: 中心节点名称。
            center_color: 中心节点颜色。
            branches: 分支列表，每项为 (分支名, 子节点列表)。
            bg_color: 分支容器背景色。

        Returns:
            Prompt 文本片段。
        """
        lines = [f"顶部深蓝灰色大标题'{title}'，居中显示"]
        lines.append(
            f"中心'{center}'（{center_color}色圆形），"
            f"周围辐射{len(branches)}个分支："
        )

        for name, children in branches or []:
            items = "、".join(f"'{c}'" for c in children)
            lines.append(
                f"  {bg_color}背景的分支'{name}' - 包含{items}"
            )

        return "\n".join(lines)

    @staticmethod
    def multi_axis(
        title: str,
        center: str,
        axes: list[tuple[str, str, float]],
        axis_color: str = "#8E8E93",
    ) -> str:
        """多轴辐射 — 从中心向外延伸的多条轴线（雷达图/蛛网图）。

        Args:
            title: 标题。
            center: 中心标签。
            axes: 轴列表，每项为 (轴名, 当前值, 目标值)。
            axis_color: 轴线颜色。

        Returns:
            Prompt 文本片段。
        """
        lines = [f"顶部深蓝灰色大标题'{title}'，居中显示"]
        lines.append(
            f"中心'{center}'，从中心向外辐射{len(axes)}条{axis_color}色轴线"
        )
        lines.append("每条轴线末端标注维度名称和得分：")

        for name, current, target in axes:
            lines.append(f"  '{name}'：当前{current}，目标{target}")

        lines.append("同心圆刻度环从内到外递增，当前状态用半透明色块填充")

        return "\n".join(lines)

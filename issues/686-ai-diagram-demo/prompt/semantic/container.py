"""
ContainerBuilder — 容器化原语

用容器框/泳道/象限/环绕表达分组归属关系。
替代连线的"归属关系"语义。
"""

from __future__ import annotations

from typing import Optional


class ContainerBuilder:
    """容器化原语构建器。

    每个方法返回一段 Prompt 文本片段，描述一种容器布局。
    """

    @staticmethod
    def layer(
        name: str,
        components: list[str],
        bg_color: str = "#F0F2F5",
        border_color: str = "#D0D5DD",
        style: str = "horizontal",
    ) -> str:
        """分层容器 — 从上到下垂直排列的层级。

        Args:
            name: 层级名称。
            components: 该层包含的组件列表。
            bg_color: 容器背景色。
            border_color: 容器边框色。
            style: 组件排列方向（horizontal / vertical）。

        Returns:
            Prompt 文本片段。
        """
        items = "、".join(f"'{c}'" for c in components)
        direction = "水平并排" if style == "horizontal" else "垂直排列"
        return (
            f"{bg_color}背景、{border_color}边框的圆角容器框'{name}'"
            f"：包含{len(components)}个组件{direction}：{items}"
        )

    @staticmethod
    def swimlane(
        name: str,
        activities: list[str],
        bg_color: str = "#F0F2F5",
        label: str = "",
    ) -> str:
        """泳道容器 — 横向泳道，左侧有标签。

        Args:
            name: 泳道名称。
            activities: 该泳道包含的活动列表。
            bg_color: 泳道背景色。
            label: 左侧标签文字（可选）。

        Returns:
            Prompt 文本片段。
        """
        items = "、".join(f"'{a}'" for a in activities)
        label_part = f"，左侧标注'{label}'标签" if label else ""
        return (
            f"{bg_color}背景的泳道容器'{name}'{label_part}"
            f"：包含{len(activities)}个活动：{items}"
        )

    @staticmethod
    def quadrant(
        position: str,
        name: str,
        items: list[str],
        bg_color: str = "#D4E2D4",
    ) -> str:
        """象限容器 — 2x2 矩阵中的一个象限。

        Args:
            position: 象限位置（tl / tr / bl / br）。
            name: 象限名称。
            items: 象限包含的项目列表。
            bg_color: 象限背景色。

        Returns:
            Prompt 文本片段。
        """
        pos_map = {
            "tl": "左上",
            "tr": "右上",
            "bl": "左下",
            "br": "右下",
        }
        pos_cn = pos_map.get(position, position)
        item_str = "、".join(f"'{i}'" for i in items)
        return (
            f"{pos_cn}象限（{bg_color}背景）：'{name}'"
            f" - 包含{item_str}"
        )

    @staticmethod
    def surround(
        center: str,
        satellites: list[str],
        center_color: str = "#4A6FA5",
        satellite_color: str = "#F0F2F5",
    ) -> str:
        """环绕容器 — 中心实体 + 环绕外部实体。

        Args:
            center: 中心实体名称。
            satellites: 环绕实体列表。
            center_color: 中心实体颜色。
            satellite_color: 环绕实体背景色。

        Returns:
            Prompt 文本片段。
        """
        sats = "、".join(f"'{s}'" for s in satellites)
        return (
            f"中心'{center}'（{center_color}色），"
            f"周围环绕{satellite_color}背景的{sats}"
        )

    @staticmethod
    def group(
        name: str,
        children: list[str],
        bg_color: str = "#F0F2F5",
        border_color: str = "#D0D5DD",
    ) -> str:
        """自由分组容器 — 通用的分组容器。

        Args:
            name: 分组名称。
            children: 子元素列表。
            bg_color: 容器背景色。
            border_color: 容器边框色。

        Returns:
            Prompt 文本片段。
        """
        items = "、".join(f"'{c}'" for c in children)
        return (
            f"{bg_color}背景、{border_color}边框的圆角容器框'{name}'"
            f"：包含{len(children)}项：{items}"
        )

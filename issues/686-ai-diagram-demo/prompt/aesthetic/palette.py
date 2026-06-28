"""
ColorPalette — 跨图通用的配色系统。

从现有 ``batch/design/tokens.py`` 提取进化，保持向后兼容。
"""

from __future__ import annotations

from typing import Optional


class ColorPalette:
    """跨图通用的配色系统。

    每套配色体系包含背景色、边框色、文字色等设计 Token。
    输出为 Prompt 文本片段，可直接拼接到最终 Prompt。
    """

    # ── 莫兰迪高级色系（通用） ──
    MORANDI = {
        "sage_green": "#D4E2D4",
        "mist_blue": "#D4DCE8",
        "beige": "#E8E0D4",
        "dusty_pink": "#E8D4D4",
        "light_blue_gray": "#F0F2F5",
        "light_green_gray": "#EFF5F0",
        "light_orange_gray": "#F5F2EF",
        "light_purple_gray": "#F2EFF5",
    }

    # ── Slate 主题色系（公众号风格） ──
    SLATE = {
        "primary": "#4A6FA5",
        "dark": "#2C3E50",
        "warm_gray": "#8E8E93",
        "bg": "#F2F2F7",
        "accent": "#D4A04A",
        "green": "#7A9E7E",
    }

    # ── 角色主题色系 ──
    ROLE = {
        "pm": "#4A6FA5",
        "pm_light": "#E8EDF5",
        "pm_border": "#3A5A8A",
        "project": "#7A9E7E",
        "project_light": "#EDF5EE",
        "architect": "#D4A04A",
        "architect_light": "#F5F0E8",
        "coach": "#8E7EA5",
        "coach_light": "#F0EDF5",
    }

    # ── 分支类型色系 ──
    BRANCH = {
        "main": "#4A6FA5",
        "feature": "#8E8E93",
        "release": "#D4A04A",
        "hotfix": "#C0392B",
        "develop": "#7A9E7E",
    }

    # ── 阶段/等级色系 ──
    STAGE = {
        "level_1": "#8E8E93",
        "level_2": "#4A6FA5",
        "level_3": "#7A9E7E",
        "level_4": "#D4A04A",
        "alpha": "#4A6FA5",
        "beta": "#7A9E7E",
        "rc": "#D4A04A",
        "release": "#C0392B",
    }

    # ── 事件风暴色系 ──
    EVENT = {
        "command": "#F5E8D0",
        "event": "#D0D8F5",
        "aggregate": "#D0F0D0",
        "external": "#E8E8E8",
    }

    @staticmethod
    def describe(palette: dict, name: str = "莫兰迪") -> str:
        """输出配色体系的 Prompt 描述。

        Args:
            palette: 配色字典。
            name: 配色名称。

        Returns:
            Prompt 文本片段。
        """
        return f"使用{name}色系，色调统一，色彩和谐，低饱和度高级灰配色"

    @staticmethod
    def background(color: str) -> str:
        """输出背景色描述。

        Args:
            color: 色号（如 ``#F0F2F5``）。

        Returns:
            Prompt 文本片段。
        """
        return f"{color}背景"

    @staticmethod
    def border(color: str) -> str:
        """输出边框色描述。

        Args:
            color: 色号。

        Returns:
            Prompt 文本片段。
        """
        return f"{color}色边框"

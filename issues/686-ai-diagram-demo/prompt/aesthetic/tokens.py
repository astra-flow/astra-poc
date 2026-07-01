"""
DesignTokens — 设计 Token 系统。

语义 Builder 的颜色/样式唯一来源。
所有硬编码颜色值集中管理，支持与 StylePreset / ColorPalette 联动。
"""

from __future__ import annotations

from typing import Optional


class DesignTokens:
    """设计 Token 系统 — 语义 Builder 的颜色/样式唯一来源。

    所有语义 Builder 不再硬编码任何颜色值，全部通过 DesignTokens 注入。
    支持与 StylePreset / ColorPalette 联动，确保美学风格与语义颜色一致。

    Attributes:
        title_color: 标题颜色描述（如 "深蓝灰色"、"#2C3E50"）。
        title_size: 标题尺寸描述（如 "大"、"中"）。
        card_bg_cycle: 阶段卡片背景色循环列表。
        return_card_color: 闭环返回卡片颜色（如 "浅红色"）。
        lane_bg: 泳道默认背景色。
        accent: 强调色。
        text_primary: 主要文字色。
        text_secondary: 次要文字色。
        border: 边框色。
    """

    def __init__(
        self,
        title_color: str = "深蓝灰色",
        title_size: str = "大",
        card_bg_cycle: Optional[list[str]] = None,
        return_card_color: str = "浅红色",
        lane_bg: str = "#F0F2F5",
        accent: str = "#D4A04A",
        text_primary: str = "#333333",
        text_secondary: str = "#8E8E93",
        border: str = "#D0D5DD",
    ) -> None:
        self.title_color = title_color
        self.title_size = title_size
        self.card_bg_cycle = card_bg_cycle or ["#F0F2F5"]
        self.return_card_color = return_card_color
        self.lane_bg = lane_bg
        self.accent = accent
        self.text_primary = text_primary
        self.text_secondary = text_secondary
        self.border = border

    @classmethod
    def from_palette(cls, palette: dict, **overrides) -> "DesignTokens":
        """从 ColorPalette 的配色字典创建 DesignTokens。

        Args:
            palette: ColorPalette 中的配色字典（如 MORANDI、SLATE）。
            **overrides: 手动覆盖的 Token 值。

        Returns:
            DesignTokens 实例。
        """
        tokens = cls(**overrides)
        if "dark" in palette:
            tokens.title_color = palette["dark"]
        if "bg" in palette:
            tokens.lane_bg = palette["bg"]
            tokens.card_bg_cycle = [palette["bg"]]
        if "accent" in palette:
            tokens.accent = palette["accent"]
        if "warm_gray" in palette:
            tokens.text_secondary = palette["warm_gray"]
        if "primary" in palette:
            tokens.title_color = palette["primary"]
        return tokens

    @classmethod
    def from_style(cls, style: str, **overrides) -> "DesignTokens":
        """从风格名称创建 DesignTokens，与 StylePreset 保持一致。

        Args:
            style: 风格名称（consulting / wechat / minimal / dark / brand）。
            **overrides: 手动覆盖的 Token 值。

        Returns:
            DesignTokens 实例。
        """
        style_map: dict[str, dict[str, str | list[str]]] = {
            "consulting": {
                "title_color": "深蓝灰色",
                "title_size": "大",
                "card_bg_cycle": [
                    "#F0F2F5", "#EFF5F0", "#F5F2EF", "#F2EFF5",
                ],
                "return_card_color": "浅红色",
                "lane_bg": "#F0F2F5",
                "accent": "#D4A04A",
                "text_primary": "#333333",
                "text_secondary": "#8E8E93",
                "border": "#D0D5DD",
            },
            "wechat": {
                "title_color": "#2C3E50",
                "title_size": "大",
                "card_bg_cycle": ["#F2F2F7"],
                "return_card_color": "#F5E8E8",
                "lane_bg": "#F2F2F7",
                "accent": "#D4A04A",
                "text_primary": "#333333",
                "text_secondary": "#8E8E93",
                "border": "#D0D5DD",
            },
            "minimal": {
                "title_color": "#333333",
                "title_size": "中",
                "card_bg_cycle": ["#F5F5F5"],
                "return_card_color": "#E8E8E8",
                "lane_bg": "#F5F5F5",
                "accent": "#666666",
                "text_primary": "#333333",
                "text_secondary": "#999999",
                "border": "#CCCCCC",
            },
            "dark": {
                "title_color": "#FFFFFF",
                "title_size": "大",
                "card_bg_cycle": ["#1C1C1E", "#2C2C2E"],
                "return_card_color": "#3D1F1F",
                "lane_bg": "#1C1C1E",
                "accent": "#4A9EFF",
                "text_primary": "#FFFFFF",
                "text_secondary": "#8E8E93",
                "border": "#38383A",
            },
        }
        base = dict(style_map.get(style, style_map["consulting"]))
        base.update(overrides)  # type: ignore[arg-type]
        return cls(**base)  # type: ignore[arg-type]

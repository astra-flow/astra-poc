"""
StylePreset — 风格预设系统。

覆盖六大美学维度：色彩、构图、光影、质感、细节、风格。
每种风格预设输出完整的 Prompt 美学描述片段。
"""

from __future__ import annotations

from typing import Optional


class StylePreset:
    """风格预设。

    每种预设输出一段完整的 Prompt 美学描述，可直接拼接到最终 Prompt。
    """

    @staticmethod
    def consulting() -> str:
        """咨询公司风格 — 专业、简洁、高级灰。

        Returns:
            Prompt 文本片段。
        """
        return (
            "纯白背景，咨询公司风格。"
            "色调统一，色彩和谐，视觉层次清晰，信息层级分明。"
            "专业图表设计，电影级光影，构图精美，"
            "层次感强，8K超清，细节丰富，质感细腻，工作室质量"
        )

    @staticmethod
    def wechat() -> str:
        """公众号文章风格 — 柔和、舒适、阅读友好。

        Returns:
            Prompt 文本片段。
        """
        return (
            "浅灰背景，公众号文章风格。"
            "柔和色调，舒适阅读体验，视觉层次分明。"
            "使用Slate色系，石板蓝主色，深蓝灰文字，暖灰辅助。"
            "卡片式布局，圆角柔和，阴影细腻"
        )

    @staticmethod
    def minimal() -> str:
        """极简风格 — 干净、留白、无装饰。

        Returns:
            Prompt 文本片段。
        """
        return (
            "纯白背景，极简风格。"
            "最大留白，最小装饰。"
            "仅使用黑白灰三色，无彩色干扰。"
            "细边框，无阴影，无渐变。"
            "文字仅使用一种字重，无装饰元素"
        )

    @staticmethod
    def dark() -> str:
        """深色风格 — 深色背景、高对比。

        Returns:
            Prompt 文本片段。
        """
        return (
            "深色背景，科技感风格。"
            "深蓝灰底色，白色文字，高对比度。"
            "霓虹蓝和琥珀色作为强调色。"
            "发光边框，微光晕效果，科技感视觉层次"
        )

    @staticmethod
    def brand(
        primary: str = "#4A6FA5",
        bg: str = "#FFFFFF",
        accent: str = "#D4A04A",
    ) -> str:
        """品牌自定义风格。

        Args:
            primary: 主色。
            bg: 背景色。
            accent: 强调色。

        Returns:
            Prompt 文本片段。
        """
        return (
            f"{bg}背景，品牌定制风格。"
            f"使用{primary}作为主色，{accent}作为强调色。"
            "色调统一，色彩和谐，视觉层次清晰。"
            "专业图表设计，细节丰富，质感细腻"
        )

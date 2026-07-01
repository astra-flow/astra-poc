"""
IconPicker — 图标选择器，独立文件避免循环导入。

语义选型 + 美学定风格，支持普通图标、表情符号和文字描述。
"""

from __future__ import annotations


class IconPicker:
    """图标选择器 — 语义选型 + 美学定风格。

    Attributes:
        type_name: 图标类型（如 database, server, user, gear, cloud）
                    或表情符号（如 "emoji:😊"）
                    或文字描述（如 "text:笑脸"）。
        style: 图标风格（line / fill / dual / emoji / text）。
        size: 图标尺寸（small / medium / large）。
        color: 图标颜色（色号）。
        label: 图标附带文字标签（如 "高"、"低"）。
    """

    def __init__(
        self,
        type_name: str,
        style: str = "line",
        size: str = "small",
        color: str = "#8E8E93",
        label: str = "",
    ) -> None:
        self.type_name = type_name
        self.style = style
        self.size = size
        self.color = color
        self.label = label

    @classmethod
    def emoji(cls, emoji_char: str, label: str = "", color: str = "#8E8E93") -> "IconPicker":
        """创建表情符号图标选择器。

        Args:
            emoji_char: 表情符号字符（如 "😊"、"😐"、"😢"）。
            label: 附带文字标签（如 "高"、"中"、"低"）。
            color: 图标颜色。

        Returns:
            IconPicker 实例。
        """
        return cls(
            type_name=f"emoji:{emoji_char}",
            style="emoji",
            color=color,
            label=label,
        )

    @classmethod
    def text(cls, description: str, label: str = "", color: str = "#8E8E93") -> "IconPicker":
        """创建文字描述图标选择器（不依赖 emoji 字符）。

        适用于模型不支持 emoji 渲染、或需要更精确语义描述的场景。
        输出格式为 ``[描述]标签``，如 ``[笑脸]高``。

        Args:
            description: 文字描述（如 "笑脸"、"哭脸"、"星星"、"对勾"）。
            label: 附带文字标签（如 "高"、"中"、"低"）。
            color: 图标颜色。

        Returns:
            IconPicker 实例。
        """
        return cls(
            type_name=f"text:{description}",
            style="text",
            color=color,
            label=label,
        )

    def build(self) -> str:
        """输出图标描述的 Prompt 片段。"""
        if self.style == "emoji" and self.type_name.startswith("emoji:"):
            emoji = self.type_name.split(":", 1)[1]
            if self.label:
                return f"{emoji}{self.label}"
            return f"{emoji}表情"

        if self.style == "text" and self.type_name.startswith("text:"):
            desc = self.type_name.split(":", 1)[1]
            if self.label:
                return f"[{desc}]{self.label}"
            return f"[{desc}]"

        style_map = {"line": "线性", "fill": "填充", "dual": "双色"}
        size_map = {"small": "小型", "medium": "中型", "large": "大型"}
        base = (
            f"{size_map.get(self.size, self.size)}"
            f"{style_map.get(self.style, self.style)}"
            f"图标'{self.type_name}'，{self.color}色"
        )
        if self.label:
            base += f"，标签'{self.label}'"
        return base

    def __str__(self) -> str:
        return self.build()

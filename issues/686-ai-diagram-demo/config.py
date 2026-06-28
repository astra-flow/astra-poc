"""Issue #686 图片生成 POC 专属配置。"""

from __future__ import annotations

from dataclasses import dataclass

from poc.base.config import PocConfig


@dataclass(frozen=True)
class ImageGenConfig(PocConfig):
    """AI 绘图大模型 POC 配置。

    Attributes:
        api_key: ARK API 密钥。
        base_url: ARK API 基础 URL。
        model: 图片生成模型名称。
        vision_api_key: 视觉 LLM API 密钥（可选）。
        vision_model: 视觉 LLM 模型名称（可选）。
        vision_base_url: 视觉 LLM API 基础 URL（可选）。
    """

    api_key: str = ""
    base_url: str = "https://ark.cn-beijing.volces.com/api/plan/v3"
    model: str = "doubao-seedream-5.0-lite"
    vision_api_key: str = ""
    vision_model: str = "doubao-seed-2.0-pro"
    vision_base_url: str = ""

    def __repr__(self) -> str:
        """返回配置摘要，遮蔽敏感密钥。"""
        return (
            f"ImageGenConfig(issue={self.issue_number}, "
            f"model={self.model}, "
            f"api_key={'***' if self.api_key else '(unset)'}, "
            f"vision_api_key={'***' if self.vision_api_key else '(unset)'})"
        )

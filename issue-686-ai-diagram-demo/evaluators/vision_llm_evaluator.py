"""视觉 LLM 质量评估器。

使用视觉大模型对图片进行 4 维度/10 分制系统性质量评估。
"""

from __future__ import annotations

import base64
import io
import json
import re
import time
from pathlib import Path

import requests
from PIL import Image
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from issue_686_ai_diagram_demo.config import ImageGenConfig

_VISION_SESSION = requests.Session()
_VISION_RETRY = Retry(
    total=2,
    backoff_factor=3,
    allowed_methods=["POST"],
    status_forcelist=[429, 500, 502, 503, 504],
)
_VISION_SESSION.mount("https://", HTTPAdapter(max_retries=_VISION_RETRY))
_VISION_SESSION.mount("http://", HTTPAdapter(max_retries=_VISION_RETRY))

_EVAL_PROMPT = """你是一名专业的 AIGC 图表质量评测专家，专精于技术架构图、流程图、概念图等结构化图表的视觉质量评估。

请仔细分析这张图表，输出两部分内容：

## 第一部分：结构化评分（JSON）

必须严格按以下 JSON 格式输出，供程序自动处理：

{
  "scores": {
    "semantic": N,
    "image_quality": N,
    "aesthetic": N,
    "compliance": N
  },
  "overall": N,
  "verdict": "pass|review|fail",
  "issues": [
    {"severity": "critical|major|minor", "dimension": "图文语义/图像质量/美学构图/合规", "description": "具体问题", "suggestion": "如何修复"}
  ],
  "strengths": ["优点1", "优点2"],
  "improvement_actions": [
    {"action": "增加边框对比度", "expected_impact": "高|中|低", "dimension": "image_quality"}
  ]
}

## 第二部分：Markdown 评估报告（供人阅读）

### 综合评分
- 加权总分：X.X | 等级：优秀/良好/合格/不合格

### 核心缺陷
- {问题1}

### 优化建议
- {建议1}
"""


class VisionLLMSingleEvaluator:
    """基于视觉大模型的质量评估器。

    对图片进行 4 维度（语义/画质/美学/合规）评分，输出结构化 JSON 报告。
    """

    def __init__(self, config: ImageGenConfig) -> None:
        self._config = config

    def evaluate(self, image_path: str) -> dict:
        """对单张图片执行视觉 LLM 评估。

        Args:
            image_path: 图片文件路径。

        Returns:
            包含 verdict/overall/scores/issues 的评估结果。
        """
        if not self._config.vision_api_key:
            return {"status": "skipped", "reason": "vision_api_key not set"}

        img = Image.open(image_path)
        max_dim = 1024
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        payload = {
            "model": self._config.vision_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": _EVAL_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"},
                        },
                    ],
                }
            ],
            "max_tokens": 4096,
        }

        try:
            resp = _VISION_SESSION.post(
                f"{self._config.vision_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._config.vision_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=(10, 180),
            )
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

        if resp.status_code != 200:
            return {"status": "error", "code": resp.status_code, "message": resp.text[:200]}

        content = resp.json()["choices"][0]["message"]["content"]
        return self._parse_response(content)

    def _parse_response(self, content: str) -> dict:
        """解析 LLM 返回的 JSON + Markdown 混合内容。"""
        result: dict = {}
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                result.update(parsed)
            except json.JSONDecodeError:
                fallback = re.search(r"\{.*\}", content, re.DOTALL)
                if fallback:
                    try:
                        parsed = json.loads(fallback.group())
                        result.update(parsed)
                    except json.JSONDecodeError:
                        result["json_parse_error"] = True
        else:
            fallback = re.search(r"\{.*\}", content, re.DOTALL)
            if fallback:
                try:
                    parsed = json.loads(fallback.group())
                    result.update(parsed)
                except json.JSONDecodeError:
                    result["json_parse_error"] = True

        nl_report = re.sub(r"```json\s*\{.*?\}\s*```", "", content, flags=re.DOTALL)
        nl_report = nl_report.strip()
        nl_report = re.sub(r"```\w*\s*", "", nl_report).strip()
        if nl_report:
            result["nl_report"] = nl_report

        if not result:
            result["status"] = "parse_failed"
            result["raw"] = content[:500]

        return result

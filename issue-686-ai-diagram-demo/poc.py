"""Issue #686 — AI 绘图大模型效果验证 POC。

继承 PocBase[ImageGenConfig]，实现图片生成、质量评估和报告输出。
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from poc.base.evaluator import CompositeEvaluator
from poc.base.poc_base import PocBase
from poc.base.result import BatchResult, PocResult

from config import ImageGenConfig
from evaluators.pillow_evaluator import PillowSingleEvaluator
from evaluators.vision_llm_evaluator import VisionLLMSingleEvaluator

# ── Socket 级全局超时兜底 ──
_DEFAULT_TIMEOUT: float = 180.0
socket.setdefaulttimeout(_DEFAULT_TIMEOUT)

# ── 带重试的 HTTP Session ──
_SESSION = requests.Session()
_SESSION.mount(
    "https://",
    HTTPAdapter(
        max_retries=Retry(
            total=3,
            backoff_factor=2,
            allowed_methods=["GET", "POST"],
            status_forcelist=[429, 500, 502, 503, 504],
        )
    ),
)
_SESSION.mount(
    "http://",
    HTTPAdapter(
        max_retries=Retry(
            total=3,
            backoff_factor=2,
            allowed_methods=["GET", "POST"],
            status_forcelist=[429, 500, 502, 503, 504],
        )
    ),
)


class PocImageGen(PocBase[ImageGenConfig]):
    """Issue #686: AI 绘图大模型效果验证 POC。"""

    # ── 工厂方法 ──

    @classmethod
    def from_issue(cls, issue_number: int) -> PocImageGen:
        """根据 Issue 编号创建 PocImageGen 实例。

        从环境变量或默认值读取 API 配置。
        """
        config = ImageGenConfig(
            issue_number=issue_number,
            api_key=os.getenv("ARK_API_KEY", ""),
            base_url=os.getenv(
                "ARK_BASE_URL",
                "https://ark.cn-beijing.volces.com/api/plan/v3",
            ),
            model=os.getenv("ARK_MODEL", "doubao-seedream-5.0-lite"),
            vision_api_key=os.getenv("VISION_API_KEY", ""),
            vision_model=os.getenv("VISION_MODEL", "doubao-seed-2.0-pro"),
            vision_base_url=os.getenv(
                "VISION_BASE_URL",
                "https://ark.cn-beijing.volces.com/api/plan/v3",
            ),
            output_dir=str(Path(__file__).resolve().parent / "output"),
            log_dir=str(Path(__file__).resolve().parent / "logs"),
        )
        return cls(config)

    # ── 生命周期 ──

    def setup(self) -> None:
        """校验 API 凭证和输出目录。"""
        if not self.config.api_key:
            raise RuntimeError(
                "ARK_API_KEY 未配置。请设置环境变量 ARK_API_KEY。"
            )
        self.config.output_path.mkdir(parents=True, exist_ok=True)
        self.config.log_path.mkdir(parents=True, exist_ok=True)

    def run(self) -> PocResult:
        """遍历所有批次，调用 ARK API 生成图片。"""
        from batches.batch_1 import get_batch_1
        from batches.batch_2 import get_batch_2
        from batches.batch_3 import get_batch_3
        from batches.batch_4 import get_batch_4
        from batches.batch_5 import get_batch_5

        batches: dict[str, tuple[str, list]] = {
            "batch_1": ("P0 图表", get_batch_1()),
            "batch_2": ("P1 图表", get_batch_2()),
            "batch_3": ("P2 图表", get_batch_3()),
            "batch_4": ("稳定性重测", get_batch_4()),
            "batch_5": ("多轮稳定性测试", get_batch_5()),
        }

        results: list[BatchResult] = []
        for batch_id, (desc, tests) in batches.items():
            print(f"\n{'#' * 60}", flush=True)
            print(f"# 批次 {batch_id}: {desc}", flush=True)
            print(f"{'#' * 60}", flush=True)
            batch_result = self._run_batch(tests, batch_id)
            results.append(batch_result)

        return PocResult(
            success=all(r.success for r in results),
            batches=results,
        )

    def evaluate(self, result: PocResult) -> dict:
        """对生成图片执行 Pillow + 视觉 LLM 评估。

        Args:
            result: run() 返回的执行结果。

        Returns:
            评估报告字典。
        """
        artifacts = [
            a for b in result.batches for a in b.artifacts
        ]
        if not artifacts:
            return {"evaluations": [], "note": "无产出物可评估"}

        evaluators = [PillowSingleEvaluator()]
        if self.config.vision_api_key:
            evaluators.append(
                VisionLLMSingleEvaluator(self.config)
            )

        composite = CompositeEvaluator(evaluators)
        evaluations = composite.evaluate_all(artifacts)
        return {"evaluations": evaluations}

    def report(self, result: PocResult, evaluation: dict) -> None:
        """输出可读报告 + JSON 报告文件。

        Args:
            result: run() 返回的执行结果。
            evaluation: evaluate() 返回的评估报告。
        """
        evaluations = evaluation.get("evaluations", [])
        if not evaluations:
            print("\n  (无评估数据)")
            return

        # 汇总表格
        print(f"\n{'─' * 60}")
        print(f"📋 评估汇总 ({len(evaluations)} 项)")
        print(f"{'─' * 60}")
        for item in evaluations:
            file_name = item.get("artifact", "?")
            pillow = item.get("PillowSingleEvaluator", {})
            sharpness = pillow.get("sharpness_score", "N/A")
            width = pillow.get("width", "?")
            height = pillow.get("height", "?")
            line = f"  {file_name}: {width}x{height} | 清晰度 {sharpness}"

            vision = item.get("VisionLLMSingleEvaluator", {})
            if vision.get("verdict"):
                v_mark = {"pass": "✅", "review": "⚠️", "fail": "❌"}
                line += (
                    f" | {v_mark.get(vision['verdict'], '❓')} "
                    f"{vision.get('overall', '?')}/10"
                )
                issues = vision.get("issues", [])
                n_c = sum(
                    1 for i in issues if i.get("severity") == "critical"
                )
                n_m = sum(
                    1 for i in issues if i.get("severity") == "major"
                )
                if n_c:
                    line += f" | 🔴{n_c}严重"
                if n_m:
                    line += f" | 🟡{n_m}主要"

            print(line)

        # 保存 JSON 报告
        json_path = self.config.output_path / "evaluation_report.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(evaluations, indent=2, ensure_ascii=False)
        )
        print(f"\n✅ JSON 报告已保存: {json_path}")

    # ── 内部方法 ──

    def _run_batch(
        self, tests: list[dict], batch_id: str
    ) -> BatchResult:
        """运行单个批次的所有测试。

        Args:
            tests: 测试列表。
            batch_id: 批次名称。

        Returns:
            单批次的执行结果。
        """
        total = sum(
            t.get("rounds", 1) * (1 + len(t.get("variants", [])))
            for t in tests
        )
        done = 0
        artifacts: list[str] = []

        for test in tests:
            rounds = test.get("rounds", 1)
            for r in range(rounds):
                prompt = test["prompt"]
                name = test["name"]
                rname = f"{name}_r{r + 1}" if rounds > 1 else name

                if "variants" in test:
                    for j, variant in enumerate(test["variants"]):
                        done += 1
                        vname = f"{rname}_v{j + 1}"
                        print(
                            f"\n>>> [{done}/{total}] 生成 {vname}",
                            flush=True,
                        )
                        img_path = self._generate_image(
                            prompt=variant,
                            name=vname,
                            batch=batch_id,
                        )
                        if img_path:
                            artifacts.append(img_path)
                        time.sleep(1)
                else:
                    done += 1
                    print(
                        f"\n>>> [{done}/{total}] 生成 {rname}",
                        flush=True,
                    )
                    img_path = self._generate_image(
                        prompt=prompt, name=rname, batch=batch_id
                    )
                    if img_path:
                        artifacts.append(img_path)
                    time.sleep(1)

        print(
            f"\n✅ 批次 {batch_id} 完成！"
            f"图片保存在 {self.config.output_path / batch_id}/",
            flush=True,
        )
        return BatchResult(
            batch_name=batch_id,
            success=len(artifacts) > 0,
            artifacts=artifacts,
        )

    def _generate_image(
        self,
        prompt: str,
        name: str,
        batch: str = "batch_1",
        size: str = "2K",
    ) -> str | None:
        """调用 ARK API 生成单张图片。

        Args:
            prompt: 图片生成提示词。
            name: 图片名称（不含路径和扩展名）。
            batch: 批次名称。
            size: 图片尺寸（如 "2K"、"1024x1024"）。

        Returns:
            保存的图片路径，失败时返回 None。
        """
        output_dir = self.config.batch_output(batch)
        output_dir.mkdir(parents=True, exist_ok=True)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "size": size,
            "output_format": "png",
            "watermark": False,
        }

        print(f"\n{'=' * 60}", flush=True)
        print(f"[{batch}] {name}", flush=True)
        print(f"提示词: {prompt[:100]}...", flush=True)
        print(f"{'=' * 60}", flush=True)

        try:
            resp = _SESSION.post(
                f"{self.config.base_url}/images/generations",
                headers=headers,
                json=payload,
                timeout=(10, 120),
            )
            api_ok = resp.status_code == 200
            self.tracker.record(
                "generate_api",
                api_ok,
                f"{batch}/{name} status={resp.status_code}",
            )
        except requests.Timeout:
            print("  ⏰ API 超时，跳过", flush=True)
            self.tracker.record(
                "generate_api", False, f"{batch}/{name} timeout"
            )
            return None
        except (requests.ConnectionError, socket.timeout) as exc:
            print(f"  ⏰ 连接异常: {exc}", flush=True)
            self.tracker.record(
                "generate_api", False, f"{batch}/{name} conn_err"
            )
            return None
        except Exception as exc:
            print(f"  ❌ API 请求异常: {exc}", flush=True)
            self.tracker.record(
                "generate_api", False, f"{batch}/{name} {exc}"
            )
            return None

        print(f"状态码: {resp.status_code}", flush=True)

        if resp.status_code != 200:
            print(f"  ❌ 错误: {resp.text[:300]}", flush=True)
            self.tracker.record(
                "generate_api",
                False,
                f"{batch}/{name} {resp.status_code}",
            )
            return None

        data = resp.json()
        if "data" not in data:
            return None

        saved_path: str | None = None
        for item in data["data"]:
            if "url" not in item:
                continue
            img_url = item["url"]
            dl_ok = False
            for attempt in range(3):
                try:
                    img_resp = _SESSION.get(img_url, timeout=(5, 30))
                    if img_resp.status_code == 200:
                        dl_ok = True
                        break
                except Exception as exc:
                    if attempt < 2:
                        wait = 2**attempt
                        print(
                            f"  ⏰ 下载失败(第{attempt+1}次)，"
                            f"{wait}s 后重试: {exc}",
                            flush=True,
                        )
                        time.sleep(wait)
                    else:
                        print(
                            f"  ❌ 下载失败(已重试3次): {exc}",
                            flush=True,
                        )
            self.tracker.record("download_image", dl_ok, f"{batch}/{name}")
            if dl_ok:
                ts = time.strftime("%Y%m%d_%H%M%S")
                fname = str(output_dir / f"{name}_{ts}.png")
                with open(fname, "wb") as f:
                    f.write(img_resp.content)
                print(f"  ✅ 已保存: {fname}", flush=True)
                saved_path = fname

        return saved_path

    def clean(self) -> None:
        """清空 output/ 下所有生成产物（幂等）。"""
        output_dir = self.config.output_path
        if not output_dir.exists():
            print("  ℹ️  output/ 不存在，无需清理")
            return

        for child in output_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
                print(f"  🧹 已清理: {child.name}/")
            elif child.suffix in (".png", ".jpg", ".jpeg", ".json", ".md"):
                child.unlink()
                print(f"  🧹 已清理: {child.name}")
        print(f"\n✅ output/ 已清空")

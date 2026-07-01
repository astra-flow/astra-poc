"""
快速测试：使用 DesignTokens + IconPicker.text 生成 3 张对比图。
"""
import os, sys, socket, time, json
sys.path.insert(0, os.path.dirname(__file__))

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from prompt.aesthetic.tokens import DesignTokens
from prompt.aesthetic.preset import StylePreset
from prompt.icon import IconPicker
from prompt.semantic.sequence import SequenceBuilder, Phase, Swimlane
from prompt.builder import PromptBuilder, LayoutRule

# ── 配置 ──
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "output", "compare")
os.makedirs(OUT, exist_ok=True)

socket.setdefaulttimeout(180)
s = requests.Session()
s.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=2, allowed_methods=["GET","POST"], status_forcelist=[429,500,502,503,504])))
H = {"Content-Type": "application/json", "Authorization": f"Bearer {os.environ['ARK_API_KEY']}"}
U = "https://ark.cn-beijing.volces.com/api/plan/v3"

# ── 通用步骤 ──
steps = [
    Phase("发现", items=["搜索", "浏览"]),
    Phase("注册", items=["填写", "验证"]),
    Phase("购买", items=["支付", "确认"]),
]

# ── 测试用例 ──
tests = []

# 1. 咨询风格 + emoji 情绪曲线
t1 = DesignTokens.from_style("consulting")
b1 = SequenceBuilder(tokens=t1)
lane1 = Swimlane(
    label="情绪曲线",
    items=[IconPicker.emoji("😊", label="高"), IconPicker.emoji("😐", label="中"), IconPicker.emoji("😢", label="低")],
    display_mode="icon",
)
sem1 = b1.linear("客户旅程地图", steps, top_swimlanes=[lane1])
p1 = PromptBuilder(semantic=sem1, aesthetic=StylePreset.consulting(), tokens=t1, no_line=True).build()
tests.append(("consulting_emoji", p1))

# 2. 微信风格 + text 情绪曲线
t2 = DesignTokens.from_style("wechat")
b2 = SequenceBuilder(tokens=t2)
lane2 = Swimlane(
    label="情绪曲线",
    items=[IconPicker.text("笑脸", label="高"), IconPicker.text("平脸", label="中"), IconPicker.text("哭脸", label="低")],
    display_mode="icon",
)
sem2 = b2.linear("客户旅程地图", steps, top_swimlanes=[lane2])
p2 = PromptBuilder(semantic=sem2, aesthetic=StylePreset.wechat(), tokens=t2, no_line=True).build()
tests.append(("wechat_text", p2))

# 3. 深色风格 + text 情绪曲线 + 底部泳道
t3 = DesignTokens.from_style("dark")
b3 = SequenceBuilder(tokens=t3)
lane3_top = Swimlane(
    label="情绪曲线",
    items=[IconPicker.text("笑脸", label="高"), IconPicker.text("平脸", label="中"), IconPicker.text("哭脸", label="低")],
    display_mode="icon",
)
lane3_bottom = Swimlane(
    label="机会点",
    items=["简化支付流程", "推荐奖励机制"],
    display_mode="text",
)
sem3 = b3.linear("客户旅程地图", steps, top_swimlanes=[lane3_top], bottom_swimlanes=[lane3_bottom])
p3 = PromptBuilder(semantic=sem3, aesthetic=StylePreset.dark(), tokens=t3, no_line=True).build()
tests.append(("dark_text", p3))

# ── 生成 ──
for i, (name, prompt) in enumerate(tests):
    print(f"\n>>> [{i+1}/{len(tests)}] 生成 {name}", flush=True)
    print(f"  Prompt 长度: {len(prompt)} 字符", flush=True)
    resp = s.post(f"{U}/images/generations", headers=H,
        json={"model": "doubao-seedream-5.0-lite", "prompt": prompt, "size": "2K", "output_format": "png", "watermark": False},
        timeout=(10, 120))
    if resp.status_code == 200 and "data" in resp.json():
        url = resp.json()["data"][0]["url"]
        img = s.get(url, timeout=(5, 30))
        if img.status_code == 200:
            fname = os.path.join(OUT, f"{name}_{time.strftime('%Y%m%d_%H%M%S')}.png")
            with open(fname, "wb") as f:
                f.write(img.content)
            print(f"  ✅ {fname} ({len(img.content) / 1024:.0f}KB)", flush=True)
    else:
        print(f"  ❌ {resp.status_code}: {resp.text[:300]}", flush=True)

print(f"\n✅ 全部完成！输出目录: {OUT}")

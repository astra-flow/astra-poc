"""
Batch 1: P0 图表 - 产品经理 + 效能教练最高频场景
使用设计 Token 和 Prompt Builder 保证一致性
"""
from .design.tokens import color_hex, token, MORANDI, SLATE, ROLE, BRANCH, STAGE
from .design.prompts import (
    base_style, build_prompt, title, no_line,
    card, tag, container_box, section_header,
)


def get_batch_core():
    return [
        # ===== 测试 1: 客户旅程地图 =====
        # 变体 A: 莫兰迪色系 / 变体 B: Slate 色系
        {
            "name": "customer_journey_map",
            "prompt": build_prompt([
                f"生成一张专业的客户旅程地图，{base_style()}",
                f"展示'在线教育平台'的用户体验流程，泳道式布局，横向时间轴从左到右分为5个阶段。",
                title("在线教育平台 - 客户旅程地图"),
                "横向5个阶段（从左到右水平排列，每个阶段一个容器框）：",
                f"阶段1（{MORANDI['light_blue_gray']}背景）：'发现' - 包含'搜索引擎'、'社交媒体'、'朋友推荐'",
                f"阶段2（{MORANDI['light_blue_gray']}背景）：'注册' - 包含'浏览首页'、'查看课程'、'注册账号'",
                f"阶段3（{MORANDI['light_blue_gray']}背景）：'体验' - 包含'试听课程'、'选择课程'、'完成支付'",
                f"阶段4（{MORANDI['light_blue_gray']}背景）：'学习' - 包含'观看视频'、'完成作业'、'互动问答'",
                f"阶段5（{MORANDI['light_blue_gray']}背景）：'推荐' - 包含'获得证书'、'分享成果'、'推荐朋友'",
                "每个阶段下方标注情绪曲线：发现→中等、注册→较高、体验→低（支付痛点）、学习→高、推荐→很高",
                f"底部泳道（{MORANDI['light_blue_gray']}背景）：'机会点' - 阶段3下方'简化支付流程'，阶段5下方'推荐奖励机制'",
                no_line(),
            ]),
            # 变体 B: Slate 色系
            "variants": [
                build_prompt([
                    f"生成一张专业的客户旅程地图，{base_style()}",
                    f"展示'在线教育平台'的用户体验流程，泳道式布局，横向时间轴。",
                    title("在线教育平台 - 客户旅程地图"),
                    "横向5个阶段：",
                    f"阶段1（{SLATE['bg']}背景）：'发现' - 包含'搜索引擎'、'社交媒体'、'朋友推荐'",
                    f"阶段2（{SLATE['bg']}背景）：'注册' - 包含'浏览首页'、'查看课程'、'注册账号'",
                    f"阶段3（{SLATE['bg']}背景）：'体验' - 包含'试听课程'、'选择课程'、'完成支付'",
                    f"阶段4（{SLATE['bg']}背景）：'学习' - 包含'观看视频'、'完成作业'、'互动问答'",
                    f"阶段5（{SLATE['bg']}背景）：'推荐' - 包含'获得证书'、'分享成果'、'推荐朋友'",
                    "情绪曲线：发现→中等、注册→较高、体验→低、学习→高、推荐→很高",
                    f"底部泳道（{SLATE['bg']}背景）：'机会点' - 阶段3下方'简化支付流程'，阶段5下方'推荐奖励机制'",
                    no_line(),
                ]),
            ],
        },

        # ===== 测试 2: 能力成熟度模型 =====
        {
            "name": "capability_maturity_model",
            "prompt": build_prompt([
                f"生成一张专业的能力成熟度模型图，{base_style()}",
                f"展示'研发效能'从 L1 到 L4 的演进阶段，从左到右递进布局。",
                title("研发效能能力成熟度模型"),
                "四个阶段从左到右水平排列，每个阶段一个容器框，宽度递增：",
                f"阶段1（{MORANDI['light_blue_gray']}背景，最窄）：'L1 初始级' - 包含'手工构建'、'无自动化'、'经验驱动'",
                f"阶段2（{MORANDI['light_blue_gray']}背景）：'L2 规范级' - 包含'CI/CD流水线'、'单元测试'、'代码规范'",
                f"阶段3（{MORANDI['light_green_gray']}背景）：'L3 量化级' - 包含'DORA度量'、'自动化测试'、'全链路监控'",
                f"阶段4（{MORANDI['light_orange_gray']}背景，最宽）：'L4 优化级' - 包含'AI辅助开发'、'持续优化'、'工程文化'",
                "每个阶段上方有圆形等级标识：L1灰色、L2蓝色、L3绿色、L4金色",
                no_line(),
            ]),
        },

        # ===== 测试 3: 分支模型对比图 =====
        {
            "name": "branch_model_comparison",
            "prompt": build_prompt([
                f"生成一张专业的分支模型对比图，{base_style()}",
                f"横向泳道式布局，每种分支模型一行，展示常驻分支和合入规则。",
                title("四种分支模型对比"),
                "四种模型从上到下垂直排列，每行一个容器框：",
                f"第1行（{MORANDI['light_blue_gray']}背景）：'Git Flow' - "
                f"标签：{BRANCH['main']}色'main'、{BRANCH['develop']}色'develop'、{BRANCH['feature']}色'feature'、"
                f"{BRANCH['release']}色'release'、{BRANCH['hotfix']}色'hotfix'",
                f"第2行（{MORANDI['light_green_gray']}背景）：'GitHub Flow' - "
                f"标签：{BRANCH['main']}色'main'、{BRANCH['feature']}色'feature'",
                f"第3行（{MORANDI['light_orange_gray']}背景）：'GitLab Flow' - "
                f"标签：{BRANCH['main']}色'main'、{BRANCH['develop']}色'staging'、{BRANCH['main']}色'production'、{BRANCH['feature']}色'feature'",
                f"第4行（{MORANDI['light_purple_gray']}背景）：'Trunk-Based' - "
                f"标签：{BRANCH['main']}色'main'、{BRANCH['feature']}色'短分支'",
                "每行底部灰色小字说明适用场景",
                no_line(),
            ]),
        },
    ]

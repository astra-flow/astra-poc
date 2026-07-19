"""
Batch 4: 稳定性重测 - 精选图表重跑验证一致性
使用新 Prompt Builder API（Chart + DesignTokens + StylePreset）
"""
from prompt.aesthetic import DesignTokens, StylePreset
from prompt.semantic import Chart, Phase, Swimlane
from prompt.icon import IconPicker
from prompt.builder import PromptBuilder


def get_batch_retest():
    t = DesignTokens.from_palette(
        {"bg": "#F0F2F5", "dark": "#2C3E50", "accent": "#D4A04A", "warm_gray": "#8E8E93", "primary": "#4A6FA5"},
        card_bg_cycle=["#F0F2F5", "#EFF5F0", "#F5F2EF", "#F2EFF5"],
    )

    return [
        # ===== 重测 1: 客户旅程地图 =====
        {
            "name": "retest_customer_journey_map",
            "prompt": PromptBuilder(
                semantic=Chart.customer_journey(
                    title="在线教育平台 - 客户旅程地图",
                    steps=[
                        Phase("发现", items=["搜索引擎", "社交媒体", "朋友推荐"]),
                        Phase("注册", items=["浏览首页", "查看课程", "注册账号"]),
                        Phase("体验", items=["试听课程", "选择课程", "完成支付"]),
                        Phase("学习", items=["观看视频", "完成作业", "互动问答"]),
                        Phase("推荐", items=["获得证书", "分享成果", "推荐朋友"]),
                    ],
                    emotion_lane=Swimlane(label="情绪曲线", items=[
                        IconPicker.text("笑脸", label="中等"),
                        IconPicker.text("笑脸", label="较高"),
                        IconPicker.text("哭脸", label="低"),
                        IconPicker.text("笑脸", label="高"),
                        IconPicker.text("笑脸", label="很高"),
                    ], display_mode="icon"),
                    opportunity_lane=Swimlane(label="机会点", items=["简化支付流程", "推荐奖励机制"], display_mode="text"),
                    tokens=t,
                ),
                aesthetic=StylePreset.consulting(),
                tokens=t,
                no_line=True,
            ).build(),
        },

        # ===== 重测 2: 能力成熟度模型 =====
        {
            "name": "retest_maturity_model",
            "prompt": PromptBuilder(
                semantic=Chart(title="研发效能能力成熟度模型", tokens=t)
                    .add_phase_row([
                        Phase("L1 初始级", items=["手工构建", "无自动化", "经验驱动"]),
                        Phase("L2 规范级", items=["CI/CD流水线", "单元测试", "代码规范"]),
                        Phase("L3 量化级", items=["DORA度量", "自动化测试", "全链路监控"]),
                        Phase("L4 优化级", items=["AI辅助开发", "持续优化", "工程文化"]),
                    ], label="4个成熟度阶段")
                    .build(),
                aesthetic=StylePreset.consulting(),
                tokens=t,
                no_line=True,
            ).build(),
        },

        # ===== 重测 3: 分支模型对比图 =====
        {
            "name": "retest_branch_model_comparison",
            "prompt": PromptBuilder(
                semantic=Chart.branch_comparison(
                    title="四种分支模型对比",
                    branches=[
                        ("Git Flow", ["main", "develop", "feature", "release", "hotfix"]),
                        ("GitHub Flow", ["main", "feature"]),
                        ("GitLab Flow", ["main", "staging", "production", "feature"]),
                        ("Trunk-Based", ["main", "短分支"]),
                    ],
                    tokens=t,
                ).build(),
                aesthetic=StylePreset.consulting(),
                tokens=t,
                no_line=True,
            ).build(),
        },

        # ===== 重测 4: 服务蓝图 =====
        {
            "name": "retest_service_blueprint",
            "prompt": PromptBuilder(
                semantic=Chart(title="在线课程平台 - 服务蓝图", tokens=t)
                    .add_swimlane_row(Swimlane(label="物理证据", items=["搜索结果", "课程详情", "支付页面", "播放器"]), label="泳道1")
                    .add_swimlane_row(Swimlane(label="用户行为", items=["搜索课程", "浏览详情", "完成支付", "开始学习"]), label="泳道2")
                    .add_swimlane_row(Swimlane(label="前台服务", items=["推荐课程", "提供试听", "发送确认"]), label="泳道3")
                    .add_swimlane_row(Swimlane(label="后台服务", items=["推荐算法", "订单处理", "权限开通"]), label="泳道4")
                    .add_swimlane_row(Swimlane(label="支持系统", items=["搜索服务", "支付网关", "学习管理"]), label="泳道5")
                    .build(),
                aesthetic=StylePreset.consulting(),
                tokens=t,
                no_line=True,
            ).build(),
        },

        # ===== 重测 5: 价值流图 =====
        {
            "name": "retest_value_stream_map",
            "prompt": PromptBuilder(
                semantic=Chart(title="需求交付价值流图", tokens=t)
                    .add_phase_row([
                        Phase("需求提出", annotations=["2h"]),
                        Phase("需求评审", annotations=["4h"]),
                        Phase("技术设计", annotations=["8h"]),
                        Phase("开发实现", annotations=["40h"]),
                        Phase("测试验证", annotations=["16h"]),
                        Phase("发布上线", annotations=["2h"]),
                    ], label="6个交付步骤")
                    .build(),
                aesthetic=StylePreset.consulting(),
                tokens=t,
                no_line=True,
            ).build(),
        },
    ]

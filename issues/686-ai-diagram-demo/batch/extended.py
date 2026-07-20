"""
Batch 2: P1 图表 - 产品经理 + 效能教练中频场景
使用新 Prompt Builder API（Chart + DesignTokens + StylePreset）
"""
from prompt.aesthetic import DesignTokens, StylePreset
from prompt.semantic import Chart, Phase, Swimlane
from prompt.builder import PromptBuilder


def get_batch_extended():
    t = DesignTokens.from_palette(
        {"bg": "#F0F2F5", "dark": "#2C3E50", "accent": "#D4A04A", "warm_gray": "#8E8E93", "primary": "#4A6FA5"},
        card_bg_cycle=["#F0F2F5", "#EFF5F0", "#F5F2EF", "#F2EFF5"],
    )

    return [
        {
            "name": "service_blueprint",
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
        {
            "name": "user_story_map",
            "prompt": PromptBuilder(
                semantic=Chart(title="在线课程平台 - 用户故事地图", tokens=t)
                    .add_phase_row([
                        Phase("选课", items=["搜索课程", "查看详情"]),
                        Phase("报名", items=["注册账号", "支付报名"]),
                        Phase("学习", items=["观看视频", "完成作业"]),
                        Phase("结业", items=["参加考试", "获取证书"]),
                    ], label="用户活动阶段")
                    .build(),
                aesthetic=StylePreset.consulting(),
                tokens=t,
                no_line=True,
            ).build(),
        },
        {
            "name": "branch_lifecycle",
            "prompt": PromptBuilder(
                semantic=Chart(title="分支晋升生命周期", tokens=t)
                    .add_phase_row([
                        Phase("开发阶段", items=["feature分支", "本地开发与测试"]),
                        Phase("集成阶段", items=["develop分支", "集成测试与代码评审"]),
                        Phase("预发布阶段", items=["staging分支", "预生产验证"]),
                        Phase("生产阶段", items=["production分支", "生产发布"]),
                    ], label="4个晋升阶段")
                    .build(),
                aesthetic=StylePreset.consulting(),
                tokens=t,
                no_line=True,
            ).build(),
        },
        {
            "name": "baseline_management",
            "prompt": PromptBuilder(
                semantic=Chart(title="版本基线管理流程", tokens=t)
                    .add_phase_row([
                        Phase("v1.0.0-alpha", items=["创建基线", "标记代码快照"]),
                        Phase("v1.0.0-beta", items=["集成验证", "修复缺陷"]),
                        Phase("v1.0.0-rc.1", items=["预发布验证", "全量回归"]),
                        Phase("v1.0.0", items=["正式发布", "打TAG归档"]),
                    ], label="4个基线里程碑")
                    .build(),
                aesthetic=StylePreset.consulting(),
                tokens=t,
                no_line=True,
            ).build(),
        },
    ]

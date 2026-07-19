"""
Batch 3: P2 图表 - 产品经理 + 效能教练低频但重要场景
使用新 Prompt Builder API（Chart + DesignTokens + StylePreset）
"""
from prompt.aesthetic import DesignTokens, StylePreset
from prompt.semantic import Chart, Phase, Swimlane
from prompt.builder import PromptBuilder


def get_batch_specialized():
    t = DesignTokens.from_palette(
        {"bg": "#F0F2F5", "dark": "#2C3E50", "accent": "#D4A04A", "warm_gray": "#8E8E93", "primary": "#4A6FA5"},
        card_bg_cycle=["#F0F2F5", "#EFF5F0", "#F5F2EF", "#F2EFF5"],
    )

    return [
        # ===== 测试 1: 事件风暴 =====
        {
            "name": "event_storming",
            "prompt": PromptBuilder(
                semantic=Chart(title="在线课程平台 - 事件风暴", tokens=t)
                    .add_swimlane_row(Swimlane(label="命令/决策", items=["用户注册", "课程下单", "开始学习"]), label="时间轴上方")
                    .add_swimlane_row(Swimlane(label="领域事件", items=["用户已注册", "订单已创建", "支付已完成", "课程已开通"]), label="时间轴下方")
                    .add_swimlane_row(Swimlane(label="聚合/外部系统", items=["用户聚合", "订单聚合", "外部系统"]), label="底部区域")
                    .build(),
                aesthetic=StylePreset.consulting(),
                tokens=t,
                no_line=True,
            ).build(),
        },

        # ===== 测试 2: 价值流图 =====
        {
            "name": "value_stream_map",
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

        # ===== 测试 3: 雷达图 =====
        {
            "name": "radar_chart",
            "prompt": PromptBuilder(
                semantic=Chart(title="研发团队效能雷达评估", tokens=t)
                    .add_swimlane_row(Swimlane(label="评估维度", items=["交付速度", "代码质量", "团队士气", "技术债务", "自动化率", "需求响应"]), label="6条轴线")
                    .build(),
                aesthetic=StylePreset.consulting(),
                tokens=t,
                no_line=True,
            ).build(),
        },

        # ===== 测试 4: 配置项管理流程 =====
        {
            "name": "config_management_process",
            "prompt": PromptBuilder(
                semantic=Chart(title="配置项管理全生命周期", tokens=t)
                    .add_phase_row([
                        Phase("识别", items=["识别配置项", "CI-001"]),
                        Phase("登记", items=["录入CMDB", "CI-002"]),
                        Phase("控制", items=["基线化与版本控制", "CI-003"]),
                        Phase("变更", items=["变更评估与审批", "CI-004"]),
                        Phase("审计", items=["定期审计与一致性检查", "CI-005"]),
                        Phase("退役", items=["归档与销毁审批", "CI-006"]),
                    ], label="6个生命周期阶段")
                    .build(),
                aesthetic=StylePreset.consulting(),
                tokens=t,
                no_line=True,
            ).build(),
        },
    ]

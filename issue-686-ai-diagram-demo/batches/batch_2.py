"""
Batch 2: P1 图表 - 产品经理 + 效能教练中频场景
使用设计 Token 和 Prompt Builder
"""
from .design_tokens import color_hex, token, MORANDI, SLATE, ROLE
from .prompt_builder import base_style, build_prompt, title, no_line, card


def get_batch_2():
    return [
        # ===== 测试 1: 服务蓝图 =====
        {
            "name": "service_blueprint",
            "prompt": build_prompt([
                f"生成一张专业的服务蓝图，{base_style()}",
                f"展示'在线课程平台'的前台/后台/支持系统交互，多层泳道布局。",
                title("在线课程平台 - 服务蓝图"),
                "从上到下5个泳道（每个泳道一个容器框，左侧有泳道名称标签）：",
                f"泳道1（{MORANDI['light_blue_gray']}背景）：'物理证据' - 包含'搜索结果'、'课程详情'、'支付页面'、'播放器'",
                f"泳道2（{MORANDI['light_green_gray']}背景）：'用户行为' - 包含'搜索课程'、'浏览详情'、'完成支付'、'开始学习'",
                f"泳道3（{MORANDI['light_orange_gray']}背景）：'前台服务' - 包含'推荐课程'、'提供试听'、'发送确认'",
                f"泳道4（{MORANDI['light_purple_gray']}背景）：'后台服务' - 包含'推荐算法'、'订单处理'、'权限开通'",
                f"泳道5（{MORANDI['light_blue_gray']}背景）：'支持系统' - 包含'搜索服务'、'支付网关'、'学习管理'",
                no_line(),
            ]),
        },

        # ===== 测试 2: 用户故事地图 =====
        {
            "name": "user_story_map",
            "prompt": build_prompt([
                f"生成一张专业的用户故事地图，{base_style()}",
                f"展示'在线课程平台'的用户活动与故事，二维矩阵布局。",
                title("在线课程平台 - 用户故事地图"),
                "横向为用户活动（从左到右4个阶段）：",
                f"阶段1（{MORANDI['light_blue_gray']}背景）：'选课' - 包含'搜索课程'、'查看详情'",
                f"阶段2（{MORANDI['light_green_gray']}背景）：'报名' - 包含'注册账号'、'支付报名'",
                f"阶段3（{MORANDI['light_orange_gray']}背景）：'学习' - 包含'观看视频'、'完成作业'",
                f"阶段4（{MORANDI['light_purple_gray']}背景）：'结业' - 包含'参加考试'、'获取证书'",
                "纵向为优先级分层（从上到下）：",
                "第1层（浅金色背景）：'MVP（第1期）' - 包含'搜索课程'、'查看详情'、'注册账号'、'观看视频'",
                "第2层（浅灰色背景）：'第2期' - 包含'支付报名'、'完成作业'",
                "第3层（浅灰色背景）：'第3期' - 包含'参加考试'、'获取证书'",
                no_line(),
            ]),
        },

        # ===== 测试 3: 分支生命周期图 =====
        {
            "name": "branch_lifecycle",
            "prompt": build_prompt([
                f"生成一张专业的分支生命周期图，{base_style()}",
                f"展示 feature → staging → production 的分支晋升路径，从左到右递进布局。",
                title("分支晋升生命周期"),
                "从左到右4个阶段，每个阶段一个容器框：",
                f"阶段1（{MORANDI['light_blue_gray']}背景）：'开发阶段' - 包含'feature分支'、'本地开发与测试'",
                f"  底部标注：从main创建",
                f"阶段2（{MORANDI['light_green_gray']}背景）：'集成阶段' - 包含'develop分支'、'集成测试与代码评审'",
                f"  底部标注：PR合并",
                f"阶段3（{MORANDI['light_orange_gray']}背景）：'预发布阶段' - 包含'staging分支'、'预生产验证'",
                f"  底部标注：环境验证",
                f"阶段4（{MORANDI['light_blue_gray']}背景）：'生产阶段' - 包含'production分支'、'生产发布'",
                f"  底部标注：打Tag发布",
                "每个阶段上方有圆形状态标识：蓝色'开发中'、绿色'集成中'、橙色'验证中'、金色'已发布'",
                no_line(),
            ]),
        },

        # ===== 测试 4: 基线管理图 =====
        {
            "name": "baseline_management",
            "prompt": build_prompt([
                f"生成一张专业的基线管理图，{base_style()}",
                f"展示版本基线的创建、验证、发布、追溯流程，横向时间轴布局。",
                title("版本基线管理流程"),
                "一条细灰色水平线贯穿画面作为时间轴，从左到右4个里程碑节点：",
                "节点1（蓝色）：'v1.0.0-alpha' - 上方蓝色圆形图标，下方白色卡片'创建基线'、'标记代码快照'，底部标注'T-30天'",
                "节点2（绿色）：'v1.0.0-beta' - 上方绿色圆形图标，下方白色卡片'集成验证'、'修复缺陷'，底部标注'T-20天'",
                "节点3（橙色）：'v1.0.0-rc.1' - 上方橙色圆形图标，下方白色卡片'预发布验证'、'全量回归'，底部标注'T-10天'",
                "节点4（金色）：'v1.0.0' - 上方金色圆形图标，下方白色卡片'正式发布'、'打TAG归档'，底部标注'T-0天'",
                "时间轴下方有容器框'基线追溯'，包含'版本号→Commit'、'Commit→需求'、'需求→测试用例'",
                no_line(),
            ]),
        },
    ]

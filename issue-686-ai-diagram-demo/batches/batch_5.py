"""
Batch 5: 多轮稳定性测试 - 精选图表跑 3 轮，验证输出一致性
每轮用相同 prompt 生成，文件名自动带时间戳区分
"""
from .design_tokens import color_hex, token, MORANDI, SLATE, BRANCH
from .prompt_builder import base_style, build_prompt, title, no_line


def get_batch_5():
    """返回 5 张精选图表，每张跑 3 轮 = 15 次生成"""
    tests = []
    
    # 精选 5 种代表性图表，每种只定义一次 prompt
    # 通过 run_batch 的循环机制自然跑多轮
    
    # 1. 客户旅程地图（P0，效果最好）
    tests.append({
        "name": "stability_customer_journey",
        "prompt": build_prompt([
            f"生成一张专业的客户旅程地图，{base_style()}",
            f"展示'在线教育平台'的用户体验流程，泳道式布局，横向时间轴。",
            title("在线教育平台 - 客户旅程地图"),
            "横向5个阶段：",
            f"阶段1（{MORANDI['light_blue_gray']}背景）：'发现' - 包含'搜索引擎'、'社交媒体'、'朋友推荐'",
            f"阶段2（{MORANDI['light_blue_gray']}背景）：'注册' - 包含'浏览首页'、'查看课程'、'注册账号'",
            f"阶段3（{MORANDI['light_blue_gray']}背景）：'体验' - 包含'试听课程'、'选择课程'、'完成支付'",
            f"阶段4（{MORANDI['light_blue_gray']}背景）：'学习' - 包含'观看视频'、'完成作业'、'互动问答'",
            f"阶段5（{MORANDI['light_blue_gray']}背景）：'推荐' - 包含'获得证书'、'分享成果'、'推荐朋友'",
            "情绪曲线：发现→中等、注册→较高、体验→低、学习→高、推荐→很高",
            f"底部泳道（{MORANDI['light_blue_gray']}背景）：'机会点' - 阶段3下方'简化支付流程'，阶段5下方'推荐奖励机制'",
            no_line(),
        ]),
        # 跑 3 轮
        "rounds": 3,
    })
    
    # 2. 能力成熟度模型（P0，阶梯式布局）
    tests.append({
        "name": "stability_maturity_model",
        "prompt": build_prompt([
            f"生成一张专业的能力成熟度模型图，{base_style()}",
            f"展示'研发效能'从 L1 到 L4 的演进阶段，从左到右递进布局。",
            title("研发效能能力成熟度模型"),
            "四个阶段从左到右水平排列：",
            f"阶段1（{MORANDI['light_blue_gray']}背景）：'L1 初始级' - 包含'手工构建'、'无自动化'、'经验驱动'",
            f"阶段2（{MORANDI['light_blue_gray']}背景）：'L2 规范级' - 包含'CI/CD流水线'、'单元测试'、'代码规范'",
            f"阶段3（{MORANDI['light_green_gray']}背景）：'L3 量化级' - 包含'DORA度量'、'自动化测试'、'全链路监控'",
            f"阶段4（{MORANDI['light_orange_gray']}背景）：'L4 优化级' - 包含'AI辅助开发'、'持续优化'、'工程文化'",
            "每个阶段上方圆形等级标识：L1灰色、L2蓝色、L3绿色、L4金色",
            no_line(),
        ]),
        "rounds": 3,
    })
    
    # 3. 分支模型对比图（P0，泳道对比布局）
    tests.append({
        "name": "stability_branch_comparison",
        "prompt": build_prompt([
            f"生成一张专业的分支模型对比图，{base_style()}",
            f"横向泳道式布局，每种分支模型一行。",
            title("四种分支模型对比"),
            "四种模型从上到下垂直排列：",
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
        "rounds": 3,
    })
    
    # 4. 服务蓝图（P1，多层泳道）
    tests.append({
        "name": "stability_service_blueprint",
        "prompt": build_prompt([
            f"生成一张专业的服务蓝图，{base_style()}",
            f"展示'在线课程平台'的多层交互，泳道布局。",
            title("在线课程平台 - 服务蓝图"),
            "从上到下5个泳道：",
            f"泳道1（{MORANDI['light_blue_gray']}背景）：'物理证据' - '搜索结果'、'课程详情'、'支付页面'、'播放器'",
            f"泳道2（{MORANDI['light_green_gray']}背景）：'用户行为' - '搜索课程'、'浏览详情'、'完成支付'、'开始学习'",
            f"泳道3（{MORANDI['light_orange_gray']}背景）：'前台服务' - '推荐课程'、'提供试听'、'发送确认'",
            f"泳道4（{MORANDI['light_purple_gray']}背景）：'后台服务' - '推荐算法'、'订单处理'、'权限开通'",
            f"泳道5（{MORANDI['light_blue_gray']}背景）：'支持系统' - '搜索服务'、'支付网关'、'学习管理'",
            no_line(),
        ]),
        "rounds": 3,
    })
    
    # 5. 价值流图（P2，含数字标注）
    tests.append({
        "name": "stability_value_stream",
        "prompt": build_prompt([
            f"生成一张专业的价值流图，{base_style()}",
            f"展示需求交付端到端流程及时效。",
            title("需求交付价值流图"),
            "横向6个步骤卡片（从左到右水平排列）：",
            "步骤1（蓝色边框）：'需求提出' - 下方标注'2h'",
            "步骤2（蓝色边框）：'需求评审' - 下方标注'4h'",
            "步骤3（蓝色边框）：'技术设计' - 下方标注'8h'",
            "步骤4（蓝色边框）：'开发实现' - 下方标注'40h'",
            "步骤5（蓝色边框）：'测试验证' - 下方标注'16h'",
            "步骤6（蓝色边框）：'发布上线' - 下方标注'2h'",
            "底部汇总区（浅灰色容器框）：总前置时间72h、总处理时间72h、增值比60%",
            no_line(),
        ]),
        "rounds": 3,
    })
    
    return tests

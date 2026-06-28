"""
设计 Token 系统 - 统一图表视觉风格
所有颜色/阴影/圆角/字号等设计常量集中管理
"""

# ============================================================
# 配色体系
# ============================================================

# 莫兰迪色系（通用）
MORANDI = {
    "sage_green": "#D4E2D4",       # 鼠尾草绿
    "mist_blue": "#D4DCE8",        # 雾霾蓝
    "beige": "#E8E0D4",            # 米色
    "dusty_pink": "#E8D4D4",       # 灰粉色
    "light_blue_gray": "#F0F2F5",  # 极浅蓝灰（容器背景）
    "light_green_gray": "#EFF5F0", # 极浅灰绿（容器背景）
    "light_orange_gray": "#F5F2EF",# 极浅灰橙（容器背景）
    "light_purple_gray": "#F2EFF5",# 极浅紫灰（容器背景）
}

# Slate 主题色系（公众号风格）
SLATE = {
    "primary": "#4A6FA5",          # 石板蓝（主色）
    "dark": "#2C3E50",             # 深蓝灰（文字）
    "warm_gray": "#8E8E93",        # 暖灰（辅助文字）
    "bg": "#F2F2F7",               # 浅灰（页面背景）
    "accent": "#D4A04A",           # 琥珀（强调色）
    "green": "#7A9E7E",            # 鼠尾草绿（辅助色）
}

# 角色主题色系
ROLE = {
    "pm": "#4A6FA5",               # 产品经理 - 蓝色
    "pm_light": "#E8EDF5",         # 产品经理浅色
    "pm_border": "#3A5A8A",        # 产品经理边框
    "project": "#7A9E7E",          # 项目经理 - 绿色
    "project_light": "#EDF5EE",    # 项目经理浅色
    "architect": "#D4A04A",        # 架构师 - 橙色
    "architect_light": "#F5F0E8",  # 架构师浅色
    "coach": "#8E7EA5",            # 效能教练 - 紫色
    "coach_light": "#F0EDF5",      # 效能教练浅色
}

# 分支类型色系
BRANCH = {
    "main": "#4A6FA5",             # 常驻分支 - 蓝色
    "feature": "#8E8E93",          # 特性分支 - 灰色
    "release": "#D4A04A",          # 发布分支 - 橙色
    "hotfix": "#C0392B",           # 热修复 - 红色
    "develop": "#7A9E7E",          # 开发分支 - 绿色
}

# 阶段/等级色系
STAGE = {
    "level_1": "#8E8E93",          # L1 - 灰色
    "level_2": "#4A6FA5",          # L2 - 蓝色
    "level_3": "#7A9E7E",          # L3 - 绿色
    "level_4": "#D4A04A",          # L4 - 金色
    "alpha": "#4A6FA5",            # Alpha - 蓝色
    "beta": "#7A9E7E",             # Beta - 绿色
    "rc": "#D4A04A",               # RC - 橙色
    "release": "#C0392B",          # Release - 红色
}

# 事件风暴色系
EVENT = {
    "command": "#F5E8D0",          # 命令 - 极浅橙色
    "event": "#D0D8F5",            # 领域事件 - 极浅蓝色
    "aggregate": "#D0F0D0",        # 聚合 - 极浅绿色
    "external": "#E8E8E8",         # 外部系统 - 极浅灰色
}

# ============================================================
# 设计 Token
# ============================================================

TOKENS = {
    # 容器
    "container_bg": "#F0F2F5",          # 容器背景
    "container_border": "#D0D5DD",      # 容器边框
    "container_radius": "12px",         # 容器圆角
    "container_padding": "16px",        # 容器内边距
    
    # 卡片
    "card_bg": "#FFFFFF",               # 卡片背景
    "card_radius": "8px",               # 卡片圆角
    "card_shadow": "0 2px 8px rgba(0,0,0,0.08)",  # 卡片阴影
    "card_padding": "12px",             # 卡片内边距
    
    # 标题
    "title_size": "24px",               # 大标题字号
    "title_color": "#2C3E50",           # 大标题颜色
    "title_weight": "bold",             # 大标题字重
    
    # 层级名称
    "layer_size": "16px",               # 层名字号
    "layer_color": "#4A6FA5",           # 层名颜色
    "layer_weight": "600",              # 层名字重
    
    # 组件名称
    "component_size": "14px",           # 组件名字号
    "component_color": "#333333",       # 组件名颜色
    
    # 辅助文字
    "caption_size": "11px",             # 说明字号
    "caption_color": "#8E8E93",         # 说明颜色
    
    # 字体
    "font_family": "PingFang SC, Microsoft YaHei, sans-serif",  # 字体栈
    
    # 时间轴
    "timeline_color": "#D0D5DD",        # 时间线颜色
    "timeline_width": "1.5px",          # 时间线粗细
    
    # 标签
    "tag_radius": "6px",                # 标签圆角
    "tag_padding": "6px 12px",          # 标签内边距
}


def color_hex(name: str, palette: str = "slate") -> str:
    """按调色板名称取色号"""
    palettes = {
        "morandi": MORANDI,
        "slate": SLATE,
        "role": ROLE,
        "branch": BRANCH,
        "stage": STAGE,
        "event": EVENT,
    }
    p = palettes.get(palette, SLATE)
    return p.get(name, "#333333")


def token(name: str) -> str:
    """取设计 Token 值"""
    return TOKENS.get(name, "")

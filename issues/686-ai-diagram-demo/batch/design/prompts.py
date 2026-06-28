"""
Prompt Builder - 用设计 Token 组装 prompt，保证跨批次一致性
集成 Astra Creative Design 美学质量系统六大维度
"""
from .tokens import color_hex, token


def base_style() -> str:
    """统一的全局风格声明（含美学基础）"""
    return (
        f"纯白背景，咨询公司风格。"
        f"使用{token('font_family')}字体。"
        f"所有文字中文。"
        f"色调统一，色彩和谐，视觉层次清晰，信息层级分明。"
    )


def aesthetic_suffix() -> str:
    """美学增强后缀 - 基于 astra-creative-design 美学质量系统
    
    覆盖六大维度：色彩、构图、光影、质感、细节、风格
    """
    return (
        "专业图表设计，电影级光影，色调统一，构图精美，"
        "层次感强，8K超清，细节丰富，质感细腻，工作室质量，获奖作品"
    )


def color_harmony(mode: str = "同类色") -> str:
    """色彩和谐模式
    
    Args:
        mode: 同类色 / 邻近色 / 对比色 / 三色和谐
    """
    modes = {
        "同类色": "使用同类色配色，同一色相不同明度，整体统一高级",
        "邻近色": "使用邻近色配色，色轮相邻颜色，自然舒适和谐",
        "对比色": "使用对比色配色，色轮对面颜色，冲击力强",
        "三色和谐": "使用三色和谐配色，色轮等距三色，丰富不杂乱",
    }
    return modes.get(mode, modes["同类色"])


def visual_hierarchy() -> str:
    """视觉层次规范"""
    return (
        "一张图只有一个主焦点，标题为第一视觉层级，"
        "容器框为第二层级，卡片组件为第三层级，"
        "辅助文字为最底层级。每个层级清晰可辨。"
    )


def container_box(bg_color: str = "#F0F2F5", border_color: str = "#D0D5DD",
                  label: str = "") -> str:
    """容器框描述"""
    r = token("container_radius")
    parts = [f"使用{bg_color}背景、{border_color}边框的{r}圆角容器框"]
    if label:
        parts.append(f"左侧标注'{label}'标签")
    return "，".join(parts)


def card(name: str, color: str = "#FFFFFF", desc: str = "") -> str:
    """卡片组件描述"""
    shadow = token("card_shadow")
    radius = token("card_radius")
    text = f"白色{radius}圆角矩形卡片'{name}'，带{shadow}阴影"
    if desc:
        text += f"，{desc}"
    return text


def tag(name: str, bg: str = "#E8EDF5", color: str = "#4A6FA5") -> str:
    """标签描述"""
    r = token("tag_radius")
    return f"{bg}背景、{color}文字的{r}圆角标签'{name}'"


def title(text: str) -> str:
    """大标题"""
    return (f"顶部深蓝灰色{token('title_size')}大标题'{text}'，"
            f"居中显示")


def section_header(text: str, color: str = "#4A6FA5") -> str:
    """层级/泳道标题"""
    return f"'{text}'使用{color}色{token('layer_size')}粗体"


def no_line() -> str:
    """无连线约束"""
    return "完全不要连接线或箭头"


def layer_layout(description: str) -> str:
    """层级布局描述"""
    return f"从上到下垂直排列，{description}"


def horizontal_layout(description: str) -> str:
    """水平布局描述"""
    return f"从左到右水平排列，{description}"


def build_prompt(sections: list, add_aesthetic: bool = True) -> str:
    """组装完整 prompt
    
    Args:
        sections: 字符串列表，每个元素是一个段落
        add_aesthetic: 是否自动追加美学增强后缀（默认 True）
    """
    result = "\n\n".join(sections)
    if add_aesthetic:
        result += f"\n\n设计要求：{aesthetic_suffix()}"
    return result

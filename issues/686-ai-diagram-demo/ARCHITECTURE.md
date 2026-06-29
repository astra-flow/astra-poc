# AI 绘图 POC 架构推演 — Prompt Builder 设计

> 基于 Issue #686 POC 实测经验提炼的架构方案。
> 日期: 2026-06-28
> 状态: DRAFT（待评审后摄入 wiki）

---

## 1. 核心发现：瓶颈不是模型，是跨领域 Prompt 工程

### 1.1 问题本质

扩散模型（doubao-seedream-5.0-lite）有能力渲染高质量技术图表，但 Prompt 需要同时满足两个跨领域要求：

| 领域 | 谁懂 | 谁不懂 | 对应 Prompt 要素 |
|------|------|--------|-----------------|
| **技术图表语义** | 工程师/产品经理 | 设计师 | 分层、容器分组、连线拓扑、泳道、流程方向 |
| **美学设计体系** | 设计师 | 工程师 | 配色、留白、字体、构图、视觉层次、光影质感 |

这两个学科的跨度太大，很难有人能有意识地把两个领域融合到一起。这是技术图表 AIGC 落地的核心瓶颈。

### 1.2 本 POC 的突破

本 POC 证明，通过结构化的 **Prompt 模板体系** 可以桥接两个领域：

- **专业知识** → 结构化自然语言 Prompt（"无连线版/容器分组/颜色编码/位置邻近"）
- **美学体系** → 设计 Token 化（莫兰迪色系、留白比控制、咨询公司风格约束）

### 1.3 "无连线版"方案的实质

不是"没有连接线"，而是用更高维度的视觉语言替代连线的语义表达：

| 视觉手段 | 替代的连线语义 | 适用场景 |
|---------|--------------|---------|
| 容器分组 | 归属关系（属于哪个模块） | 层次架构图、服务蓝图 |
| 颜色编码 | 类别关系（是什么类型） | 事件风暴、象限矩阵 |
| 位置邻近 | 时序/流程关系（先后顺序） | 时间线、流程图 |
| 嵌套层级 | 父子关系（包含关系） | 思维导图、C4 上下文图 |

---

## 2. 架构方案：Prompt Builder

### 2.1 整体结构

```
                    ┌───────────────────────────────────────┐
                    │         PromptBuilder 总装器           │
                    │   SemanticBuilder + AestheticBuilder   │
                    │   + LayoutRules + IconPicker           │
                    └───────────┬───────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                    ▼
    ┌───────────────┐   ┌───────────────┐   ┌──────────────┐
    │ 语义 Builder   │   │ 美学 Builder   │   │ 交叉关注点    │
    │ (图类型专属)    │   │ (跨图通用)     │   │ (布局/图标)   │
    ├───────────────┤   ├───────────────┤   ├──────────────┤
    │ ContainerBld  │   │ ColorPalette  │   │ LayoutRule   │
    │ SequenceBld   │   │ LightEffect   │   │ ├─ 对齐      │
    │ RadialBld     │   │ Texture       │   │ ├─ 间距      │
    │ MatrixBld     │   │ DetailLevel   │   │ ├─ 留白比    │
    │ AnnotationBld │   │ StylePreset   │   │ └─ 边距      │
    │ ...           │   │ FontSystem    │   │              │
    └───────┬───────┘   │ ShadowSystem  │   │ IconPicker   │
            │           └───────────────┘   │ ├─ 语义选型  │
            ▼                               │ ├─ 风格参数  │
    ┌───────────────┐                       │ └─ 大小/颜色 │
    │ DiagramType   │                       └──────────────┘
    │ 组合器         │
    │ (预置配置)     │
    └───────────────┘
```

### 2.2 语义 Builder（图类型专属）

每种图表类型由 1~3 个语义原语组合而成：

| 语义原语 | Builder | 描述 | 示例 |
|---------|---------|------|------|
| **容器化** | `ContainerBuilder` | 用容器框/泳道/象限表达分组归属 | 分层容器→架构图；泳道容器→服务蓝图 |
| **序列化** | `SequenceBuilder` | 用线性/分支/闭环表达时序流程 | 线性→时间线；分支→分支对比；闭环→配置管理 |
| **辐射化** | `RadialBuilder` | 用中心辐射/多轴表达关系 | 中心辐射→思维导图；多轴→雷达图 |
| **矩阵化** | `MatrixBuilder` | 用二维矩阵表达交叉分类 | 2x2→象限图；时间×优先级→用户故事地图 |
| **标注化** | `AnnotationBuilder` | 用数值/等级/颜色标注元信息 | 时效→价值流图；等级→成熟度模型 |

### 2.3 图表类型的语义组合

90% 的技术图表 = 2~3 个原语组合：

| 图表类型 | 语义组合 | 复杂度 |
|---------|---------|--------|
| 层次架构图 | `ContainerBuilder(分层)` | 直出 |
| 象限矩阵图 | `MatrixBuilder(2x2) + AnnotationBuilder(颜色)` | 直出 |
| 时间线图 | `SequenceBuilder(线性) + AnnotationBuilder(时间节点)` | 直出 |
| 流程图 | `SequenceBuilder(步骤+分支) + ContainerBuilder(返回卡片)` | 直出 |
| 思维导图 | `RadialBuilder(中心辐射) + ContainerBuilder(嵌套)` | 直出 |
| C4 上下文图 | `ContainerBuilder(中心+环绕) + AnnotationBuilder(角色)` | 直出 |
| 服务蓝图 | `ContainerBuilder(泳道) + SequenceBuilder(活动)` | 直出 |
| 事件风暴 | `ContainerBuilder(自由分组) + AnnotationBuilder(颜色编码)` | 直出 |
| 能力成熟度模型 | `SequenceBuilder(L1→L4) + AnnotationBuilder(等级描述)` | 直出 |
| 价值流图 | `SequenceBuilder(步骤) + ContainerBuilder(泳道) + AnnotationBuilder(时效)` | 直出 |
| **客户旅程地图** | `SequenceBuilder(阶段横轴) + ContainerBuilder(每阶段行为/触点/想法) + AnnotationBuilder(情绪颜色编码) + Swimlane(机会点[Anchored])` | **直出 ⭐ 最佳稳定性测试场景** |
| 用户故事地图 | `MatrixBuilder(时间×优先级) + ContainerBuilder(MVP切分)` | 直出 |
| 序列图 | `ContainerBuilder(泳道+垂直时序) + AnnotationBuilder(消息)` | 复杂→二阶段 |
| 状态机图 | `SequenceBuilder(状态流转) + AnnotationBuilder(触发条件)` | 复杂→二阶段 |

> **客户旅程地图的"情绪动线"问题**：传统方式用一条折线表达用户情绪变化，但扩散模型不擅长画精确线。无连线版用"每个阶段容器框的颜色编码"替代——将情绪值映射为容器背景色（高情绪→浅绿/浅粉，低情绪→浅橙/浅灰），人眼通过颜色变化自然感知情绪趋势。见第 3 章详细讨论。

### 2.4 美学 Builder（跨图通用）

覆盖六大美学维度，独立于图表类型：

| 维度 | Builder | 参数示例 |
|------|---------|---------|
| **色彩** | `ColorPalette` | 莫兰迪色系 / Slate 主题 / 品牌色系 |
| **构图** | `Composition` | 对称 / 黄金比例 / 三分法 |
| **光影** | `LightEffect` | 柔光 / 电影光 / 扁平无影 |
| **质感** | `Texture` | 细腻 / 磨砂 / 高光 |
| **细节** | `DetailLevel` | 简约 / 标准 / 丰富 |
| **风格** | `StylePreset` | 咨询公司 / 公众号 / 极简 |

### 2.5 交叉关注点

**布局（LayoutRule）** — 建议分两层：

- **宏观布局**（属于语义 Builder）：象限图天然 2x2、流程图天然水平流、层次图天然垂直堆叠——由图表类型决定
- **微观布局**（跨图通用）：对齐方式、组件间距、留白比、边距

**图标（IconPicker）** — 独立的交叉概念：

- 语义端选类型：`IconPicker(type="database", style="line")`
- 美学端定风格：尺寸、颜色、描边粗细
- 两者在 IconPicker 中汇合

### 2.6 跨层锚定（Cross-Layer Anchoring）

**问题**：不同语义层/模块之间存在"跨层对齐"的需求。典型场景：

- 客户旅程地图：底部"机会点"泳道中的条目，锚定到上方某个阶段下方
- 价值流图：底部汇总区的时效标注，锚定到对应步骤下方
- 架构图：底部技术栈标签，锚定到对应组件下方

**原则**：数据归属在源层，通过 `Anchored` 锚定到目标层的位置索引。

```
来源层（Owner）                   目标层（Anchor Target）
┌──────────────────┐           ┌──────────────────┐
│ Swimlane("机会点") │  ────→   │ Phase("体验")     │
│  ├ Anchored(锚定到)│  at_step │  (索引 2)         │
│  └ "简化支付流程"  │  = 2     └──────────────────┘
└──────────────────┘
```

**接口设计**：

```python
@dataclass
class Anchored:
    """跨层锚定引用"""
    text: str
    at_step: int              # 锚定到的步骤索引
    position: str = "below"   # below / above / inside

class Swimlane:
    """泳道/底部层"""
    label: str
    items: list[str | Anchored]   # 普通项或锚定项
```

**使用示例**：

```python
SequenceBuilder.linear(
    steps=[Phase("发现"), Phase("注册"), Phase("体验"),
           Phase("学习"), Phase("推荐")],
    bottom_layer=Swimlane(
        label="机会点",
        items=[
            Anchored("简化支付流程", at_step=2),   # 阶段3下方
            Anchored("推荐奖励机制", at_step=4),   # 阶段5下方
        ],
    ),
)
```

**生成的 Prompt**：锚定项在底部泳道区域统一输出，但标注了目标位置：

```
底部泳道（#F0F2F5背景）：'机会点'
  - 阶段3下方：'简化支付流程'
  - 阶段5下方：'推荐奖励机制'
```

**POC 验证结论**（2026-06-28 实测）：两种 Prompt 表达方式（标注贴在 Phase 上 vs. 底部泳道内部锚定）生成的图片视觉效果差异不大，但数据模型的合理性差异显著。**Anchored 属于 Swimlane 而非 Phase**，职责更清晰，扩展性更好。

### 2.7 双路线执行策略

```
                    ┌─────────────────────────────────────┐
                    │           PromptBuilder              │
                    └─────────────┬───────────────────────┘
                                  │
                   ┌──────────────┴──────────────┐
                   ▼                              ▼
    ┌──────────────────────┐    ┌──────────────────────────┐
    │ 路线A：直出           │    │ 路线B：二阶段美化          │
    │                      │    │                          │
    │ 适用：简单结构化图     │    │ 适用：复杂语义逻辑图        │
    │ 层次/象限/时间线/     │    │ 序列图/状态机/复杂流程     │
    │ 思维导图/C4 等        │    │                          │
    │                      │    │ Step1: Mermaid/PlantUML   │
    │ Seedream 直接渲染     │    │    → 出结构化底图          │
    │ (无连线版容器布局)     │    │ Step2: Seedream 美学美化   │
    │                      │    │    → 保留底图构图骨架       │
    │                      │    │    → 叠加莫兰迪配色+       │
    │                      │    │      字体+留白+质感        │
    └──────────────────────┘    └──────────────────────────┘
```

**路线B 的本质**：把 Seedream 放在它最擅长的位置——做美化而不是做逻辑推理。复杂拓扑交给确定性渲染引擎（Mermaid/PlantUML），Seedream 只做"把这幅图变好看"。

---

---

## 3. "线"的替代策略：当语义必须用线表达时

无连线版的核心约束是"不用连线"，但某些图表语义天然依赖线条（情绪曲线、流程箭头、关联连线）。以下策略按推荐优先级排列：

### 3.1 策略一：点阵替代（基于格式塔完形原理）⭐ 推荐

**原理**：人眼有自动补全趋势线的能力（格式塔连续性原则），不需要模型真的画线。

**客户旅程地图案例**：

```
传统:  情绪↗──↘──↗──↗  (一条连续折线)
无连线: [😊认知] [🫤体验] [😊付费] [😍推荐]
        人眼自动脑补: ↗ → ↘ → ↗ → ↗
```

**Prompt 表达**：`ContainerBuilder(每阶段容器, emotion_icon="😊🫤😊😍")`

**适用场景**：情绪曲线、趋势变化、升降关系。

### 3.2 策略二：色带替代

**原理**：用连续色块的渐变替代线的走向，扩散模型非常擅长颜色渲染。

```
[🟢认知] [🟡体验] [🟢付费] [🔴推荐]
 高情绪   低情绪   高情绪   惊喜
```

**适用场景**：热力图、情绪动线、风险分布。

### 3.3 策略三：柱状/进度条替代

**原理**：用矩形高度/长度替代线的 Y 值变化。

```
认知: ████████░░ 8/10
体验: ██░░░░░░░░ 2/10
付费: ██████░░░░ 6/10
推荐: █████████░ 9/10
```

**适用场景**：数值对比、评分分布、满意度度量。

### 3.4 策略四：二阶段法（复杂度换精度）

**原理**：Mermaid/PlantUML 精确画线 → Seedream 美化叠色。

```
Step1: Mermaid 画精确的情绪折线图 → 出 PNG 底图
Step2: Seedream 以底图为构图骨架，叠加莫兰迪配色 + 字体 + 质感
```

**代价**：增加一次 API 调用；Seedream 需保留底图线条位置，自由度受限。

**适用场景**：线条精度不可妥协的场景（技术图纸、精确流程图）。

### 3.5 策略对比

| 策略 | 模型友好度 | 语义清晰度 | 视觉美感 | 推荐场景 |
|------|-----------|-----------|---------|---------|
| 点阵替代 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 情绪曲线、趋势变化 |
| 色带替代 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 热力图、风险分布 |
| 柱状替代 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 数值对比、评分 |
| 二阶段法 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 精度不可妥协 |

**核心原则**：优先用"不需要线的方式"表达线的语义。只在语义精度必须由线承载时，才用二阶段法。

---

## 4. 接口设计示例（伪代码）

```python
# ── 语义 Builder ──
class ContainerBuilder:
    """容器化原语"""
    def layer(name, components, style="horizontal") -> str
    def swimlane(name, activities) -> str
    def quadrant(position, items, color) -> str
    def surround(center, satellites) -> str

class SequenceBuilder:
    """序列化原语"""
    def linear(steps, direction="horizontal") -> str
    def branch(steps, branches) -> str
    def loop(steps, return_point) -> str

# ── 美学 Builder ──
class ColorPalette:
    """跨图通用的配色系统"""
    morandi = {...}      # 莫兰迪色系
    slate = {...}        # Slate 公众号主题
    brand = {...}        # 品牌色系

class StylePreset:
    """风格预设"""
    consulting = {...}   # 咨询公司风格
    wechat = {...}       # 公众号文章风格
    minimal = {...}      # 极简风格

# ── 使用示例：象限矩阵图 ──
prompt = PromptBuilder(
    semantic=ContainerBuilder.quadrant(
        tl=("高价值高难度", "#D4E2D4", ["项目A", "项目B"]),
        tr=("高价值低难度", "#D4DCE8", ["项目C"]),
        bl=("低价值高难度", "#E8E0D4", ["项目D"]),
        br=("低价值低难度", "#E8D4D4", ["项目E"]),
    ),
    aesthetic=StylePreset.consulting + ColorPalette.morandi,
    layout=LayoutRule(margin="均衡", align="center"),
).build()
```

---

## 5. 下一步行动

| 优先级 | 事项 | 说明 |
|--------|------|------|
| P0 | 架构方案评审 | 本文件 DRAFT → 评审 → wiki 摄入 |
| P1 | 语义原语接口定义 | 5 个 Builder 的 Python Protocol/ABC |
| P1 | 美学系统接口对齐 | 对齐 astra-creative-design Skill 的六大维度 |
| P2 | 路线B PoC | Mermaid → Seedream 二阶段美化的可行性验证 |
| P2 | DiagramType 组合器 | 预置 12+ 种图表类型的原语组合配置 |

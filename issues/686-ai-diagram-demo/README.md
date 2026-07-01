# AI 绘图大模型 POC — Issue #686

> Spike Issue: [#686](https://github.com/astra-flow/astra/issues/686)
> 模型: doubao-seedream-5.0-lite（ARK API）
> 日期: 2026-06-26

---

## 目录结构

```
poc/issue-686-ai-diagram-demo/
├── poc.py                 # 入口脚本（python3 poc.py 即可运行）
├── README.md              # 本文件（完整经验总结）
├── scripts/               # 辅助脚本
│   ├── verify_llm_quality.py   # 视觉 LLM 批量质检
│   ├── check_stability.py      # 稳定性分析
│   ├── test_vision.py          # 视觉 LLM 连通性测试
│   └── run_eval.py             # 后台评估
├── batches/               # 批次定义 + 设计 Token + Prompt 构建
│   ├── batch_1.py ~ batch_5.py
│   ├── design_tokens.py
│   └── prompt_builder.py
├── references/            # 方案对比参考（mermaid / d2 / excalidraw）
└── output/                # 生成产物（gitignored）
```

---

## 核心结论

### 扩散模型能力边界

| 擅长 | 不擅长 |
| ------ | -------- |
| 容器分组 / 层级布局 | 精确画连接线（交叉、错位、悬空） |
| 颜色编码 / 视觉层次 | 理解 Mermaid / PlantUML 语法 |
| 中文文字渲染 | 复杂拓扑关系表达 |
| 泳道 / 矩阵 / 时间轴等结构化布局 | 精确控制组件间距 |
| 整体美观度（可达咨询级） | — |

**最佳方案：无连线版** — 用容器分组 + 颜色编码 + 位置邻近表达关系，完全避免连接线。

### 7 种图表实测结论

| 图类型 | 效果 | 推荐布局策略 |
| -------- | ------ | ------------- |
| 层次架构图 | 效果最好 | 垂直分层容器，每层 2-4 组件 |
| 象限矩阵图 | 效果很好 | 2x2 十字分割 + 四色象限 |
| 时间线图 | 效果很好 | 垂直/横向时间轴 + 节点 + 卡片 |
| 流程图 | 效果良好 | 水平步骤卡片 + 返回小卡片 |
| 思维导图 | 效果良好 | 中心圆形 + 辐射分支 + 嵌套子节点 |
| C4 上下文图 | 效果良好 | 中心平台框 + 环绕外部实体 |
| 序列图 | 建议用 PlantUML | Seedream 泳道式效果一般 |

---

## Prompt 模板体系

### 层次架构图

```
生成一张专业[主题]架构图，纯白背景，咨询公司风格。
从上到下垂直排列[N]个层级，每层用极浅高级灰圆角容器框包裹：

第1层（最上方，[颜色]）：[层名]
  包含[N]个白色圆角矩形组件水平并排：[组件1]、[组件2]...

第2层（[颜色]）：[层名]
  包含[N]个组件：[组件1]、[组件2]...

设计要求：
- 完全不要连接线
- 每层容器框使用极浅高级灰色，边框使用对应主题色
- 组件使用纯白色圆角矩形，带细微阴影
- 组件内包含简洁线性图标
- 现代无衬线字体，深灰色文字
- 所有文字中文
```

### 象限矩阵图

```
生成一张专业[主题]矩阵图，纯白背景，咨询公司风格。
使用2x2四象限布局，细灰色十字分割线。
横轴标签"[X轴]"，纵轴标签"[Y轴]"。

[位置]象限（[颜色]背景）："[象限名]"
  包含：[项目1]、[项目2]...

设计要求：
- 完全不要连接线
- 每个象限使用对应主题色极浅版本背景
- 每个项目名称放在白色小圆角矩形内，带细微阴影
- 所有文字中文
```

### 时间线图

```
生成一张专业[主题]时间线图，纯白背景，咨询公司风格。
[垂直/横向]时间线布局，一条细灰色[竖线/水平线]贯穿画面。

时间线上分布[N]个里程碑节点：

节点1（[颜色]）：[时间标签] "[标题]"
  描述：[描述文字]
节点2（[颜色]）：[时间标签] "[标题]"
  描述：[描述文字]

设计要求：
- 完全不要连接线
- 节点在时间线左侧/上方用小圆形图标表示
- 描述卡片在时间线右侧/下方，白色圆角矩形带细微阴影
- 每个节点使用不同的高级色系
- 所有文字中文
```

### 流程图

```
生成一张专业[主题]流程图，纯白背景，咨询公司风格。
使用步骤卡片风格，从左到右水平排列[N]个圆角矩形卡片：

步骤1（[颜色]）："[步骤名]"
步骤2（[颜色]）："[步骤名]"
...

在步骤[X]下方有一个浅红色小卡片"驳回→返回步骤[Y]"

设计要求：
- 完全不要连接线
- 每个卡片带轻微阴影
- 步骤编号在左上角小字，步骤名称居中大字
- 所有文字中文
```

---

## 配色体系

### 莫兰迪高级色系（通用）

| 色名 | 色号 | 用途 |
| ------ | ------ | ------ |
| 鼠尾草绿 | #D4E2D4 | 象限/层级背景 |
| 雾霾蓝 | #D4DCE8 | 象限/层级背景 |
| 米色 | #E8E0D4 | 象限/层级背景 |
| 灰粉色 | #E8D4D4 | 象限/层级背景 |
| 极浅蓝灰 | #F0F2F5 | 容器框背景 |
| 极浅灰绿 | #EFF5F0 | 容器框背景 |
| 极浅灰橙 | #F5F2EF | 容器框背景 |

### Slate 主题色系（公众号风格）

| 色名 | 色号 | 用途 |
| ------ | ------ | ------ |
| 石板蓝（主色） | #4A6FA5 | 边框、标题 |
| 深蓝灰 | #2C3E50 | 文字、背景 |
| 暖灰 | #8E8E93 | 辅助文字 |
| 浅灰 | #F2F2F7 | 页面背景 |
| 琥珀（强调色） | #D4A04A | 强调元素 |
| 鼠尾草绿 | #7A9E7E | 辅助色 |

### 角色主题色系

| 角色 | 色号 |
| ------ | ------ |
| 产品经理 | #4A6FA5 |
| 项目经理 | #7A9E7E |
| 架构师 | #D4A04A |
| 效能咨询师 | #8E7EA5 |

---

## Prompt 设计原则

### 结构公式

```
[图类型声明] → [背景/风格] → [组件列表] → [布局要求] → [视觉规范]
```

### 关键技巧

| 技巧 | 说明 |
| ------ | ------ |
| 无连线 | 完全不用连接线/箭头 |
| 容器分组 | 用容器框表达层级关系 |
| 颜色编码 | 不同层级/角色用不同颜色 |
| 图标描述 | 用"带XX图标"让模型画小图标 |
| 数量控制 | 每层不超过 4 个组件 |
| 阴影质感 | 加细微阴影提升层次感 |
| 字体指定 | 指定现代无衬线字体 |
| 叙事逻辑 | 按逻辑链排列层级 |

### 常见失败模式

| 失败模式 | 根因 | 解决方案 |
| --------- | ------ | --------- |
| 线条交叉/错位 | 扩散模型画线不准 | 完全不用连线 |
| 组件间距不均 | 模型不擅长精确控制 | 减少每层组件数（≤4） |
| Mermaid 语法无效 | 模型不理解 DSL | 用结构化自然语言替代 |
| 颜色太鲜艳 | 默认配色倾向饱和 | 指定莫兰迪色系/高级灰 |

---

## 推荐工作流

```
1. 确定图表类型
   ├── 层次架构图 → 无连线版（效果最好）
   ├── 象限矩阵图 → 无连线版（效果很好）
   ├── 时间线图   → 无连线版（效果很好）
   ├── 流程图     → 步骤卡片式（效果良好）
   ├── 思维导图   → 嵌套辐射式（效果良好）
   ├── C4上下文图 → 中心环绕式（效果良好）
   └── 序列图     → PlantUML（推荐）

2. 构造 prompt → 按模板 + 配色体系，确保"完全不要连接线"

3. 调用 API
   ├── POST /api/plan/v3/images/generations
   ├── size: "2K", output_format: "png", watermark: false
   └── 模型: doubao-seedream-5.0-lite

4. 人工确认 → 布局合理？文字清晰？配色高级？

5. 上传微信 CDN → 插入公众号文章
```

---

## 待验证图表类型

| 优先级 | 图表类型 | 说明 |
| -------- | --------- | ------ |
| P0 | 客户旅程地图 | 产品经理最常用，泳道式布局 |
| P0 | 能力成熟度模型 | 效能教练核心产出，阶梯式布局 |
| P0 | 分支模型对比图 | 效能教练高频咨询场景，对比式布局 |
| P1 | 服务蓝图 | 复杂多层泳道 |
| P1 | 用户故事地图 | 二维矩阵布局 |
| P1 | 分支生命周期图 | 晋升路径阶梯式 |
| P1 | 基线管理图 | 时间轴 + 版本号标注 |
| P2 | 事件风暴 | 多色贴纸分组 |
| P2 | 价值流图 | 含时效标注 |
| P2 | 雷达图 | 多边形/辐射布局 |
| P2 | 配置项管理流程 | 环形闭环布局 |

---

## 产出物索引

| 类别 | 文件 | 说明 |
| ------ | ------ | ------ |
| 最佳效果 | `output/role_arch_diagram.png` | 5层角色协作架构图 |
| 最佳效果 | `output/test_c_nolines.png` | 无连线版微服务架构图 |
| 最佳效果 | `output/test_5_quadrant.png` | 象限评估矩阵 |
| 最佳效果 | `output/test_premium_timeline.png` | 优化版横向时间线 |
| 最佳效果 | `output/test_6_timeline.png` | 垂直时间线 |
| 配色优化 | `output/slate_arch_diagram.png` | Slate 主题配色 |
| 配色优化 | `output/test_premium_quadrant.png` | 莫兰迪色系象限图 |
| 配色优化 | `output/test_premium_layers.png` | 高级灰层次图 |
| 封面图 | `output/cover_test.png` | 公众号封面图测试 |
| 角色对比 | `output/role_comparison.png` | 2x2 角色能力矩阵 |

---

## 方案对比

| 维度 | Mermaid | D2 | Excalidraw |
| ------ | --------- | ----- | ------------ |
| 自动布局 | 一般（dagre） | 优秀（tala） | 无（手动） |
| LLM 生成质量 | 最佳 | 一般 | 良好（MCP） |
| Git 版本控制 | 优秀（文本 diff） | 优秀（文本 diff） | 一般（JSON diff） |
| VS Code 原生支持 | 是 | 否（需插件） | 否 |
| 手绘风格 | 否 | 否 | 是 |
| 适合场景 | 文档嵌入、简单图 | 复杂图、高质量布局 | 快速草图、演示 |

---

## 架构设计：Prompt Builder 语义模型

### 设计理念

> **任何"设计系统"，本质上都是一套"语义原子 + 组合规则"的产物。**

UI Design System 和"图表语义模型"是同构的，只是应用域不同。本 POC 的 Prompt Builder 借鉴了 Design System 的分层思想，构建了 4 层语义模型：

### 四层架构

```
┌─────────────────────────────────────────────────────┐
│  层级 4: Prompt 生成层                               │
│  PromptBuilder 总装器 → 完整 Prompt → ARK API       │
├─────────────────────────────────────────────────────┤
│  层级 3: 图表模板层（行业惯用组合）                   │
│  Chart.customer_journey() / .approval_flow() / ...  │
├─────────────────────────────────────────────────────┤
│  层级 2: 图表原语层（通用元素）                       │
│  Swimlane / Phase / Quadrant / Connector / Card     │
├─────────────────────────────────────────────────────┤
│  层级 1: 设计 Token 层（跨图通用）                    │
│  DesignTokens / ColorPalette / StylePreset          │
└─────────────────────────────────────────────────────┘
```

### 目录结构（prompt/）

```
prompt/
├── builder.py              # PromptBuilder 总装器 + LayoutRule
├── icon.py                 # IconPicker 图标选择器（emoji/text/line）
├── aesthetic/              # 美学 Builder（跨图通用）
│   ├── tokens.py           # DesignTokens 设计 Token 系统
│   ├── palette.py          # ColorPalette 配色体系
│   └── preset.py           # StylePreset 风格预设
└── semantic/               # 语义 Builder（图类型专属）
    ├── sequence.py         # SequenceBuilder 序列化原语
    ├── container.py        # ContainerBuilder 容器化原语
    ├── annotation.py       # AnnotationBuilder 标注化原语
    ├── chart.py            # Chart 自由组合模型
    ├── matrix.py           # MatrixBuilder 矩阵原语
    └── radial.py           # RadialBuilder 辐射原语
```

### 核心组件

#### 层级 1：设计 Token 层

**DesignTokens** — 语义 Builder 的颜色/样式唯一来源，所有硬编码颜色值集中管理：

```python
# 三种构造方式
tokens = DesignTokens()                                    # 默认值
tokens = DesignTokens.from_palette(ColorPalette.MORANDI)   # 从配色体系
tokens = DesignTokens.from_style('wechat')                 # 从风格名称
```

| Token | 说明 | 默认值 |
|-------|------|--------|
| `title_color` | 标题颜色 | 深蓝灰色 |
| `title_size` | 标题尺寸 | 大 |
| `card_bg_cycle` | 阶段卡片背景色循环 | `["#F0F2F5"]` |
| `return_card_color` | 闭环返回卡片颜色 | 浅红色 |
| `lane_bg` | 泳道默认背景色 | `#F0F2F5` |
| `accent` | 强调色 | `#D4A04A` |

**StylePreset** — 5 种风格预设（consulting / wechat / minimal / dark / brand），覆盖六大美学维度：色彩、构图、光影、质感、细节、风格。

**ColorPalette** — 6 套配色体系（MORANDI / SLATE / ROLE / BRANCH / STAGE / EVENT）。

#### 层级 2：图表原语层

| 原语 | 说明 | 关键方法 |
|------|------|---------|
| **Swimlane** | 泳道/层 | label, items, display_mode, label_position |
| **Phase** | 序列阶段 | name, items, bg_color, annotations |
| **Anchored** | 跨层锚定 | text, at_step, position |
| **IconPicker** | 图标选择器 | emoji(), text(), build() |
| **ContainerBuilder** | 容器化 | layer(), swimlane(), quadrant(), surround(), group() |
| **AnnotationBuilder** | 标注化 | value_label(), level(), color_code(), emotion_curve() |

**关键设计决策：归属优先于对齐**

`Anchored` 属于源层（如 Swimlane），通过 `at_step` 锚定到目标层，而非把标注挂在 Phase 上：

```python
Swimlane(
    label="机会点",
    items=[
        Anchored("简化支付流程", at_step=2, position="below"),
        Anchored("推荐奖励机制", at_step=4, position="below"),
    ],
)
```

#### 层级 3：图表模板层

**Chart** — 自由组合模型，支持行级自由增删改排序：

```python
chart = Chart(title='客户旅程地图', tokens=t)
chart.add_swimlane_row(emotion_lane)     # 情绪曲线
chart.add_phase_row(steps)               # 业务阶段
chart.add_swimlane_row(opportunity_lane) # 机会点
prompt = chart.build()
```

预设工厂方法：

| 方法 | 说明 |
|------|------|
| `Chart.customer_journey()` | 客户旅程地图（情绪曲线 + 阶段 + 机会点） |
| `Chart.approval_flow()` | 审批流程（阶段 + 驳回返回卡片） |
| `Chart.branch_comparison()` | 分支模型对比（多行分支对比） |

#### 层级 4：Prompt 生成层

**PromptBuilder** — 总装器，组装语义 + 美学 + 布局 + 图标：

```python
prompt = PromptBuilder(
    semantic=chart.build(),
    aesthetic=StylePreset.consulting(),
    tokens=tokens,
    no_line=True,
).build()
```

### 与 UI Design System 的对应关系

| UI Design System 概念 | 图表语义模型对应 |
|----------------------|----------------|
| Design Token（色/字/间距） | DesignTokens（标题色/卡片背景/边框色） |
| Component Library（Button/Card） | Primitive Library（Swimlane/Phase/Quadrant） |
| Layout Grid（8px 网格） | LayoutRule（方向/对齐/间距/留白） |
| Composition Rules（组件嵌套约束） | Chart 行级组合规则 |
| Theming（浅色/深色主题） | StylePreset（咨询风/微信风/极简风/深色风） |

### 数据流

```
用户定义图表 → Chart.build() + StylePreset
                → PromptBuilder.assemble() → 完整 Prompt
                → ARK API (doubao-seedream-5.0-lite) → PNG
                → PillowEvaluator + VisionLLMEvaluator → Report
```

### 待改进方向

1. **JSON Schema 注册表** — 将 Python 类定义提炼为 JSON Schema，支持跨语言复用
2. **图表模板 DSL** — 用 YAML 编写模板，支持参数化变体和嵌套组合
3. **Prompt 质检器** — 调 API 前检查 prompt 质量（组件数、配色、无连线约束等）
4. **渐进式约束** — 常见图表用强模板（精确可控），自定义场景用弱模板（灵活但有风险）

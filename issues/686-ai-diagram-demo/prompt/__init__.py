"""
Prompt Builder 架构 — #686 AI 绘图大模型 POC

三层分离：
1. Semantic Builder — 图表类型专属的原语构建器
   - container: ContainerBuilder（分层/泳道/象限/环绕）
   - sequence: SequenceBuilder（线性/分支/闭环）+ Phase + Anchored
   - radial: RadialBuilder（中心辐射/多轴）
   - matrix: MatrixBuilder（2x2 矩阵/时间×优先级）
   - annotation: AnnotationBuilder（数值/等级/颜色/情绪/锚定列表）
2. Aesthetic Builder — 跨图通用的美学系统
   - palette: ColorPalette（莫兰迪/Slate/角色/分支/阶段/事件色系）
   - preset: StylePreset（咨询/公众号/极简/深色/品牌风格）
3. PromptBuilder 总装器 — 组装语义+美学+布局+图标 → 最终 Prompt
   - LayoutRule（宏观+微观布局）
   - IconPicker（语义选型+美学定风格）
"""

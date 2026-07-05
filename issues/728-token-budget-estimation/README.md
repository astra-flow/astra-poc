# Token 资源包预算测算 — Issue #728

> Issue: [#728](https://github.com/astra-flow/astra/issues/728)
> 隶属 Epic: [#553](https://github.com/astra-flow/astra/issues/553) 企业级AI平台选型与竞标推进
> 关联 Issue: [#676](https://github.com/astra-flow/astra/issues/676) 费用测算（企业级AI平台）

## 背景

基于内部《敏捷软件开发AI应用需求情况统计》调研数据，测算 AI 大模型资源包的年度采购预算，并生成三份面向不同读者的文档。

## 核心结论

- **年预算：265.9 万元**（含 15% 波动系数，覆盖 400 人）
- **人均月费用：482 元/人/月**
- **主力供应商**：DeepSeek 占 73.2%（V4 + Flash）+ 智谱 GLM-5.2 占 24.0%
- **测算方法**：费用主线法（费用数据自洽可信，Token 数据虚高弃用）
- **采购建议**：按金额签框架协议，不按 Token 量签

## 目录结构

```
728-token-budget-estimation/
├── README.md                              # 本文件
├── data/                                  # 原始数据
│   ├── 敏捷软件开发AI应用需求情况统计.xlsx  # 调研表
│   └── official_prices.json               # 各厂商官方刊例价（标准JSON）
├── scripts/                               # 脚本
│   ├── data_provider.py                   # 唯一数据源（所有计算逻辑）
│   ├── 00_official_calc.py                # 控制台输出（预算测算结果预览）
│   ├── 01_vendor_comparison.py            # 供应商比价表生成
│   ├── 02_generate_report_tables.py       # 表格快速预览（markdown）
│   └── 03_render_reports.py               # 文档渲染（Jinja2模板→输出文档）
├── templates/                             # Jinja2 模板
│   ├── 01_预算测算说明.md.j2              # 模板1：完整测算模型
│   ├── 02_预算汇报.md.j2                  # 模板2：管理层汇报版
│   └── 03_供应商询价.md.j2                # 模板3：供应商询价报告
└── output/                                # 输出文档
    ├── 01_预算测算说明.md                 # 预算测算说明
    ├── 02_预算汇报.md                     # 预算汇报
    ├── 03_供应商询价.md                   # 供应商询价报告
    ├── report_tables.md                   # 表格快速预览
    └── 供应商比价表.xlsx                   # 供应商比价表
```

## 架构设计

### 数据流

```
official_prices.json（官方刊例价）+ 调研表.xlsx（费用数据）
        ↓
data_provider.py（唯一数据源，所有计算逻辑）
        ↓
┌──────────────┬──────────────┬──────────────┐
│ 00_控制台输出 │ 01_供应商比价 │ 02_表格预览   │
│              │              │              │
│ 03_文档渲染   │              │              │
│ ↓ Jinja2模板  │              │              │
│ output/*.md  │ output/*.xlsx│ output/*.md  │
└──────────────┴──────────────┴──────────────┘
```

### 单一事实来源原则

所有数据通过 `data_provider.py` 获取，严禁在脚本或模板中写死数据：

- **官方刊例价**：`data/official_prices.json`（标准JSON格式）
- **调研费用数据**：`data/敏捷软件开发AI应用需求情况统计.xlsx`
- **计算逻辑**：`scripts/data_provider.py`（加权单价、Token反推、年预算等）
- **人数计算**：从调研表合计行动态计算，不硬编码

## 三份输出文档

| # | 文档 | 读者 | 内容定位 |
|:-:|------|------|---------|
| 1 | **预算测算说明** | 采购/审计 | 完整的以内部需求调研为基础的预算测算模型，含公式、假设、约束、数据校验 |
| 2 | **预算汇报** | 管理层 | 测算说明的提炼版，补充管理友好的话术（公式一句话说明、预算依据简述等） |
| 3 | **供应商询价** | 供应商 | 询价报告，基于预算测算的 Token 需求和模型配比，让供应商能看懂核心逻辑并报价 |

## 脚本说明

### data_provider.py（唯一数据源）

所有脚本的统一数据来源，包含：
- `load_prices()`：加载官方刊例价JSON
- `calc_persons()`：从调研表合计行计算总人数
- `get_survey_meta()`：提取调研元数据（产品线数、模块数、记录数等）
- `parse_survey()`：解析调研表，按模型族聚合月费用
- `get_all_data()`：获取所有计算数据，返回字典供模板使用

### 00_official_calc.py（控制台输出）

控制台打印预算测算结果，供人工核对。

```bash
python3 scripts/00_official_calc.py
```

### 01_vendor_comparison.py（供应商比价表）

读取供应商报价Excel，生成横向比价表。

```bash
python3 scripts/01_vendor_comparison.py
```

输出：`output/供应商比价表.xlsx`（3个Sheet：年度总价对比、模型单价对比、结论汇总）

### 02_generate_report_tables.py（表格快速预览）

快速生成所有汇报表格的markdown内容，供控制台预览。

```bash
python3 scripts/02_generate_report_tables.py
```

输出：`output/report_tables.md`

### 03_render_reports.py（文档渲染）

使用Jinja2模板渲染生成三份正式文档。

```bash
# 一次性生成全部文档
python3 scripts/03_render_reports.py --all

# 分步骤生成单个文档
python3 scripts/03_render_reports.py --doc 1    # 仅预算测算说明
python3 scripts/03_render_reports.py --doc 2    # 仅预算汇报
python3 scripts/03_render_reports.py --doc 3    # 仅供应商询价

# 生成多个文档
python3 scripts/03_render_reports.py --doc 1 2  # 预算测算说明+预算汇报

# 查看帮助
python3 scripts/03_render_reports.py --help
```

输出：
- `output/01_预算测算说明.md`
- `output/02_预算汇报.md`
- `output/03_供应商询价.md`

### 04_generate_inquiry_template.py（询价Excel模板）

生成标准化的供应商报价 Excel 模板，基于 data_provider 数据自动填充采购需求概况。

```bash
python3 scripts/04_generate_inquiry_template.py
```

输出：`output/Token资源包报价模板.xlsx`（3个Sheet）
- Sheet1: Token资源包报价（供应商填写，黄色=必填）
- Sheet2: 填写说明
- Sheet3: 参考基准价（采购方内部，不发送给供应商）

## 运行方式

### 依赖

```bash
pip install openpyxl jinja2
```

### 全流程运行

```bash
# 1. 控制台预览预算数据
python3 scripts/00_official_calc.py

# 2. 生成供应商比价表（如有供应商报价）
python3 scripts/01_vendor_comparison.py

# 3. 生成表格快速预览
python3 scripts/02_generate_report_tables.py

# 4. 渲染正式文档
python3 scripts/03_render_reports.py --all
```

## 测算逻辑链

```
调研表费用数据自洽可信（62条记录0偏差）
    ↓
以费用为主线编预算
    ↓
用官方刊例价反推 Token 量（费用 ÷ 单价 = Token）
    ↓
Token 量作为规模参考（汇报口径）
    ↓
实际采购按金额签框架协议（不按 Token 量签）
```

## 数据来源

- 调研表：《敏捷软件开发AI应用需求情况统计》（16 产品线 + 21 基础软件模块）
- 官方刊例价：`data/official_prices.json`（来源：DeepSeek/智谱/字节火山/阿里百炼/腾讯TokenHub 官方定价页）

## 如何修改数据

- **修改官方刊例价**：编辑 `data/official_prices.json`
- **修改调研数据**：替换 `data/敏捷软件开发AI应用需求情况统计.xlsx`
- **修改计算参数**（波动系数、缓存命中率等）：编辑 `scripts/data_provider.py` 的参数区
- **修改文档内容/格式**：编辑 `templates/*.md.j2` 模板文件
- **添加新供应商报价**：将报价Excel放入指定目录，编辑 `scripts/01_vendor_comparison.py` 的 `QUOTE_FILES`

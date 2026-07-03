# Token 资源包预算测算 — Issue #728

> Issue: [#728](https://github.com/astra-flow/astra/issues/728)
> 隶属 Epic: [#553](https://github.com/astra-flow/astra/issues/553) 企业级AI平台选型与竞标推进
> 关联 Issue: [#676](https://github.com/astra-flow/astra/issues/676) 费用测算（企业级AI平台）
> 日期: 2026-07-03

## 背景

基于内部《敏捷软件开发AI应用需求情况统计》调研数据，测算 AI 大模型 Token 资源包的年度采购预算。

## 核心结论

- **年预算：314.5 万元**（含 15% 波动系数，覆盖 400 人）
- **人均月费用：570 元/人/月**
- **三大主力模型**：DeepSeek-V4（140万）+ Qwen3-Plus（90万）+ GLM-5.2（82万）占 99%
- **测算方法**：费用主线法（费用数据自洽可信，Token 数据虚高弃用）

## 目录结构

```
728-token-budget-estimation/
├── README.md                          # 本文件
├── data/                              # 调研原始数据
│   └── 敏捷软件开发AI应用需求情况统计.xlsx
├── scripts/                           # 测算脚本
│   ├── 01_data_clean_and_aggregate.py # 数据清洗与模型名归一化
│   ├── 02_budget_calc_fee_line.py     # 费用主线预算计算
│   ├── 03_token_line_compare.py       # Token 主线对比（论证方法选择）
│   ├── 04_per_capita_analysis.py      # 人均费用分析
│   └── 05_recalc_after_fee_update.py  # 费用更新后重算（剔除ArkClaw席位费）
└── output/                            # 输出文档
    └── 敏捷软件开发AI应用Token资源包预算测算说明.md
```

## 脚本说明

| 脚本 | 用途 | 关键输出 |
|------|------|---------|
| 01_data_clean | 模型名归一化、按模型族/场景聚合 | 6 个模型族聚合表 |
| 02_budget_calc | 费用主线法计算年预算 | 314.5 万年预算明细 |
| 03_token_line_compare | Token 主线 vs 费用主线对比 | Token 虚高 60 倍的反证 |
| 04_per_capita | 人均费用测算 | 570 元/人/月 |
| 05_recalc | 剔除 ArkClaw 席位费后重算 | 346 万→314.5 万 |

## 运行方式

```bash
cd scripts
python3 01_data_clean_and_aggregate.py
python3 02_budget_calc_fee_line.py
python3 03_token_line_compare.py
python3 04_per_capita_analysis.py
python3 05_recalc_after_fee_update.py
```

依赖：openpyxl（读取 Excel 调研表）

## 测算逻辑链

```
调研表费用数据自洽可信（62条记录0偏差）
    ↓
以费用为主线编预算
    ↓
用市场真实单价反推 Token 量（费用 ÷ 单价 = Token）
    ↓
Token 量 × 12 × 1.15 波动系数 = 年度资源包规格
    ↓
资源包规格 × 单价 = 年度预算（与费用主线交叉验证，偏差 0%）
```

## 数据来源

- 调研表：《敏捷软件开发AI应用需求情况统计》（17 产品线 + 21 基础软件模块，104 条记录）
- 市场单价：阿里云官方文档（2026-06-24）+ Google 搜索交叉验证

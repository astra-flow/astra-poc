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
- **主力供应商**：DeepSeek 占 73.1%（V4 + Flash）+ 智谱 GLM-5.2 占 26.0%
- **测算方法**：费用主线法（费用数据自洽可信，Token 数据虚高弃用）
- **Token 量**：人均月 3.40 亿，全公司年 18,744 亿（按 DeepSeek 官方刊例价反推，作规模参考）
- **采购建议**：按金额签框架协议，不按 Token 量签

## 目录结构

```
728-token-budget-estimation/
├── README.md                          # 本文件
├── data/                              # 调研原始数据
│   └── 敏捷软件开发AI应用需求情况统计.xlsx
├── scripts/                           # 测算脚本
│   └── 00_official_calc.py            # 权威计算脚本（唯一数据来源）
└── output/                            # 输出文档
    └── 敏捷软件开发AI应用Token资源包预算测算说明.md
```

## 脚本说明

| 脚本 | 用途 |
|------|------|
| 00_official_calc.py | **权威计算脚本**（唯一数据来源），输出所有文档/消息引用的数字 |

> ⚠️ 所有数字必须来自 `00_official_calc.py` 脚本输出，禁止手动计算。

## 运行方式

```bash
cd data
python3 ../scripts/00_official_calc.py
```

依赖：openpyxl（读取 Excel 调研表）

## 测算逻辑链

```
调研表费用数据自洽可信（62条记录0偏差）
    ↓
以费用为主线编预算
    ↓
用 DeepSeek 官方刊例价反推 Token 量（费用 ÷ 单价 = Token）
    ↓
Token 量作为规模参考（汇报口径）
    ↓
实际采购按金额签框架协议（不按 Token 量签）
```

## 数据来源

- 调研表：《敏捷软件开发AI应用需求情况统计》（17 产品线 + 21 基础软件模块，104 条记录）
- 市场单价：阿里云官方文档（2026-06-24）+ Google 搜索交叉验证

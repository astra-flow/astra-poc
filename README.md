# Astra POC Framework

> 本目录是 `astra-flow/astra-poc` 仓库的 git submodule。
> 框架代码在 `src/poc/` 下，POC 实例在 `issue-<N>-<desc>/` 下。

## 快速开始

```bash
# 初始化 submodule（首次克隆主项目后执行）
git submodule update --init poc

# 运行指定 Issue 的 POC
python -m poc run 686

# 查看所有 POC 汇总进度
python -m poc status

# 查看指定 POC 进度
python -m poc status 686

# 列出所有已注册 POC
python -m poc list
```

## 目录结构

```
poc/                              # ← submodule: astra-flow/astra-poc
├── src/poc/                      # POC 框架代码
│   ├── __main__.py               # CLI 入口 (python -m poc)
│   ├── run/                      # 运行时编排层
│   │   ├── discovery.py          # 自动发现
│   │   ├── runner.py             # PocRunner 编排
│   │   └── status.py             # 进度查看
│   └── base/                     # 核心抽象层
│       ├── config.py             # PocConfig 数据类
│       ├── poc.py                # PocBase[T] 抽象基类
│       ├── tracker.py            # StatsTracker
│       ├── evaluator.py          # CompositeEvaluator
│       └── result.py             # PocResult / BatchResult
├── issue-686-ai-diagram-demo/    # AI 绘图 POC 实例
└── issue-<N>-<desc>/             # 新增 POC 实例
```

## 新增 POC

在 `poc/` 目录下创建 `issue-<N>-<desc>/` 目录：

```
issue-<N>-<desc>/
├── poc.py           # PocBase 子类（必须）
├── config.py        # PocConfig 子类（可选）
├── evaluate/        # 评估器实现（可选）
├── batch/           # 批次定义（可选）
└── README.md        # 经验总结
```

`poc.py` 中实现 `PocBase[TConfig]` 子类并覆盖 `from_issue()` 工厂方法，框架自动发现注册。

## CLI 用法

```
python -m poc run <issue>          # 运行指定 Issue 的 POC
python -m poc run <issue> --clean  # 清空产出物
python -m poc status               # 所有 POC 进度汇总
python -m poc status <issue>       # 指定 POC 进度
python -m poc list                 # 列出所有已注册 POC
```

## 核心概念

| 概念 | 说明 |
|------|------|
| `PocBase[T]` | 抽象基类，定义 setup/run/evaluate/report 生命周期 |
| `PocConfig` | 不可变配置数据类，子类可扩展 |
| `PocRunner` | 编排执行器，自动调用生命周期方法 |
| `CompositeEvaluator` | 组合多个评估器，按顺序执行并聚合结果 |
| `StatsTracker` | 各阶段成功率追踪 |
| `PocResult` | 结构化执行结果 |

## 向后兼容

现有 POC 的独立运行入口保留：

```bash
# 旧入口（仍可用）
python3 poc/issue-686-ai-diagram-demo/legacy_poc.py

# 新入口（推荐）
python -m poc run 686
```

## License

Apache 2.0

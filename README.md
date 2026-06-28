# Astra POC Framework

通用 POC（Proof of Concept）验证框架。提供抽象基类 `PocBase[T]`、编排执行器 `PocRunner`、组合评估器 `CompositeEvaluator` 等基础设施，支持任意类型的验证任务。

## 快速开始

```bash
# 在主项目中初始化
git submodule update --init poc

# 运行指定 Issue 的 POC
python -m poc run 686

# 查看所有 POC 进度
python -m poc status

# 列出已注册 POC
python -m poc list
```

## 新增 POC

在 `poc/` 目录下创建 `issue-<N>-<desc>/` 目录，包含：

```
issue-<N>-<desc>/
├── poc.py           # PocBase 子类
├── config.py        # PocConfig 子类（可选）
├── evaluators/      # 评估器（可选）
├── batches/         # 批次定义（可选）
└── README.md        # 经验总结
```

`poc.py` 中实现 `PocBase[TConfig]` 子类，框架自动发现注册。

## 目录结构

```
src/poc/
├── __init__.py
├── __main__.py      # CLI 入口: python -m poc
├── _discovery.py    # 自动发现
├── _runner.py       # PocRunner
├── _status.py       # 进度查看
├── py.typed         # PEP 561 类型标记
└── base/
    ├── __init__.py
    ├── config.py    # PocConfig
    ├── poc_base.py  # PocBase[T]
    ├── tracker.py   # StatsTracker
    ├── evaluator.py # CompositeEvaluator
    └── result.py    # PocResult, BatchResult
```

## License

Apache 2.0

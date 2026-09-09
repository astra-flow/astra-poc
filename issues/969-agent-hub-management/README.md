# 969 - Agent Hub 承载 APM + Spec Kit 管理面（workflow 编排实证归档）

> **来源**：#969 Spike「Astra Agent Hub 承载 APM + Spec Kit 管理面的整体架构调研」（已关闭）
> **性质**：配置形态实证归档（非 poc 框架注册项——本目录无 `poc.py`，发现器自动跳过，仅作静态产物防丢失）
> **scratch 源**：`/Users/suwei/workspace/speckit-spike-968/`（commit 67749c3，本地保留）

## 内容

| 文件 | 说明 |
|------|------|
| `workflows/workflow.yml` | **自建 astra-delivery base workflow**：六阶段（intake→specify→plan→tasks→implement→test→converge→maintain）+ 四角色 gate（PO/Arch/QA/Release）+ 2 个 slot 扩展点（post-implement 互审 / maintain 治理循环） |
| `overlays/fill-slots.yml` | slot 填充 overlay 示例：把 post-implement 填为 Prog 互审 gate、maintain 填为 shell（治理循环挂载） |

## 验证命令（需 `specify` CLI ≥ 1.0.5.dev0）

```bash
# 安装自建 workflow
specify workflow add .specify/workflows/astra-delivery --dev

# 填充 slot 并解析组合结果（应见 13 steps 完整流水线）
specify workflow overlay add .specify/workflows/overlays/astra-delivery/fill-slots.yml
specify workflow resolve astra-delivery
```

## 关键实证结论（详见 #969 报告）

1. **overlay 只能锚定 base workflow 的 step（或 slot）**，不能锚定其他 overlay 添加的 step → 完整六阶段编排需**自建 base workflow（含 slot 扩展点）**，而非在官方 speckit workflow 上叠加
2. **gate 交互模式**：CLI 强制暂停（TTY 选择）vs Agent 交互式（`verdict_input` + `resume --input verdict=approve` 非交互注入）——评审分层用人工 gate 兜底，确定性校验可 Agent 裁决
3. **step 类型**：12 种内置（command/prompt/shell/gate/slot/if/switch/while/do-while/fan-out/fan-in/init），`prompt` step 可承载多轮交互

## 关联

- #969（spike，已关闭）｜ wiki `concepts/agent-hub-architecture.md`「workflow 编排」节 ｜ wiki `specs/astra-extensions-draft-969.md`（三 extension 规格）
- 后续：`astra-delivery-flow` skill 设计输入

[SIGNAL: OK]

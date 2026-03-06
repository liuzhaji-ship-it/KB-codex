# 冲突项修正规则（2026-03-06）

依据：`manager/agent_roles_v1.md`（最高优先级）

## 已修正冲突项

1. Codex CLI 权限过大（可改代码）
- 冲突来源：旧策略 `scripts/codex_policy.json` 使用 max_auto + danger-full-access
- 修正：限制 Codex 为规划/评估角色，不允许改业务代码

2. Watcher 调用参数过于危险
- 冲突来源：`scripts/watcher.py` 调用 Codex 使用 danger-full-access
- 修正：改为 `--full-auto --sandbox workspace-write`，并要求遵守 `agent_roles_v1.md`

3. 角色优先级未明确
- 冲突来源：`manager/system_goal.md` / `README.md` 仅描述流程，未声明权威规则
- 修正：加入“以 agent_roles_v1.md 为准”的冲突覆盖声明

4. Prompt 对 Codex 写入边界不明确
- 冲突来源：manager/reviewer prompt 无明确禁改代码约束
- 修正：仅允许写 manager/eval/handoff 状态文件，禁止修改业务代码

## 结论
当前项目角色分配与权限边界已与 v1.0 规则对齐。后续新需求默认按该规则执行。
# KB codex

## OpenClaw + Codex CLI 自动协作框架（v1）

当前系统由 **OpenClaw + Codex CLI + watcher** 组成：

1. **OpenClaw（开发执行端）**
   - 负责开发实现、修复问题、交付结果
   - 负责更新 handoff 文件（build_summary / delivery_report / latest_status）

2. **Codex CLI（规划与监督端）**
   - 负责规划拆解、发布任务单、定义验收标准
   - 负责审查交付并输出评测与改进建议

3. **watcher（唯一调度器）**
   - 监听 `handoff/latest_status.json`
   - 按 stage 自动触发 Codex CLI：
     - `waiting_for_manager` -> manager prompt
     - `waiting_for_review` -> reviewer prompt

4. **人工角色**
   - 仅负责注入高层目标和必要纠偏
   - 不参与每轮手工调度

## 目录结构

- `manager/`：目标、任务单、验收标准
- `handoff/`：执行总结、交付报告、状态文件
- `eval/`：评测报告、改进清单、测试问题
- `scripts/`：manager/reviewer prompt + watcher

## 快速使用

1. 查看当前状态：`handoff/latest_status.json`
2. 启动 watcher：
   ```bash
   python scripts/watcher.py
   ```
3. OpenClaw 按任务单开发并更新 handoff 文件
4. 将 stage 改为 `waiting_for_review`，由 watcher 触发监督评审

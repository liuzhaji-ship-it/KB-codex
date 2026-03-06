# OpenClaw + Codex CLI 双执行体系统目标

> 角色与权限以 `manager/agent_roles_v1.md` 为最高优先级。若与历史文档冲突，以该文件为准。

## 项目总体目标
构建一个可重复运行的“双执行体编程系统”：
- **OpenClaw**：开发执行端，负责实现、修复、提交代码与交付产物。
- **Codex CLI**：规划与监督端，负责目标拆解、任务发布、验收定义、审查评估、改进建议。
- **watcher**：唯一调度器，监听状态并按阶段触发 Codex CLI。

## 角色边界

### 1) OpenClaw（执行者，默认规划负责人）
- 默认承担规划动作（Manager）与执行落地
- 规划阶段必须进行充分调研（优先开源复用与许可审查）
- 产出 build_summary 与 delivery_report
- 更新 latest_status.json 表示是否需要审查/修复

### 2) Codex CLI（规划/监督者）
- 读取项目状态与目标
- 发布/更新 task_order 与 acceptance_criteria
- 审查交付，产出 eval_report 与 improvement_todo
- 给出是否通过、是否需修复

### 3) watcher（调度器）
- 作为唯一自动触发入口
- 仅依据 handoff/latest_status.json 的 stage 执行动作
- 避免重复触发、空转和死循环

## 协作原则
1. 一切协作以文件为准，不依赖口头约定。
2. 规划与监督优先于业务功能扩展。
3. 每轮必须有清晰输入、清晰输出、清晰状态迁移。
4. watcher 必须有防重复触发机制。
5. 第一版先保证“可跑通流程”，再做复杂增强。
6. 默认执行《manager/development_methodology.md》：除非明确授权跳过，不允许未调研先编码。

## 初始要求（第一阶段）
- 搭建目录与通信文件
- 搭建 manager/reviewer 两类 Prompt
- 搭建 watcher 调度逻辑与日志
- 建立初始状态，能进入 Codex CLI 规划阶段

## 初始阶段定义
- `waiting_for_manager`：等待规划端生成任务单与验收标准
- `ready_for_build`：可由 OpenClaw 执行开发
- `waiting_for_review`：等待监督端审查
- `needs_fix`：需修复后再提交审查
- `passed`：当前轮通过，可进入下一轮

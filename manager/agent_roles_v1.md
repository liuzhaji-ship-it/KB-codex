# 自动化编程 Agent 系统角色设定与权限规则（权威版）

- 版本：v1.0
- 生效时间：2026-03-06 00:00（本地时间）
- 冲突处理：若与历史文档冲突，以本文件为准。

## 1. 角色与职责

### 用户（Human User）
- 目标提供者与最终决策者
- 可启动/停止流程、覆盖规划、关键阶段审核
- 不直接执行开发任务，不参与自动调度

### OpenClaw（Implementation Agent）
- 需求分析、技术调研、方案规划、代码实现、修复优化
- 参与阶段：Planning + Implementation
- 典型输出：
  - manager/research_report.md
  - manager/module_plan.md
  - manager/implementation_roadmap.md
  - handoff/build_summary.md
  - handoff/delivery_report.md
- 权限：可读写项目文件、改代码、安装依赖、清理自身临时文件
- 限制：
  - 不改冻结层
  - 不跳过规划直接开发
  - 不绕过评估直接宣告完成
  - 不无限循环

### Codex CLI（Planning & Review Agent）
- 规划监督与评估：出题、评估、幻觉检测、改进建议
- 典型输出：
  - eval/test_questions.json
  - eval/eval_report.md
  - eval/improvement_todo.md
- 权限：可读文档/代码、生成测试与评估文档
- 限制：
  - 不直接修改代码
  - 不直接执行开发任务
  - 不控制流程调度

### Watcher（Orchestrator）
- 仅负责状态监听与调度控制
- 防死循环、节流、异常停机
- 不做需求分析/评估/编码

## 2. 状态机制（必须顺序）
idle -> triage -> planning -> plan_ready -> implementing -> waiting_for_review -> reviewing -> needs_revision -> approved -> stopped

不得跳跃推进。

## 3. 文件协作目录
- manager/
- handoff/
- eval/
- scripts/

## 4. 冻结层与演化层
- 冻结层：2026-03-06 00:00 前存在内容，默认不可改
- 演化层：该时间后新增内容，可改可重建

## 5. 自动化限制
1) 每轮必须有最大轮数
2) 连续重复建议不超过两轮
3) 异常状态必须停止
4) Watcher 必须有触发冷却
5) 重要改动必须记录

## 6. 设计原则
- 规划先于编码
- 回答基于知识库
- 回答可追溯
- 流程可控
- 系统可扩展
- 全阶段可审计

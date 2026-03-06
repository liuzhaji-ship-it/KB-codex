# 当前任务单（Implementation Round）

## 元信息
- 任务编号：TASK-20260306-COPD-IMPL-01
- 轮次：R3
- 发布方：OpenClaw Manager
- 发布时间：2026-03-06 15:46 (Asia/Shanghai)

## 本轮目标（允许编码）
1. 完成 3 PDF ingest 建库能力
2. 完成 ask 检索 + 引用来源输出
3. 通过 Codex CLI 自动出题与评测

## In Scope
- src/app.py 功能实现与修复
- data/index.json 索引生成
- eval 测试题、评测报告、改进建议

## Out of Scope
- UI 深度开发
- 非 COPD 范围扩展

## 状态迁移
- 实现完成 -> waiting_for_review
- 评测通过 -> approved
- 评测失败 -> needs_revision

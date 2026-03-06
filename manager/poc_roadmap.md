# PoC 实施路线图（R2）

## 阶段 A：规划完成（当前）
- 已完成调研、底座选择、模块拆解
- 产出文档：research/base_selection/module_breakdown/poc_roadmap

## 阶段 B：编码实现（下一阶段）
目标：实现最小可运行 COPD 问答闭环

1. 建立 ingest 接口
- 读取项目目录 3 PDF
- 建立索引（含 metadata）

2. 建立 ask 接口
- 支持自然语言提问
- 输出结构：结论 / 依据 / 来源
- 证据不足时固定回复：当前知识库中暂无相关依据。

3. 建立测试脚本
- 执行固定题集与自动出题测试入口

## 阶段 C：自动评测（Codex CLI 审查）
1. Codex CLI 读取 3 PDF 生成测试题
2. 调用系统接口完成问答
3. 生成：
- eval/eval_report.md
- eval/improvement_todo.md

## 阶段 D：修复与迭代
- OpenClaw 根据评测结果修复
- Codex CLI 复审
- 达到 PoC 验收标准后进入扩展阶段

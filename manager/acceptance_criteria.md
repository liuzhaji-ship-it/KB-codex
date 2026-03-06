# 验收标准（R3 编程与评测）

## A. 功能实现
- [ ] POST /ingest 能读取项目目录3个PDF并建索引
- [ ] POST /ask 能返回结构化回答（结论/依据/来源）
- [ ] 无依据问题返回“当前知识库中暂无相关依据。”

## B. 可追溯性
- [ ] 回答包含来源文档名
- [ ] 回答包含来源页码

## C. 自动评测
- [ ] Codex CLI 生成测试题（>=8）
- [ ] 输出 eval/eval_report.md
- [ ] 输出 eval/improvement_todo.md

## D. 状态一致性
- [ ] latest_status.json 与实际阶段一致
- [ ] 评测后明确 approved 或 needs_revision

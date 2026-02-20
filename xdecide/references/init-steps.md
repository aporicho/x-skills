## 探测

1. **DECIDE-LOG.md 探测**：搜索 `DECIDE-LOG.md` 或文件名含 `决策记录`、`decision`、`ADR` 等关键词的文件（搜索范围：文档目录及项目根目录）。找到已有文件时优先使用，不强制重命名
2. **三态检测**：
   - **不存在** → 标记"需创建"
   - **存在但格式不符**（无 `## D-NNN` 标题行）→ 标记"迁移候选"
   - **存在且格式正确** → 标记"已就绪"，用 `decision-log.py list` 获取现有条目概览

## 创建

1. **DECIDE-LOG.md 处理**：
   - 需创建 → 在 `output_dir` 下创建（格式见 `references/decision-format.md`）
   - 迁移候选 → 用 AskUserQuestion 询问是否迁移
   - 已就绪 → 跳过
2. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xdecide decision_log "<路径>"`

## 去重

按 `../xbase/references/dedup-steps.md` 流程执行。xdecide 去重职责：MEMORY.md 中决策记录格式说明 → 替换为指针；「任何决策必须记录」→ **保留**（禁令）。

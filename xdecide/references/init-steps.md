1. **探测 DECIDE-LOG.md**：搜索 `DECIDE-LOG.md` 或文件名含 `决策记录`、`decision`、`ADR` 等关键词的文件（搜索范围：文档目录及项目根目录）。找到已有文件时优先使用，不强制重命名。

2. **三态检测**：
   - **不存在** → 在 `output_dir` 下创建 `DECIDE-LOG.md`（格式见 `references/decision-format.md`）
   - **存在但格式不符**（无 `## D-NNN` 标题行）→ AskUserQuestion 询问是否迁移
   - **已就绪** → 用 `decision-log.py list` 获取现有条目，展示概览

3. **写入**：`python3 .claude/skills/xbase/scripts/skill-state.py write xdecide decision_log "<路径>"`

4. **去重**：按 `../xbase/references/dedup-steps.md` 流程执行。xdecide 去重职责：MEMORY.md 中决策记录格式说明 → 替换为指针；「任何决策必须记录」→ **保留**（禁令）。

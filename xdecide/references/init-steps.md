## 探测

1. **DECIDE-LOG.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/DECIDE-LOG.md"`
   - 指纹 Grep：`"^## D-\\d{3} "`, glob=`"*.md"`
   - 模糊名 Glob：`"**/*{决策,decision,ADR,decide}*.md"`
   - 内容指纹：`^## D-\d{3} `
   - 已就绪时追加：用 `decision-log.py list` 获取现有条目概览

## 创建

1. **DECIDE-LOG.md 处理**：
   - 需创建 → 在 `output_dir` 下创建（格式见 `.claude/skills/xdecide/references/decision-format.md`）
   - 迁移候选 → 保留原始内容套用新格式（旧文件在清理步骤处理）
   - 已就绪 → 跳过
2. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xdecide decision_log "<路径>"`

## 清理

**文件清理**：删除探测阶段标记的"废弃候选"文件（已被规范文件取代的旧文件）。有待删除文件时逐个展示，AskUserQuestion 确认后用 `rm -f` 删除（所有废弃文件合并到一条命令）。

**引用清理**：读取 CLAUDE.md，对比本 skill 核心文件（路径从 SKILL-STATE.md 获取），将已被覆盖的具体规范替换为一句话指针（方法论/禁令保留原文）。有重复时逐条展示 diff，AskUserQuestion 确认后 Edit 替换。修复过时引用（指向已不存在的 skill 或旧文件名的引用）。

xdecide 职责：CLAUDE.md/MEMORY.md 中决策记录格式说明 → 替换为指针；「任何决策必须记录」→ **保留**（禁令）。

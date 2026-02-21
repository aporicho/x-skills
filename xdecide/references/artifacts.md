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

xdecide 职责：CLAUDE.md/MEMORY.md 中决策记录格式说明 → 替换为指针；「任何决策必须记录」→ **保留**（禁令）。

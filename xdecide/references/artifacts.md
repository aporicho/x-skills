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
2. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xdecide decision_log "<路径>"`

## 清理

仅执行文件清理。

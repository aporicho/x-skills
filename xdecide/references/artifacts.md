## 探测

1. **DECIDE_LOG.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/DECIDE_LOG.md"`
   - 指纹 Grep：`"^## D-\\d{3} "`, glob=`"*.md"`
   - 模糊名 Glob：`"**/*{决策,decision,ADR,decide}*.md"`
   - 内容指纹：`^## D-\d{3} `
   - 已就绪时追加：读取文件获取现有条目概览

## 创建

1. **DECIDE_LOG.md 处理**：
   - 需创建 → 在 `doc_dir` 下创建（格式见 `.claude/skills/xdecide/references/decide-log-template.md`）
2. **写入状态**：`python3 .claude/skills/xbase/scripts/state.py write xdecide decision_log "<路径>"`
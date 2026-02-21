## 探测

1. **构建命令**：从 CLAUDE.md 或构建配置推导，验证可执行。已有 → 记录；缺失 → 标记"待创建"
2. **DEBUG-LOG.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/DEBUG?LOG.md"`（匹配 DEBUG-LOG.md 和 DEBUG_LOG.md）
   - 指纹 Grep：`"^#### #\\d{3}:"`, glob=`"*.md"`
   - 模糊名 Glob：`"**/*{debug,bug,修复记录,调试}*.md"`
   - 内容指纹：`^#### #\d{3}:`

## 创建

1. **构建命令补齐**：构建命令缺失 → 根据项目类型推导
2. **DEBUG-LOG.md 处理**：
   - 需创建 → 在 `output_dir` 下创建（格式见 `.claude/skills/xdebug/references/debug-log-format.md`）
3. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xdebug debug_log "<DEBUG-LOG.md 路径>"`

## 清理

仅执行文件清理。

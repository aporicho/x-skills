## 探测

1. **RUN.sh 检查**：
   - 从 SKILL-STATE.md `## xbase → run_script` 读取路径
   - 有值 → 验证文件存在且可用
   - 无值 → 标记"需先运行 /xbase 初始化"（RUN.sh 由 xbase 负责创建）
2. **DEBUG_LOG.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/DEBUG?LOG.md"`（匹配 DEBUG_LOG.md 和 DEBUG_LOG.md）
   - 指纹 Grep：`"^#### #\\d{3}:"`, glob=`"*.md"`
   - 模糊名 Glob：`"**/*{debug,bug,修复记录,调试}*.md"`
   - 内容指纹：`^#### #\d{3}:`

## 创建

1. **DEBUG_LOG.md 处理**：
   - 需创建 → 在 `doc_dir` 下创建（格式见 `.claude/skills/xdebug/references/debug-log-template.md`）
3. **写入状态**：`python3 .claude/skills/xbase/scripts/state.py write xdebug debug_log "<DEBUG_LOG.md 路径>"`
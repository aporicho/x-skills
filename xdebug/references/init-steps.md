1. **验证并补齐调试基础设施**：按 `../xbase/references/infra-setup.md` 中的流程检查四项能力（构建、后台启动、日志捕获、停止），缺失的自动创建。后续阶段的"构建""启动""读日志""停止"均通过此基础设施执行，不再各自拼命令。

2. **检测调试日志文件**（DEBUG-LOG.md），判断状态：
   - **不存在** → 在 `output_dir` 下创建（格式见 `references/debug-log-format.md`）
   - **存在但格式不符** → 用 AskUserQuestion 询问是否迁移（保留原始内容，套用新格式）
   - **存在且格式正确** → 跳过，无需操作

3. **写入**：`python3 .claude/skills/xbase/scripts/skill-state.py write xdebug debug_log "<DEBUG-LOG.md 路径>"`

4. **去重**：按 `../xbase/references/dedup-steps.md` 流程执行。xdebug 去重职责：MEMORY.md 中 DEBUG_LOG 格式说明 → 替换为指针；「修复 Bug 必须更新」→ **保留**（禁令）。

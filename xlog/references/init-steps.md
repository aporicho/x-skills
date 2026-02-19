1. 阅读 CLAUDE.md 了解日志相关规则和禁忌（如禁止 print）

2. 扫描代码找到日志工具：
   - 日志工具文件（如 `Logger.swift`、`log.rs`、`logger.ts` 等）
   - 已有的日志调用模式（`Log.xxx`、`log::xxx`、`console.xxx`、`logger.xxx` 等）
   - 可用的 Logger 实例 / 分类 / 子系统
   - 消息语言和 metadata 命名风格

3. 检测两个核心文件：
   - **LOG-RULES.md**：不存在 → 基于扫描结果生成（格式见 `references/log-rules-format.md`）；存在但格式不符 → 问是否迁移；已就绪 → 跳过
   - **LOG-COVERAGE.md**：同上三态检测（格式见 `references/log-coverage-format.md`）

4. **写入**：`python3 .claude/skills/xbase/scripts/skill-state.py write xlog log_rules "<LOG-RULES.md 路径>" log_coverage "<LOG-COVERAGE.md 路径>"`

5. **去重**：按 `../xbase/references/dedup-steps.md` 流程执行。xlog 去重职责：MEMORY.md 中日志规则重复部分 → 替换为指针；「禁止 print()」「日志规范详见 /logging」→ **保留**。

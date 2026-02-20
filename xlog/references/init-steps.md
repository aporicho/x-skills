## 探测

1. **阅读 CLAUDE.md** 了解日志相关规则和禁忌（如禁止 print）
2. **扫描代码**找到日志工具：
   - 日志工具文件（如 `Logger.swift`、`log.rs`、`logger.ts` 等）
   - 已有的日志调用模式（`Log.xxx`、`log::xxx`、`console.xxx`、`logger.xxx` 等）
   - 可用的 Logger 实例 / 分类 / 子系统
   - 消息语言和 metadata 命名风格
3. **LOG-RULES.md 三态检测**（文件名含 log、日志规范、logging）：
   - **不存在** → 标记"需创建"
   - **存在但格式不符** → 标记"迁移候选"
   - **存在且格式正确** → 标记"已就绪"
4. **LOG-COVERAGE.md 三态检测**（文件名含 coverage、覆盖）：
   - 同上三态检测

## 创建

1. **LOG-RULES.md 处理**：
   - 需创建 → 基于扫描结果生成（格式见 `references/log-rules-format.md`）
   - 迁移候选 → 用 AskUserQuestion 问是否迁移
   - 已就绪 → 跳过
2. **LOG-COVERAGE.md 处理**：
   - 需创建 → 基于扫描结果生成（格式见 `references/log-coverage-format.md`）
   - 迁移候选 → 用 AskUserQuestion 问是否迁移
   - 已就绪 → 跳过
3. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xlog log_rules "<LOG-RULES.md 路径>" log_coverage "<LOG-COVERAGE.md 路径>"`

## 去重

按 `../xbase/references/dedup-steps.md` 流程执行。xlog 去重职责：MEMORY.md 中日志规则重复部分 → 替换为指针；「禁止 print()」「日志规范详见 /logging」→ **保留**。

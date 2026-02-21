## 探测

1. **阅读 CLAUDE.md** 了解日志相关规则和禁忌（如禁止 print）
2. **扫描代码**找到日志工具：
   - 日志工具文件（如 `Logger.swift`、`log.rs`、`logger.ts` 等）
   - 已有的日志调用模式（`Log.xxx`、`log::xxx`、`console.xxx`、`logger.xxx` 等）
   - 可用的 Logger 实例 / 分类 / 子系统
   - 消息语言和 metadata 命名风格
3. **LOG-RULES.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/LOG-RULES.md"`
   - 指纹 Grep：`"^## Logger 列表"`, glob=`"*.md"`
   - 模糊名 Glob：`"**/*{log-rules,日志规范,logging}*.md"`
   - 内容指纹：`^## Logger 列表`
4. **LOG-COVERAGE.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/LOG-COVERAGE.md"`
   - 指纹 Grep：`"^## 模块明细"`, glob=`"*.md"`
   - 模糊名 Glob：`"**/*{log.*coverage,日志覆盖}*.md"`
   - 内容指纹：`^## 模块明细`

## 创建

1. **LOG-RULES.md 处理**：
   - 需创建 → 基于扫描结果生成（格式见 `.claude/skills/xlog/references/log-rules-format.md`）
   - 迁移候选 → 保留原始内容套用新格式（旧文件在清理步骤处理）
   - 已就绪 → 跳过
2. **LOG-COVERAGE.md 处理**：
   - 需创建 → 基于扫描结果生成（格式见 `.claude/skills/xlog/references/log-coverage-format.md`）
   - 迁移候选 → 保留原始内容套用新格式（旧文件在清理步骤处理）
   - 已就绪 → 跳过
3. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xlog log_rules "<LOG-RULES.md 路径>" log_coverage "<LOG-COVERAGE.md 路径>"`

## 清理

xlog 职责：CLAUDE.md/MEMORY.md 中日志规则重复部分 → 替换为指针；「禁止 print()」「日志规范详见 ...」→ **保留**（禁令/指针）。

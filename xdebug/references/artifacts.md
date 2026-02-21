## 探测

1. **调试基础设施检查**：
   - **构建命令**：从 CLAUDE.md 或构建配置推导，验证可执行。已有 → 记录；缺失 → 标记"待创建"
   - **调试运行脚本**探测（走废弃候选机制）：
     - Glob 搜索 `"**/run.sh"` + `"**/*{run,start,launch,debug}*.sh"` 找所有候选
     - 排除 `.claude/`、`node_modules/`、`build/`、`target/` 等
     - 对每个候选检查是否支持 `build`/`start`/`stop`/`logs`/`status` 五个子命令
     - 功能最完备的 → 记录为规范脚本；其余 → 标记为废弃候选（步骤 3 清理）
     - 全部缺失或不完备 → 标记"待创建"
2. **DEBUG-LOG.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/DEBUG?LOG.md"`（匹配 DEBUG-LOG.md 和 DEBUG_LOG.md）
   - 指纹 Grep：`"^#### #\\d{3}:"`, glob=`"*.md"`
   - 模糊名 Glob：`"**/*{debug,bug,修复记录,调试}*.md"`
   - 内容指纹：`^#### #\d{3}:`

## 创建

1. **补齐调试基础设施**（对探测中标记"待创建"的项）：
   - 构建命令缺失 → 根据项目类型推导
   - 运行脚本缺失 → 在 `scripts/` 下创建，需支持：`build`（构建）、`start`（后台启动 + 日志捕获到文件）、`stop`（停止进程）、`logs [filter]`（读取/过滤日志）、`status`（检查运行状态）
   - 创建后验证：运行 `build` 和 `status` 确认可用，失败则修复重试
   - 更新状态：`python3 .claude/skills/xbase/scripts/skill-state.py write-info 运行脚本 "<脚本路径>"`
2. **DEBUG-LOG.md 处理**：
   - 需创建 → 在 `output_dir` 下创建（格式见 `.claude/skills/xdebug/references/debug-log-format.md`）
3. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xdebug debug_log "<DEBUG-LOG.md 路径>"`

## 清理

xdebug 职责：CLAUDE.md/MEMORY.md 中 DEBUG_LOG 格式说明 → 替换为指针；「修复 Bug 必须更新」→ **保留**（禁令）。

## 探测

1. **调试基础设施检查**：
   - **构建命令**：从 CLAUDE.md 或构建配置推导，验证可执行。已有 → 记录；缺失 → 标记"待创建"
   - **调试运行脚本**（如 `scripts/run.sh`）：检查是否存在且支持后台启动、日志捕获、停止
     - 已有且功能完备 → 记录路径
     - 缺失或不完备 → 标记"待创建"
2. **DEBUG-LOG.md 三态检测**：搜索文件（文件名含 debug、bug、修复记录），判断状态：
   - **不存在** → 标记"需创建"
   - **存在但格式不符** → 标记"迁移候选"
   - **存在且格式正确** → 标记"已就绪"

## 创建

1. **补齐调试基础设施**（对探测中标记"待创建"的项）：
   - 构建命令缺失 → 根据项目类型推导
   - 运行脚本缺失 → 在 `scripts/` 下创建，需支持：`build`（构建）、`start`（后台启动 + 日志捕获到文件）、`stop`（停止进程）、`logs [filter]`（读取/过滤日志）、`status`（检查运行状态）
   - 创建后验证：运行 `build` 和 `status` 确认可用，失败则修复重试
   - 更新状态：`python3 .claude/skills/xbase/scripts/skill-state.py write-info 运行脚本 "<脚本路径>"`
2. **DEBUG-LOG.md 处理**：
   - 需创建 → 在 `output_dir` 下创建（格式见 `references/debug-log-format.md`）
   - 迁移候选 → 保留原始内容套用新格式，删除旧文件
   - 已就绪 → 跳过
3. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xdebug debug_log "<DEBUG-LOG.md 路径>"`

## 去重

读取 CLAUDE.md/MEMORY.md，对比本 skill 核心文件（路径从 SKILL-STATE.md 获取），将已被覆盖的具体规范替换为一句话指针（方法论/禁令保留原文）。有重复时逐条展示 diff，AskUserQuestion 确认后 Edit 替换。

xdebug 职责：MEMORY.md 中 DEBUG_LOG 格式说明 → 替换为指针；「修复 Bug 必须更新」→ **保留**（禁令）。

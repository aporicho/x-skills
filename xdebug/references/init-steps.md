## 探测

1. **调试基础设施检查**：按 `../xbase/references/infra-setup.md` 中的流程检查四项能力（构建、后台启动、日志捕获、停止），记录现状（已有/缺失）
2. **DEBUG-LOG.md 三态检测**：搜索文件（文件名含 debug、bug、修复记录），判断状态：
   - **不存在** → 标记"需创建"
   - **存在但格式不符** → 标记"迁移候选"
   - **存在且格式正确** → 标记"已就绪"

## 创建

1. **补齐调试基础设施**：对探测中标记缺失的能力，按 `../xbase/references/infra-setup.md` 自动创建
2. **DEBUG-LOG.md 处理**：
   - 需创建 → 在 `output_dir` 下创建（格式见 `references/debug-log-format.md`）
   - 迁移候选 → 保留原始内容套用新格式，删除旧文件
   - 已就绪 → 跳过
3. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xdebug debug_log "<DEBUG-LOG.md 路径>"`

## 去重

读取 CLAUDE.md/MEMORY.md，对比本 skill 核心文件（路径从 SKILL-STATE.md 获取），将已被覆盖的具体规范替换为一句话指针（方法论/禁令保留原文）。有重复时逐条展示 diff，AskUserQuestion 确认后 Edit 替换。

xdebug 职责：MEMORY.md 中 DEBUG_LOG 格式说明 → 替换为指针；「修复 Bug 必须更新」→ **保留**（禁令）。

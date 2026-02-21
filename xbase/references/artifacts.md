## 探测

1. **文档目录**：扫描项目根目录，按优先级查找：`document/` → `docs/` → `doc/`。
   - 找到 → 记录路径
   - 未找到 → 标记为"待创建"
2. **运行脚本**探测：
   - Glob 搜索 `"**/run.sh"` + `"**/*{run,start,launch,debug}*.sh"` 找所有候选
   - 排除 `.claude/`、`node_modules/`、`build/`、`target/` 等
   - 对每个候选检查是否支持 `build`/`start`/`stop`/`logs`/`status` 五个子命令
   - 功能最完备的 → 记录为规范脚本；其余 → 标记为废弃候选（清理阶段处理）
   - 全部缺失或不完备 → 标记"待创建"

## 创建

1. **文档目录**：
   - output_dir 已存在 → 无操作
   - output_dir 待创建 → 创建 `docs/`
   - 写入状态：`python3 .claude/skills/xbase/scripts/skill-state.py write-info output_dir "<路径>"`
2. **运行脚本**（对探测中标记"待创建"的）：
   - 在 `scripts/` 下创建，需支持：`build`（构建）、`start`（后台启动 + 日志捕获到文件）、`stop`（停止进程）、`logs [filter]`（读取/过滤日志）、`status`（检查运行状态）
   - 创建后验证：运行 `build` 和 `status` 确认可用，失败则修复重试
   - 写入状态：`python3 .claude/skills/xbase/scripts/skill-state.py write xbase run_script "<脚本路径>"`

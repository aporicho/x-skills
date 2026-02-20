## 探测

扫描项目根目录，按优先级查找文档目录：`document/` → `docs/` → `doc/`。
- 找到 → 记录路径
- 未找到 → 标记为"待创建"

## 创建

- output_dir 已存在 → 无操作
- output_dir 待创建 → 创建 `docs/`
- 写入状态：`python3 .claude/skills/xbase/scripts/skill-state.py write-info output_dir "<路径>"`

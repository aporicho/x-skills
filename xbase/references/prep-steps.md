按步骤 1→2→3 顺序执行，然后执行本 skill 的特有探测步骤。

**步骤 1：快速跳过检查**

查看上方预加载输出：

- 输出含 `initialized` → **跳过整个阶段 0**，直接进入阶段 1
- 输出含 `not_found` → 继续步骤 2

**步骤 2：项目探测**

> 如预加载输出中 `## 项目信息` 的 `output_dir` 已有值（其他 skill 已写入）→ 跳过本步，直接步骤 3。

1. 用 Glob 扫描项目根目录，识别标志文件（Cargo.toml、Package.swift、*.xcodeproj、package.json 等）
2. 读 CLAUDE.md，理解构建命令、项目类型、日志系统等
3. 找到文档目录（`document/`、`docs/`、`doc/` 等），未找到则创建 `docs/`
4. 写入探测结果：
   ```bash
   python3 .claude/skills/xbase/scripts/skill-state.py write-info output_dir "<目录>"
   ```

**步骤 3：产出物搜索与创建**

从预加载输出或步骤 2 获取 `output_dir`。对本 skill `## 核心文件` 表中的每个产出物：

1. 在全项目搜索用途相似的已有文件（按内容和用途匹配，不限文件名和位置）
2. **找到** → AskUserQuestion 询问是否迁移（保留原始内容，套用新格式），确认后迁移到 `output_dir`
3. **没找到** → 创建骨架后用 Edit 填充：
   ```bash
   python3 .claude/skills/xbase/scripts/artifact-create.py <artifact_name> <output_dir>/<文件名>
   ```

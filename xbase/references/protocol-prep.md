# 准备协议

**步骤 1：快速跳过检查**

查看上方预加载输出：

- 输出含 `initialized` → **跳过整个阶段 0**，直接进入阶段 1
- 输出含 `not_found` → 继续步骤 2

**步骤 2：项目探测**

> 如预加载输出中 `## 项目信息` 的 `doc_dir` 已有值（其他 skill 已写入）→ 跳过本步。

1. 用 Glob 扫描项目根目录，识别标志文件（Cargo.toml、Package.swift、*.xcodeproj、package.json 等）
2. 读 CLAUDE.md，理解构建命令、项目类型、日志系统等
3. 找到文档目录（`document/`、`docs/`、`doc/` 等），未找到则创建 `docs/`
4. 写入探测结果：
   ```bash
   python3 .claude/skills/xbase/scripts/skill-state.py write-info doc_dir "<目录>"
   ```

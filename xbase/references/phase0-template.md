# 阶段 0 标准流程

> 所有工作流 skill 共享的阶段 0 模板。各 skill 引用此文件 + 补充特有探测步骤。

## 预加载状态

在 SKILL.md 的流程段开头添加一行自动执行命令：

```
!`python3 .claude/skills/xbase/scripts/skill-state.py check-and-read <skill名> 2>/dev/null`
```

输出格式：第一行为 check 结果（`initialized` / `not_found`），`---` 分隔，后续为完整状态内容。

## 快速跳过逻辑

查看预加载结果：
- 第一行输出 `initialized` → 已有状态信息可用 → **跳过整个阶段 0**
- `## 项目信息` 段已存在（其他 skill 写入）→ 直接复用项目类型、构建命令等，不再重复探测
- `## 项目信息` 中有 `运行脚本` 字段 → 跳过基础设施检查（如有）
- 第一行输出 `not_found` → 执行完整探测流程

## SKILL.md 结构约定

有产出物的 skill 在 SKILL.md 中必须包含：

1. **核心文件表**（`## 核心文件`）— 列出 skill 管理的产出文件、说明、格式规范路径：
   ```markdown
   ## 核心文件

   | 文件 | 说明 | 格式规范 |
   |------|------|----------|
   | `XXX.md` | 文件用途 | `references/xxx-format.md` |
   ```

2. **references/ 目录** — 存放产出物的格式规范文件（`*-format.md`），阶段 0 生成产出物时参照。

所有工作流 skill 均有产出物（xcommit 有 COMMIT-RULES.md、xdoc 有 DOC-RULES.md 等），需要以上结构。

## 完整探测流程

1. **项目探测**（Claude 直接执行，不依赖脚本）：
   1. 用 Glob 扫描项目根目录，识别标志文件（Cargo.toml、Package.swift、*.xcodeproj、package.json 等）
   2. 读 CLAUDE.md，提取构建命令、项目类型、日志系统等信息
   3. 找到文档目录（`document/`、`docs/`、`doc/` 等），未找到则创建 `docs/`
   4. 用 `skill-state.py write-info` 写入结果：
      ```bash
      python3 .claude/skills/xbase/scripts/skill-state.py write-info 类型 "<项目类型>" 构建命令 "<构建命令>" output_dir "<文档目录>"
      ```

2. **确定产出物目录**：读取 SKILL-STATE.md 的 `output_dir` 字段（已由步骤 1 写入）。

3. **（各 skill 在此插入特有探测步骤）**
   - 有产出物的 skill：使用 `artifact-check.py` 做**三态检测**：
     ```bash
     python3 .claude/skills/xbase/scripts/artifact-check.py check <artifact_name> <expected_path>
     ```
     - `not_found` → 生成（可用 `artifact-check.py create` 创建骨架，再用 Edit 填充内容）
     - `format_mismatch` → 问迁移
     - `ready` → 跳过

4. **写入 SKILL-STATE.md**：用脚本写入 skill 特有字段：
   ```bash
   # skill 特有字段（含产出物路径）
   python3 .claude/skills/xbase/scripts/skill-state.py write <skill名> <key> <value> ...
   ```

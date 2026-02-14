# 阶段 0 标准流程

> 所有工作流 skill 共享的阶段 0 模板。各 skill 引用此文件 + 补充特有探测步骤。

## 预加载状态

在 SKILL.md 的流程段开头添加两行自动执行命令：

```
!`python3 .claude/skills/xbase/skill-state.py check <skill名> 2>/dev/null`
!`python3 .claude/skills/xbase/skill-state.py read 2>/dev/null`
```

## 快速跳过逻辑

查看预加载结果：
- 输出 `initialized` → 已有状态信息可用 → **跳过整个阶段 0**
- `## 项目信息` 段已存在（其他 skill 写入）→ 直接复用项目类型、构建命令等，不再重复探测
- `## 项目信息` 中有 `运行脚本` 字段 → 跳过基础设施检查（如有）
- 输出 `not_found` → 执行完整探测流程

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

无产出物的 skill（如 xcommit、xdoc）不需要以上结构。

## 完整探测流程

1. **项目探测**：按 xbase SKILL.md 中的标准流程执行（扫描项目根目录、读 CLAUDE.md、确定项目关键信息）

2. **确定产出物目录**：读取 SKILL-STATE.md 的 `output_dir` 字段。如为空（首个 skill），探测项目文档目录（搜索 `docs/`/`doc/`/`document/` 等），写入 `output_dir`

3. **（各 skill 在此插入特有探测步骤）**
   - 有产出物的 skill：在 `output_dir` 下对核心文件做**三态检测**（不存在→生成 / 格式不符→问迁移 / 已就绪→跳过）

4. **写入 SKILL-STATE.md**：用脚本写入项目信息（如尚未写入）和 skill 特有字段：
   ```bash
   # 项目信息（首个 skill 写入，后续复用）
   python3 .claude/skills/xbase/skill-state.py write-info 类型 "<类型>" 构建命令 "<命令>" output_dir "<目录>" ...
   # skill 特有字段（含产出物路径）
   python3 .claude/skills/xbase/skill-state.py write <skill名> <key> <value> ...
   ```

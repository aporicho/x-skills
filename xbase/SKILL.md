---
name: xbase
description: xSkills 初始化与状态管理。一键探测项目、创建所有核心文件、查看状态。其他 skill 未初始化时自动调用 xbase。(xSkills init, status, shared base)
user-invocable: true
allowed-tools: ["Bash", "Read", "Edit", "Write", "Glob", "Grep", "AskUserQuestion"]
argument-hint: "[init | status]"
---

## 参数处理

根据 `$ARGUMENTS` 分发：

- **空** 或 **`init`** → `init`：全量初始化
- **`status`** → `status`：状态查看

## 预加载状态

!`python3 .claude/skills/xbase/scripts/skill-state.py read 2>/dev/null`

---

## `init`：全量初始化

先清空所有状态，确保从零开始：
```bash
python3 .claude/skills/xbase/scripts/skill-state.py reset-all
```

### 步骤 1 — 全面探测

> 一次性收集所有 skill 所需的项目信息和核心文件状态，后续步骤不重复探测。

**A. 项目信息**

!`cat .claude/skills/xbase/references/detect-steps.md`

> A 区探测完成后**立即执行 write-info 写入**（不等用户确认），B 区核心文件搜索依赖 `output_dir` 已就绪。

**B. 核心文件状态**（三态判定：✅ 已就绪 / 🔄 可改造 / ❌ 需新建）

对以下各 skill 声明的核心文件，在全项目范围搜索：

!`cat .claude/skills/xdebug/references/core-files.md`

!`cat .claude/skills/xtest/references/core-files.md`

!`cat .claude/skills/xlog/references/core-files.md`

!`cat .claude/skills/xcommit/references/core-files.md`

!`cat .claude/skills/xreview/references/core-files.md`

!`cat .claude/skills/xdoc/references/core-files.md`

!`cat .claude/skills/xdecide/references/core-files.md`

**展示探测结果**，等用户确认后进入步骤 2：

```
项目信息：
| 字段 | 值 |
|------|---|
| 类型 | ... |
| 构建命令 | ... |
| ... | ... |

核心文件状态：
| Skill | 文件 | 状态 |
|-------|------|------|
| xdebug | DEBUG-LOG.md | ✅ / 🔄 ← 旧文件路径 / ❌ |
| ... | ... | ... |
```

### 步骤 2 — 创建核心文件

对每个核心文件，根据三态判定：

- **❌ 需新建** → 在 `output_dir` 下创建（格式见各 `core-files.md` 中的格式规范引用）
- **🔄 可改造** → AskUserQuestion 询问是否迁移（保留内容，套用新格式）
- **✅ 已就绪** → 跳过创建

按以下顺序依次处理各 skill。三态判定已在步骤 1 确定，直接使用；每个 skill 处理完后无论三态结果如何，都执行 skill-state.py write 写入路径。

**xdebug**

!`cat .claude/skills/xdebug/references/init-steps.md`

---

**xtest**

!`cat .claude/skills/xtest/references/init-steps.md`

---

**xlog**

!`cat .claude/skills/xlog/references/init-steps.md`

---

**xcommit**

!`cat .claude/skills/xcommit/references/init-steps.md`

---

**xreview**

!`cat .claude/skills/xreview/references/init-steps.md`

---

**xdoc**

!`cat .claude/skills/xdoc/references/init-steps.md`

---

**xdecide**

!`cat .claude/skills/xdecide/references/init-steps.md`

### 步骤 3 — 去重

!`cat .claude/skills/xbase/references/dedup-steps.md`

### 步骤 4 — 汇总

展示所有核心文件的创建结果和项目信息概览。

---

## `status`：状态查看

1. 运行 `python3 .claude/skills/xbase/scripts/skill-state.py read`
2. 对每个 skill 检查 `initialized` 字段
3. 对每个核心文件路径用 Glob 确认文件存在
4. 展示汇总表：

```
xSkills 状态：

项目信息：
- output_dir：[值 / 未探测]
- 运行脚本：[值 / 未探测]

Skill 状态：
| Skill | 已初始化 | 核心文件 | 路径 | 文件存在 |
|-------|---------|---------|------|---------|
| xdebug | ✅ 2026-02-14 | DEBUG-LOG.md | document/DEBUG-LOG.md | ✅ |
| xtest  | ❌ | TEST-CHECKLIST.md | — | ❌ |
|        |    | TEST-ISSUES.md    | — | ❌ |
| ...    | | | | |
```

> 多核心文件的 skill（如 xtest）每个文件占一行，Skill 和已初始化列在首行填写，后续行留空。路径列展示 SKILL-STATE.md 中记录的实际路径，未记录时显示 `—`。



---
name: xbase
description: xSkills 初始化与状态管理。一键探测项目、初始化所有 skill、查看状态。(xSkills init, status, shared base)
user-invocable: true
allowed-tools: ["Bash", "Read", "Edit", "Write", "Glob", "Grep", "AskUserQuestion", "Task"]
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

### 步骤 1 — 集中探测

> 一次性收集所有信息，后续步骤直接使用结果。

**项目级**

!`python3 .claude/skills/xbase/scripts/extract-section.py xbase 探测`

**xdebug**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdebug 探测`

**xtest**

!`python3 .claude/skills/xbase/scripts/extract-section.py xtest 探测`

**xlog**

!`python3 .claude/skills/xbase/scripts/extract-section.py xlog 探测`

**xcommit**

!`python3 .claude/skills/xbase/scripts/extract-section.py xcommit 探测`

**xreview**

!`python3 .claude/skills/xbase/scripts/extract-section.py xreview 探测`

**xdoc**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdoc 探测`

**xdecide**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdecide 探测`

**展示探测结果**，等用户确认后进入步骤 2：

| Skill | 核心文件 | 状态 |
|-------|---------|------|
| xdebug | DEBUG-LOG.md | 需创建 / 迁移候选 / 已就绪 |
| xtest | TEST-CHECKLIST.md | 需全量生成 / 迁移候选 / 增量更新 |
| xtest | TEST-ISSUES.md | 需创建 / 迁移候选 / 已就绪 |
| xlog | LOG-RULES.md | 需创建 / 迁移候选 / 已就绪 |
| xlog | LOG-COVERAGE.md | 需创建 / 迁移候选 / 已就绪 |
| xcommit | COMMIT-RULES.md | 需创建 / 迁移候选 / 已就绪 |
| xreview | REVIEW-RULES.md | 需创建 / 迁移候选 / 已就绪 |
| xdoc | DOC-RULES.md | 需创建 / 迁移候选 / 已就绪 |
| xdecide | DECIDE-LOG.md | 需创建 / 迁移候选 / 已就绪 |

### 步骤 2 — 集中创建

> 根据步骤 1 结果执行，跳过已完成的探测。

**项目级**

!`python3 .claude/skills/xbase/scripts/extract-section.py xbase 创建`

---

**xdebug**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdebug 创建 去重`

---

**xtest**

!`python3 .claude/skills/xbase/scripts/extract-section.py xtest 创建 去重`

---

**xlog**

!`python3 .claude/skills/xbase/scripts/extract-section.py xlog 创建 去重`

---

**xcommit**

!`python3 .claude/skills/xbase/scripts/extract-section.py xcommit 创建 去重`

---

**xreview**

!`python3 .claude/skills/xbase/scripts/extract-section.py xreview 创建 去重`

---

**xdoc**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdoc 创建 去重`

---

**xdecide**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdecide 创建 去重`

### 步骤 3 — 汇总

展示所有核心文件的创建结果和项目信息概览。

---

## `status`：状态查看

1. 使用预加载状态（已在上方执行 `skill-state.py read`），对每个 skill 检查 `initialized` 字段
2. 对每个核心文件路径用 Glob 确认文件存在
3. 展示汇总表：

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



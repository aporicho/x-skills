---
name: xbase
description: xSkills 初始化与状态管理：一键探测项目、初始化所有 skill、查看状态。
allowed-tools: ["Bash", "Read", "Edit", "Write", "Glob", "Grep", "AskUserQuestion", "Task"]
argument-hint: "[init | status]"
---

### 参数处理（`$ARGUMENTS`）

根据 `$ARGUMENTS` 分发：

- **空** 或 **`init`** → `init`：全量初始化
- **`status`** → `status`：状态查看

### 预加载状态

!`python3 .claude/skills/xbase/scripts/skill-state.py read 2>/dev/null`

---

### `init`：全量初始化

先清空所有状态，确保从零开始：
```bash
python3 .claude/skills/xbase/scripts/skill-state.py reset-all
```

### 阶段 1：集中探测

> 一次性收集所有信息，后续阶段直接使用结果。

!`python3 .claude/skills/xbase/scripts/include.py xbase protocol-detection $ARGUMENTS`

**项目级**

!`python3 .claude/skills/xbase/scripts/include.py xbase xbase:探测 $ARGUMENTS`

**xdebug**

!`python3 .claude/skills/xbase/scripts/include.py xbase xdebug:探测 $ARGUMENTS`

**xlog**

!`python3 .claude/skills/xbase/scripts/include.py xbase xlog:探测 $ARGUMENTS`

**xtest**

!`python3 .claude/skills/xbase/scripts/include.py xbase xtest:探测 $ARGUMENTS`

**xreview**

!`python3 .claude/skills/xbase/scripts/include.py xbase xreview:探测 $ARGUMENTS`

**xcommit**

!`python3 .claude/skills/xbase/scripts/include.py xbase xcommit:探测 $ARGUMENTS`

**xdoc**

!`python3 .claude/skills/xbase/scripts/include.py xbase xdoc:探测 $ARGUMENTS`

**xdecide**

!`python3 .claude/skills/xbase/scripts/include.py xbase xdecide:探测 $ARGUMENTS`

**最终状态**（基于上方原始命中汇总推导），等用户确认后进入阶段 2：

| Skill | 核心文件 | 状态 | 废弃候选 |
|-------|---------|------|---------|
| xdebug | DEBUG-LOG.md | 需创建 / 迁移候选 / 已就绪 | （旧文件路径，无则留空） |
| xlog | LOG-RULES.md | 需创建 / 迁移候选 / 已就绪 | |
| xlog | LOG-COVERAGE.md | 需创建 / 迁移候选 / 已就绪 | |
| xtest | TEST-CHECKLIST.md | 需全量生成 / 迁移候选 / 增量更新 | |
| xtest | TEST-ISSUES.md | 需创建 / 迁移候选 / 已就绪 | |
| xreview | REVIEW-RULES.md | 需创建 / 迁移候选 / 已就绪 | |
| xcommit | COMMIT-RULES.md | 需创建 / 迁移候选 / 已就绪 | |
| xdoc | DOC-RULES.md | 需创建 / 迁移候选 / 已就绪 | |
| xdecide | DECIDE-LOG.md | 需创建 / 迁移候选 / 已就绪 | |

### 阶段 2：集中创建

> 根据阶段 1 结果执行，跳过已完成的探测。

!`python3 .claude/skills/xbase/scripts/include.py xbase protocol-creation $ARGUMENTS`

**项目级**

!`python3 .claude/skills/xbase/scripts/include.py xbase xbase:创建 $ARGUMENTS`

---

**xdebug**

!`python3 .claude/skills/xbase/scripts/include.py xbase xdebug:创建 $ARGUMENTS`

---

**xlog**

!`python3 .claude/skills/xbase/scripts/include.py xbase xlog:创建 $ARGUMENTS`

---

**xtest**

!`python3 .claude/skills/xbase/scripts/include.py xbase xtest:创建 $ARGUMENTS`

---

**xreview**

!`python3 .claude/skills/xbase/scripts/include.py xbase xreview:创建 $ARGUMENTS`

---

**xcommit**

!`python3 .claude/skills/xbase/scripts/include.py xbase xcommit:创建 $ARGUMENTS`

---

**xdoc**

!`python3 .claude/skills/xbase/scripts/include.py xbase xdoc:创建 $ARGUMENTS`

---

**xdecide**

!`python3 .claude/skills/xbase/scripts/include.py xbase xdecide:创建 $ARGUMENTS`

### 阶段 3：集中清理

> 所有核心文件已就位，一次性清理废弃文件和 CLAUDE.md 重复内容。

!`python3 .claude/skills/xbase/scripts/include.py xbase protocol-cleanup $ARGUMENTS`

**xdebug**

!`python3 .claude/skills/xbase/scripts/include.py xbase xdebug:清理 $ARGUMENTS`

**xlog**

!`python3 .claude/skills/xbase/scripts/include.py xbase xlog:清理 $ARGUMENTS`

**xtest**

!`python3 .claude/skills/xbase/scripts/include.py xbase xtest:清理 $ARGUMENTS`

**xreview**

!`python3 .claude/skills/xbase/scripts/include.py xbase xreview:清理 $ARGUMENTS`

**xcommit**

!`python3 .claude/skills/xbase/scripts/include.py xbase xcommit:清理 $ARGUMENTS`

**xdoc**

!`python3 .claude/skills/xbase/scripts/include.py xbase xdoc:清理 $ARGUMENTS`

**xdecide**

!`python3 .claude/skills/xbase/scripts/include.py xbase xdecide:清理 $ARGUMENTS`

### 阶段 4：汇总

展示所有核心文件的创建结果和项目信息概览。

---

### `status`：状态查看

1. 使用预加载状态（已在上方执行 `skill-state.py read`），直接格式化展示
2. 展示汇总表：

```
xSkills 状态：

项目信息：
- output_dir：[值 / 未探测]
- 运行脚本：[值 / 未探测]

Skill 状态：
| Skill | 已初始化 | 核心文件 | 路径 |
|-------|---------|---------|------|
| xdebug | ✅ 2026-02-20 | DEBUG-LOG.md | document/90-开发/DEBUG-LOG.md |
| xlog | ❌ | LOG-RULES.md | — |
| xlog | ❌ | LOG-COVERAGE.md | — |
| xtest | ❌ | TEST-CHECKLIST.md | — |
| xtest | ❌ | TEST-ISSUES.md | — |
| xreview | ❌ | REVIEW-RULES.md | — |
| xcommit | ❌ | COMMIT-RULES.md | — |
| xdoc | ❌ | DOC-RULES.md | — |
| xdecide | ❌ | DECIDE-LOG.md | — |
```

> 多核心文件的 skill（如 xtest）每个文件占一行，每行都填写完整的 Skill 名和初始化状态。路径列展示 SKILL-STATE.md 中记录的实际路径，未记录时显示 `—`。

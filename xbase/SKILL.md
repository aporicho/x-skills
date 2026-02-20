---
name: xbase
description: xSkills 初始化与状态管理：一键探测项目、初始化所有 skill、查看状态。
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

**CRITICAL — 三路并行探测协议**（适用于所有核心文件）：

每个核心文件有三路互补搜索，每路都有盲区，缺任何一路都会漏文件：
- **精确名** Glob — 漏：改过名的文件
- **指纹** Grep — 漏：内容已变或为空的文件
- **模糊名** Glob — 漏：名称无相关关键词的文件

执行规则：
1. **同批并行发出**：三路 Glob/Grep 必须在同一批 tool call 中发出，禁止看到某路结果后再决定是否跑其余
2. **收齐后再判定**：汇总去重（排除 `.claude/`、`node_modules/`、`.git/`、`build/`、`target/`、`vendor/`、`DerivedData/`），对每个候选用内容指纹 regex 判格式：命中 → 已就绪，未命中（含空文件）→ 迁移候选
3. **优先级**：output_dir 内 > 项目根 > 其他；精确文件名 > 非精确；已就绪 > 迁移候选
4. **冲突**：多个已就绪 → AskUserQuestion 选规范文件，其余标记废弃候选
5. **无候选** → 需创建

**展示原始命中**（确保三路都有数值，0 也要写）：

| 核心文件 | 精确名 | 指纹 | 模糊名 | 去重后候选 |
|---------|-------|------|-------|-----------|
| DEBUG-LOG.md | 1 | 1 | 2 | 2 |
| ... | | | | |

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

**最终状态**（基于上方原始命中汇总推导），等用户确认后进入步骤 2：

| Skill | 核心文件 | 状态 | 废弃候选 |
|-------|---------|------|---------|
| xdebug | DEBUG-LOG.md | 需创建 / 迁移候选 / 已就绪 | （旧文件路径，无则留空） |
| xtest | TEST-CHECKLIST.md | 需全量生成 / 迁移候选 / 增量更新 | |
| xtest | TEST-ISSUES.md | 需创建 / 迁移候选 / 已就绪 | |
| xlog | LOG-RULES.md | 需创建 / 迁移候选 / 已就绪 | |
| xlog | LOG-COVERAGE.md | 需创建 / 迁移候选 / 已就绪 | |
| xcommit | COMMIT-RULES.md | 需创建 / 迁移候选 / 已就绪 | |
| xreview | REVIEW-RULES.md | 需创建 / 迁移候选 / 已就绪 | |
| xdoc | DOC-RULES.md | 需创建 / 迁移候选 / 已就绪 | |
| xdecide | DECIDE-LOG.md | 需创建 / 迁移候选 / 已就绪 | |

### 步骤 2 — 集中创建

> 根据步骤 1 结果执行，跳过已完成的探测。

**项目级**

!`python3 .claude/skills/xbase/scripts/extract-section.py xbase 创建`

---

**xdebug**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdebug 创建`

---

**xtest**

!`python3 .claude/skills/xbase/scripts/extract-section.py xtest 创建`

---

**xlog**

!`python3 .claude/skills/xbase/scripts/extract-section.py xlog 创建`

---

**xcommit**

!`python3 .claude/skills/xbase/scripts/extract-section.py xcommit 创建`

---

**xreview**

!`python3 .claude/skills/xbase/scripts/extract-section.py xreview 创建`

---

**xdoc**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdoc 创建`

---

**xdecide**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdecide 创建`

### 步骤 3 — 集中清理

> 所有核心文件已就位，一次性清理废弃文件和 CLAUDE.md 重复内容。

**xdebug**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdebug 清理`

**xtest**

!`python3 .claude/skills/xbase/scripts/extract-section.py xtest 清理`

**xlog**

!`python3 .claude/skills/xbase/scripts/extract-section.py xlog 清理`

**xcommit**

!`python3 .claude/skills/xbase/scripts/extract-section.py xcommit 清理`

**xreview**

!`python3 .claude/skills/xbase/scripts/extract-section.py xreview 清理`

**xdoc**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdoc 清理`

**xdecide**

!`python3 .claude/skills/xbase/scripts/extract-section.py xdecide 清理`

### 步骤 4 — 汇总

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



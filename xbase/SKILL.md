---
name: xbase
description: xSkills 初始化与状态管理：一键探测项目、初始化所有 skill、查看状态。
allowed-tools: ["Bash", "Read", "Edit", "Write", "Glob", "Grep", "AskUserQuestion", "Task"]
argument-hint: "[ensure | init | reinit <skill> | status]"
---

### D1. 参数处理（`$ARGUMENTS`）

根据 `$ARGUMENTS` 分发：

- **空** 或 **`ensure`** → `ensure`：补充初始化
- **`init`** → `init`：全量初始化（reset-all）
- **`reinit <skill>`** → `reinit`：重新初始化指定 skill
- **`status`** → `status`：状态查看

### 预加载状态

!`python3 .claude/skills/xbase/scripts/state.py read 2>/dev/null`

---

### `ensure`：补充初始化

读取预加载状态，识别未初始化的 skill（无 `initialized` 值的段）。

- 全部已初始化 → 输出"所有 skill 已初始化"，按 `status` 格式展示，结束
- 有未初始化的 → 仅对未初始化的 skill 执行阶段 1-4（流程与 init 相同，但不执行 reset-all，跳过已初始化的 skill）

---

### `reinit <skill>`：重新初始化指定 skill

1. 删除状态：`python3 .claude/skills/xbase/scripts/state.py delete <skill>`
2. 按 `ensure` 流程处理（只会处理刚删除的那个 skill）

---

### `init`：全量初始化

先清空所有状态，确保从零开始：
```bash
python3 .claude/skills/xbase/scripts/state.py reset-all
```

### D2. 阶段 1：集中探测

> 一次性收集所有信息，后续阶段直接使用结果。

1. 读取探测协议：`.claude/skills/xbase/references/protocol-detection.md`
2. 对每个待初始化 skill，读取其 `references/artifacts.md` 的 `## 探测` 段：
   - 项目级：`.claude/skills/xbase/references/artifacts.md`
   - xdebug：`.claude/skills/xdebug/references/artifacts.md`
   - xlog：`.claude/skills/xlog/references/artifacts.md`
   - xtest：`.claude/skills/xtest/references/artifacts.md`
   - xreview：`.claude/skills/xreview/references/artifacts.md`
   - xcommit：`.claude/skills/xcommit/references/artifacts.md`
   - xdoc：`.claude/skills/xdoc/references/artifacts.md`
   - xdecide：`.claude/skills/xdecide/references/artifacts.md`
3. 按协议和各 skill 探测声明执行探测

展示**最终状态**表（基于上方原始命中汇总推导）：

| Skill | 制品文件 | 状态 | 废弃候选 |
|-------|---------|------|---------|
| xbase | RUN.sh | 需创建 / 迁移候选 / 需更新 / 已就绪 | （旧文件路径，无则留空） |
| xdebug | DEBUG_LOG.md | 需创建 / 迁移候选 / 需更新 / 已就绪 | |
| xlog | LOG_RULES.md | 需创建 / 迁移候选 / 需更新 / 已就绪 | |
| xtest | TEST_CHECKLIST.md | 需创建 / 迁移候选 / 需更新 / 已就绪 | |
| xtest | TEST_ISSUES.md | 需创建 / 迁移候选 / 需更新 / 已就绪 | |
| xreview | REVIEW_RULES.md | 需创建 / 迁移候选 / 需更新 / 已就绪 | |
| xcommit | COMMIT_RULES.md | 需创建 / 迁移候选 / 需更新 / 已就绪 | |
| xdoc | DOC_RULES.md | 需创建 / 迁移候选 / 需更新 / 已就绪 | |
| xdecide | DECIDE_LOG.md | 需创建 / 迁移候选 / 需更新 / 已就绪 | |

**快捷路径**：如果全部已就绪且无废弃候选 → 跳过阶段 2-3，直接写入状态并进入阶段 4 汇总（无需等待用户确认）。否则等待用户确认后进入阶段 2。

### D3. 阶段 2：集中创建

> 根据阶段 1 的四态结果，对每个制品文件执行对应处理。

1. 读取创建协议：`.claude/skills/xbase/references/protocol-creation.md`
2. 对每个需创建/迁移/更新的 skill，读取其 `references/artifacts.md` 的 `## 创建` 段
3. 按协议和各 skill 创建声明执行创建

### D4. 阶段 3：集中清理

> 所有制品文件已就位，一次性清理废弃文件和 CLAUDE.md 重复内容。

1. 读取清理协议：`.claude/skills/xbase/references/protocol-cleanup.md`
2. 对每个有废弃候选的 skill，读取其 `references/artifacts.md` 的 `## 清理` 段（如有）
3. 按协议执行清理

### D5. 阶段 4：汇总

按下方 `status` 格式展示所有制品文件状态和项目信息概览。

---

### `status`：状态查看

1. 使用预加载状态（已在上方执行 `state.py read`），直接格式化展示
2. 展示汇总表：

```
xSkills 状态：

| 项目信息 | 值 |
|---------|------|
| doc_dir | [值 / 未探测] |

| Skill | 已初始化 | 制品文件 | 路径 |
|-------|---------|---------|------|
| xbase | ✅ 2026-02-21 | RUN.sh | scripts/RUN.sh |
| xdebug | ✅ 2026-02-20 | DEBUG_LOG.md | document/90-开发/DEBUG_LOG.md |
| xlog | ❌ | LOG_RULES.md | — |
| xtest | ❌ | TEST_CHECKLIST.md | — |
| xtest | ❌ | TEST_ISSUES.md | — |
| xreview | ❌ | REVIEW_RULES.md | — |
| xcommit | ❌ | COMMIT_RULES.md | — |
| xdoc | ❌ | DOC_RULES.md | — |
| xdecide | ❌ | DECIDE_LOG.md | — |
```

> 多制品文件的 skill（如 xtest）每个文件占一行，每行都填写完整的 Skill 名和初始化状态。路径列展示 SKILL-STATE.md 中记录的实际路径，未记录时显示 `—`。

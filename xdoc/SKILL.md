---
name: xdoc
description: 文档维护工作流。用户输入 /xdoc 时激活。基于 DOC-RULES.md 进行文档健康检查 + 代码-文档一致性验证。当用户要维护文档、检查文档质量时也适用。
user-invocable: true
allowed-tools: ["Bash", "Read", "Edit", "Write", "Grep", "Glob", "AskUserQuestion"]
argument-hint: "[健康检查 | 一致性 | reinit]"
---

### 参数处理（`$ARGUMENTS`）

> **执行顺序**：无论参数如何，阶段 0 的快速跳过检查始终先执行。参数仅影响阶段 1 及之后的跳转。

- **空** → 正常走阶段 1 询问
- **`reinit`** → 删除 SKILL-STATE.md 中 `## xdoc` 段（`python3 .claude/skills/xbase/scripts/skill-state.py delete xdoc`）+ 重新执行阶段 0（忽略预加载的 check 结果，delete 后强制执行完整阶段 0）
- **`健康检查`** → 跳过阶段 1，直接进入阶段 2a
- **`一致性`** → 跳过阶段 1，直接进入阶段 2b
- **其他文本** → 作为指定文件/目录路径，执行该路径的健康检查

### 核心文件

| 文件 | 说明 | 格式规范 |
|------|------|----------|
| `DOC-RULES.md` | 文档规范（目录结构 + 检查脚本 + 映射规则） | `references/doc-rules-format.md` |

### 预加载状态
!`python3 .claude/skills/xbase/scripts/skill-state.py check-and-read xdoc 2>/dev/null`

### 阶段 0：探测项目

!`cat .claude/skills/xbase/references/prep-steps.md`

以下为本 skill 的特有探测步骤：

!`cat .claude/skills/xdoc/references/init-steps.md`

### 阶段 1：选择任务

用 AskUserQuestion：

```
问题：文档维护。选择操作：
选项：
- 健康检查（断链、格式、结构）
- 一致性验证（代码 ↔ 文档）
- 指定文件检查
- Other → 输入具体需求
```

### 阶段 2a：健康检查

读取 DOC-RULES.md 获取检查规则：

1. **运行检查脚本**（从 DOC-RULES.md「检查脚本」列表获取）：
   - 逐个运行，捕获输出
   - 汇总每个脚本发现的问题

2. **格式规范检查**（按 DOC-RULES.md「格式规范」执行）：
   - 扫描 markdown 文件中的链接，验证内部链接指向的文件存在
   - 检查标题层级规范
   - 检查代码块是否标注语言
   - 检查是否存在空文件或只有标题的占位文件

3. **汇总问题清单**：按严重程度排序（断链 > 格式 > 建议）

### 阶段 2b：一致性验证

1. **获取最近代码变更**：
   - 运行 `git log --oneline -20` 查看最近提交
   - 运行 `git diff HEAD~5..HEAD --stat` 查看最近 5 次提交的变更文件

2. **读取 DOC-RULES.md「代码-文档映射」**，对照变更文件识别应更新的文档

3. **检查映射项是否一致**：
   - 代码变更的提交中是否包含对应文档更新
   - 文档描述是否与当前代码一致

4. **汇总不一致清单**

### 阶段 3：修复

对汇总的问题清单，逐项用 AskUserQuestion：

```
问题：[问题类型] [文件路径]
  问题：[描述]
  建议修复：[方案]
选项：
- 自动修复
- 手动处理（跳过）
- 忽略
```

选择"自动修复"时：执行修复，确认结果。

**批量修复后验证**：如果修改了 10 个以上文件，按 DOC-RULES.md「批量编辑验证」中指定的脚本运行验证。

### 阶段 4：汇报

用 AskUserQuestion：

```
问题：文档维护完成。
  检查 N 个文件，发现 X 个问题（已修复 Y / 跳过 Z）。
  下一步？
选项：
- 重新检查（确认修复效果）
- 提交变更（→ /xcommit）
- 结束
```

---

## 关键原则

- **规则从文件读取** — 文档目录、检查脚本、映射规则基于 DOC-RULES.md，`reinit` 时重新生成
- **脚本优先** — DOC-RULES.md 中有检查脚本就用，没有才用内置基础检查
- **逐项决策** — 每个问题单独决策，不批量处理
- **批量修复后验证** — 10+ 文件修改后按 DOC-RULES.md 运行验证脚本
- **一致性检查优先最近变更** — 聚焦最近几次提交，不全量扫描
- **选项优先于打字** — Other 兜底自由输入
- **每轮只问一个问题** — 不堆叠

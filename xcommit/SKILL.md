---
name: xcommit
description: 提交工作流：基于 COMMIT-RULES.md 自动预检 + 文档完整性检查 + 规范化提交。当用户要提交代码、保存变更时使用。
allowed-tools: ["Bash", "Read", "Edit", "Write", "Grep", "Glob", "AskUserQuestion"]
argument-hint: "[commit消息]"
---

### 参数处理（`$ARGUMENTS`）

- **空** → 正常走全流程（自动生成 commit message）
- **其他文本** → 作为 commit message 候选，跳到阶段 1（阶段 5 时优先使用此消息）

### 核心文件

| 文件 | 说明 | 格式规范 |
|------|------|----------|
| `COMMIT-RULES.md` | 提交规范（git log 分析 + CLAUDE.md 提取） | `references/commit-rules-guideline.md` |

### 预加载状态
!`python3 .claude/skills/xbase/scripts/state.py check-and-read xcommit 2>/dev/null`

### 初始化检查

查看上方预加载输出：
- 含 `initialized` → 跳过，进入阶段 1
- 含 `not_found` → 输出"xcommit 尚未初始化，请先运行 `/xbase`"，停止

### 阶段 1：检查变更

1. 运行 git-context.py 收集上下文：
   ```bash
   python3 .claude/skills/xcommit/scripts/git-context.py commit-context
   ```
   输出包含 status、diff_stat、cached_diff、recent_log、commit_style 等。

**分支判断**：
- **无变更（工作区干净）** → 提示"无变更需要提交"，结束
- **全部已暂存** → 直接进入阶段 2
- **有未暂存变更** → 用 AskUserQuestion：

```
问题：有以下未暂存文件：
  [文件列表]
  如何处理？
选项：
- 全部暂存
- 选择暂存（展示文件列表）
- 仅提交已暂存的
- Other → 指定文件
```

**暂存操作**：用具体文件名 `git add <file1> <file2> ...`，不用 `git add -A` 或 `git add .`。

### 阶段 2：审查确认

用 AskUserQuestion：

```
问题：变更已就绪，提交前是否需要审查代码？
选项：
- 跳过审查，继续提交
- 先审查（→ /xreview）
```

选择"先审查"时：提示用户运行 `/xreview` 审查未提交变更，审查完成后再运行 `/xcommit` 继续提交，结束当前流程。

### 阶段 3：预检

读取 COMMIT-RULES.md 中的「预检脚本」列表，逐个运行：

1. 运行每个脚本，捕获输出
2. **全部通过** → 继续阶段 4
3. **有失败** → 用 AskUserQuestion：

```
问题：预检脚本 [脚本名] 失败：
  [失败摘要]
  如何处理？
选项：
- 自动修复（尝试修复后重新运行）
- 跳过此检查
- 取消提交
```

选择"自动修复"时：分析失败原因，尝试修复，重新运行预检脚本验证。

> 如果没有探测到预检脚本，跳过此阶段。

### 阶段 4：文档完整性

**不阻断提交，仅给出建议。**

1. 运行 `git diff --cached` 分析已暂存的变更
2. 推断变更类型：
   - **Bug 修复**：diff 中包含修复逻辑、测试修复、错误处理变更
   - **架构变更**：新增/删除模块、依赖关系变更、接口变更
   - **新功能**：新增文件/函数/命令
3. 读取 COMMIT-RULES.md 中的「文档完整性检查 → 变更类型 → 文档映射」，检查对应文档是否在暂存中
4. **疑似遗漏** → 用 AskUserQuestion：

```
问题：本次提交看起来是 [Bug 修复]，但 [DEBUG-LOG.md] 未在暂存中。
  可能需要更新文档？
选项：
- 先补文档再提交（暂停，用户补充后重新运行 /xcommit）
- 不需要，继续提交
- Other → 说明情况
```

**无遗漏** → 直接进入阶段 5。

### 阶段 5：生成提交

1. **生成 commit message**：
   - 如果参数已提供 message → 优先使用
   - 否则：参照 COMMIT-RULES.md 中的「提交消息风格」，分析 `git diff --cached` 生成 message
   - 总结变更性质（新功能/增强/Bug修复/重构/文档等）
   - 确保 message 准确反映变更内容和目的

2. **展示确认** — 用 AskUserQuestion：

```
问题：准备提交。
  文件列表：
  [git diff --cached --stat 输出]

  Commit message：
  [生成的 message]
选项：
- 确认提交
- 修改 message
- 取消
- Other → 输入新 message
```

3. **执行提交**：
   ```bash
   git commit -m "$(cat <<'EOF'
   <message>
   EOF
   )"
   ```

4. 运行 `git status` 确认提交成功。

### 阶段 6：决策回顾

回顾本次变更的 diff 和对话上下文，检测是否包含隐式决策——架构选择、方案取舍、技术选型、"先不做 X" 等取舍。

**检测到疑似决策时**，用 AskUserQuestion：

```
问题：本次工作中检测到以下疑似决策：
  1. [决策描述]
  2. [决策描述]
  需要记录吗？
选项：
- 记录（→ /xdecide）
- 不需要
```

**未检测到时**，用 AskUserQuestion：

```
问题：提交完成。本次工作中有需要记录的决策吗？
选项：
- 有（→ /xdecide）
- 没有
```

---

## 关键原则

- **规则从文件读取** — 预检脚本、文档映射、commit 风格基于 COMMIT-RULES.md，`/xbase reinit xcommit` 时重新生成
- **全量暂存检查** — 展示完整文件列表，确认无遗漏
- **文档完整性是建议不是阻断** — 提醒但不阻止提交
- **不用 `git add -A`** — 用具体文件名暂存，避免意外包含敏感文件
- **commit message 遵循项目风格** — 按 COMMIT-RULES.md 中的风格规范
- **展示文件列表** — 提交前展示完整变更文件列表
- **选项优先于打字** — Other 兜底自由输入
- **每轮只问一个问题** — 不堆叠
- **提交前审查锚点** — 每次提交前固定询问是否需要代码审查，不依赖用户记忆
- **提交后决策捕获** — 提交成功后 AI 主动检测对话中的隐式决策，提醒记录
- **不推送** — 只做本地 commit，不自动 push（除非用户明确要求）

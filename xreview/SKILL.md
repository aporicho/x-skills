---
name: xreview
description: 代码审查工作流：基于 REVIEW-RULES.md 三维度审查（规范/架构/安全），逐项决策。当用户要审查代码、做 code review 时使用。
allowed-tools: ["Bash", "Read", "Edit", "Write", "Grep", "Glob", "AskUserQuestion"]
argument-hint: "[文件/目录路径 | reinit]"
---

### 参数处理（`$ARGUMENTS`）

> **执行顺序**：无论参数如何，阶段 0 的快速跳过检查始终先执行。参数仅影响阶段 1 及之后的跳转。

- **空** → 正常走阶段 1 询问
- **`reinit`** → 删除 SKILL-STATE.md 中 `## xreview` 段（`python3 .claude/skills/xbase/scripts/skill-state.py delete xreview`）+ 重新执行阶段 0（忽略预加载的 check 结果，delete 后强制执行完整阶段 0）
- **其他文本** → 作为审查目标路径，跳过阶段 1 直接进入阶段 2

### 核心文件

| 文件 | 说明 | 格式规范 |
|------|------|----------|
| `REVIEW-RULES.md` | 审查规范（代码扫描 + CLAUDE.md 提取） | `references/review-rules-format.md` |

### 预加载状态
!`python3 .claude/skills/xbase/scripts/skill-state.py check-and-read xreview 2>/dev/null`

### 阶段 0：探测项目

!`cat .claude/skills/xbase/references/protocol-prep.md`

!`cat .claude/skills/xbase/references/protocol-detection.md`

!`cat .claude/skills/xreview/references/artifacts.md`

!`cat .claude/skills/xbase/references/protocol-cleanup.md`

### 阶段 1：确定范围

用 AskUserQuestion：

```
问题：审查什么代码？
选项：
- 未提交变更（git diff）
- 最近一次提交（git show HEAD）
- 指定路径
- Other → 输入路径或 git range
```

### 阶段 2：执行审查

**获取目标代码**：
- 未提交变更 → `git diff` + `git diff --cached`
- 最近提交 → `git show HEAD`
- 指定路径 → 读取文件

**上下文感知**：根据变更类型调整审查重点：
- **Bug 修复** → 重点检查是否真正修复了根因、是否引入新问题、边界条件
- **新功能** → 重点检查架构一致性、接口设计、扩展性
- **重构** → 重点检查行为一致性、依赖关系、是否遗漏

**获取审查规则**：读取 REVIEW-RULES.md（路径从 SKILL-STATE.md 的 `review_rules` 字段获取）。

**三维度审查**：

#### A. 规范合规

逐条核对 REVIEW-RULES.md `## A. 规范合规` 中的规则：
- 禁忌类：是否违反任何禁止规则
- 必须类：是否遵守所有必须规则
- 编码规范：命名、缩进、注释语言等是否一致

#### B. 架构质量

- 依赖方向：是否违反分层依赖（如内层依赖外层）
- 职责划分：新增代码是否放在正确的模块
- 重复代码：是否存在可合并的重复逻辑
- 接口设计：API 是否清晰、错误处理是否完善

#### C. 安全健壮

- 边界条件：空值、越界、类型转换
- 并发安全：共享状态、线程安全
- 资源管理：内存泄漏、文件句柄、循环引用
- 安全漏洞：注入、XSS、权限检查

**逐项反馈**：每发现一个问题，用 AskUserQuestion：

```
问题：[维度] 发现问题：
  文件：[path:line]
  问题：[描述]
  建议：[修复方案]
选项：
- 立即修复
- 记录到重构清单
- 记录决策（→ /xdecide，将架构问题描述作为参数）
- 忽略
```

选择"立即修复"时：执行修复 → 读取修复后代码确认 → 继续审查下一项。

**无问题时**：如果审查完毕未发现问题，直接告知结果并进入阶段 3。

### 阶段 3：收尾

汇总审查结果，用 AskUserQuestion：

```
问题：审查完成。发现 N 个问题（已修复 X / 记录 Y / 忽略 Z）。下一步？
选项：
- 提交变更（→ /xcommit）
- 记录决策（→ /xdecide）
- 继续审查其他代码（→ 回阶段 1）
- 结束
```

---

## 关键原则

- **规则从文件读取** — 审查基于 REVIEW-RULES.md，`reinit` 时重新生成
- **三维度不遗漏** — 规范合规、架构质量、安全健壮全覆盖
- **逐项决策** — 每个问题单独决策，不堆叠
- **修复即时验证** — 修复后读取代码确认，不盲信
- **上下文感知** — 根据变更类型（Bug修复/新功能/重构）调整审查重点
- **不硬编码** — 规则从代码扫描 + CLAUDE.md 提取，适用于任何项目
- **选项优先于打字** — Other 兜底自由输入
- **每轮只问一个问题** — 不堆叠

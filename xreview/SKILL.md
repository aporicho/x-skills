---
name: xreview
description: 代码审查工作流。用户输入 /xreview 时激活。基于 REVIEW-RULES.md 三维度审查，逐项决策。
allowed-tools: ["Bash", "Read", "Edit", "Write", "Grep", "Glob", "AskUserQuestion", "Task"]
argument-hint: "[文件/目录路径 | reinit]"
---

# 代码审查工作流

## 目录

- [阶段 0：探测项目](#阶段-0探测项目)
- [阶段 1：确定范围](#阶段-1确定范围)
- [阶段 2：执行审查](#阶段-2执行审查)
- [阶段 3：收尾](#阶段-3收尾)
- [关键原则](#关键原则)

## 启动方式

- 用户输入 `/xreview` 时激活

### 参数处理（`$ARGUMENTS`）

- **空** → 正常走阶段 1 询问
- **`reinit`** → 删除 SKILL-STATE.md 中 `## xreview` 段（`python3 .claude/skills/xbase/skill-state.py delete xreview`）+ 重新执行阶段 0
- **其他文本** → 作为审查目标路径，跳过阶段 1 直接进入阶段 2

## 核心文件

| 文件 | 说明 | 格式规范 |
|------|------|----------|
| `REVIEW-RULES.md` | 审查规范（代码扫描 + CLAUDE.md 提取） | `references/review-rules-format.md` |

## 流程

### 预加载状态
!`python3 .claude/skills/xbase/skill-state.py check xreview 2>/dev/null`
!`python3 .claude/skills/xbase/skill-state.py read 2>/dev/null`

### 阶段 0：探测项目

> 按 `references/phase0-template.md` 标准流程执行。特有探测步骤：

1. **REVIEW-RULES.md 三态检测**：
   - **不存在** → 在 `output_dir` 下生成（执行步骤 2）
   - **存在但格式不符**（缺少 A/B/C 三维度章节）→ 用 AskUserQuestion 问是否重新生成（保留旧文件为 `.bak`）
   - **已就绪** → 跳过生成，直接步骤 3

2. **生成 REVIEW-RULES.md**（按 `references/review-rules-format.md` 格式）：

   规则来源两层：

   **a) CLAUDE.md 提取**（如存在）：
   - **禁忌类**：搜索"禁止"/"NEVER"/"不要"/"绝对不"等关键词，提取禁止事项
   - **必须类**：搜索"必须"/"MUST"/"IMPORTANT"/"CRITICAL"等关键词，提取必须遵守的规则
   - **规范类**：搜索"规范"/"风格"/"命名"/"格式"等关键词，提取编码规范
   - **架构类**：搜索"架构"/"依赖"/"层"/"模块"/"耦合"等关键词，提取架构约束

   **b) 代码扫描推导**（始终执行，不依赖 CLAUDE.md 存在）：
   - **缩进风格**：扫描源文件判断 tab/空格、缩进宽度
   - **命名风格**：扫描函数/变量名判断 camelCase/snake_case 等
   - **注释语言**：扫描注释判断中文/英文
   - **目录结构**：扫描项目目录推导架构分层
   - **错误处理模式**：扫描 guard/try-catch/Result 等模式
   - **项目特有安全检查点**：根据技术栈推导（如 FFI 项目检查内存安全、Web 项目检查 XSS 等）

   来源标记：每条规则标注来源为 `CLAUDE.md` 或 `代码扫描`，便于维护。

3. **写入状态**：`python3 .claude/skills/xbase/skill-state.py write xreview review_rules <REVIEW-RULES.md路径>`

4. **去重子步骤**（阶段 0 最后执行）：

   产出物创建/确认就绪后，扫描 CLAUDE.md 和 MEMORY.md，将本 skill 产出物已覆盖的详细内容替换为指针。

   **原则**：
   - 每次对话都需要的**方法论/禁令/哲学** → 保留原文
   - 已被产出物详细覆盖的**具体规范** → 替换为一句话 + 文件路径
   - 修改前展示 diff 预览，等用户确认

   **去重职责**：
   - CLAUDE.md `## 代码规范` 段中的具体条目（4 空格缩进、中文注释、guard 提前退出、MARK 组织、避免强制解包）→ 已被 REVIEW-RULES.md 覆盖，替换为：`代码规范详见 REVIEW-RULES.md（路径见 SKILL-STATE.md）`
   - CLAUDE.md 中「避免强制解包」「禁止 print()」等 → 「禁止 print()」是禁令需**保留**，其余具体规范条目已迁移

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
- 记录决策（→ /xdecide）
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

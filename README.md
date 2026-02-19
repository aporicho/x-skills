# xSkills

Claude Code 自定义工作流 skill 集合 — 用 `/x*` 命令驱动调试、测试、日志、审查、提交、文档、决策的完整开发循环。

**核心理念**：每个 skill 都是"阶段化推进的交互式工作流"，通过 `AskUserQuestion` 选项一步步引导，可独立使用也可互相衔接。skill 自动适配任何项目（不硬编码路径和命令）。

## Quick Start

```bash
/xbase   init          # 一键初始化所有 skill（探测项目 → 并行创建产出物 → 去重）
/xdebug  拖拽偏移      # 直接开始调试一个 bug
/xtest   手动          # 启动手动测试流程
/xcommit               # 预检 + 文档完整性 + 规范化提交
/xbase   status        # 查看所有 skill 的初始化状态
```

各 skill 可独立运行（首次使用时自动初始化），`/xbase init` 只是批量快捷入口。

---

## 整体架构

### 两层结构

```
┌─────────────────────────────────────────────────────────────────────┐
│  7 个工作流 skill（按使用顺序）                                     │
│  xtest → xdebug → xlog → xreview → xdecide → xdoc → xcommit   │
├─────────────────────────────────────────────────────────────────────┤
│  xbase — 共享基础设施 + 各 skill 领域脚本                          │
│  共享：状态管理 · 项目探测 · 产出物检测 · 去重 (xbase/scripts/)     │
│  领域：Git 上下文 (xcommit/scripts/) · Bug 队列 (xtest/scripts/)    │
│         决策记录 (xdecide/scripts/)                                 │
└─────────────────────────────────────────────────────────────────────┘
```

- **上层**：7 个工作流 skill，每个有自己的 `SKILL.md`（定义阶段和流程）和 `references/` 目录（格式规范）
- **下层**：共享工具在 `xbase/scripts/`，领域工具在各 skill 的 `scripts/` 下（如 `xcommit/scripts/git-context.py`）

### 三类文件

| 类别 | 位置 | 作用 | 谁读 |
|------|------|------|------|
| **SKILL.md** | 每个 skill 目录下 | Claude 读取后知道怎么执行工作流 | Claude（prompt） |
| **references/*.md** | 每个 skill 的 references/ | 产出物的格式规范，生成时参照 | Claude（生成时参考） |
| **产出物** | 目标项目的文档目录 | skill 运行后创建的实际文件 | Claude + 用户 |

**一句话总结**：SKILL.md 告诉 Claude "做什么"，references/ 告诉 Claude "格式长什么样"，产出物是最终结果。

---

## 每个 Skill 详解

> 按**典型使用顺序**排列：先初始化 → 测试发现问题 → 调试修复 → (补日志) → 审查代码 → (记录决策) → (维护文档) → 提交。括号内的 skill 是按需触发，不一定每次都用。

### 0. xbase — 初始化与状态管理（前置：一切的起点）

**做什么**：一键初始化所有 skill 的运行环境（探测项目 → 创建产出物 → 去重），管理共享状态，提供所有 skill 复用的 Python 工具。

**典型触发时机**：首次使用 xSkills 时运行 `/xbase init`；之后各 skill 首次使用会自动初始化，不需要手动再跑。

**命令**：
| 命令 | 做什么 |
|------|--------|
| `/xbase init` | 探测项目 → 并行初始化 7 个 skill 的阶段 0 → 串行去重 |
| `/xbase status` | 查看所有 skill 的初始化状态 + 产出物健康度 |
| `/xbase reset` | 清空状态重新来过（会确认） |
| `/xbase reinit` | 清空项目信息 + 重新执行 init |

**管理的共享资源**：
- `SKILL-STATE.md` — 所有 skill 的运行时状态（项目类型、路径、初始化日期）
- 3 个共享 Python 工具（`xbase/scripts/`）— 状态管理、产出物检测、去重扫描
- 3 个领域 Python 工具 — Git 上下文（`xcommit/scripts/`）、Bug 队列（`xtest/scripts/`）、决策记录（`xdecide/scripts/`）

**关键设计**：xbase 自身不创建任何工作产出物，只做编排 — "谁的产出物谁负责创建"。`/xbase init` 启动 7 个并行 Task 子 agent，各自执行自己的阶段 0。

#### 执行流程

**`/xbase init`（或空参数）**：

1. **预加载**：`skill-state.py read` 获取当前完整状态（xbase 不是工作流 skill，没有自己的 `initialized` 字段，所以用 `read` 读完整状态而非 `check-and-read`）
2. **步骤 1 — 项目探测**（如 `## 项目信息` 各字段已有值则跳过）：
   - Claude 用 Glob 扫描根目录识别标志文件（Cargo.toml、Package.swift、package.json 等）
   - Claude 读 CLAUDE.md，理解构建命令、项目类型、日志系统等信息
   - Claude 找到文档目录（`document/`、`docs/` 等），未找到则创建 `docs/`
   - Claude 将探测结果作为参数传给脚本写入：`skill-state.py write-info 类型 "<Claude判断的类型>" 构建命令 "<Claude提取的命令>" output_dir "<Claude找到的目录>"`（脚本只是写入器，不做判断）
3. **步骤 2 — 并行创建产出物**：
   - 先写入跳过去重标记：`skill-state.py write-info skip_dedup true`
   - 启动 7 个 Task 子 agent（xdebug、xtest、xlog、xcommit、xreview、xdoc、xdecide），各自执行自己的阶段 0（产出物创建部分，跳过去重子步骤）
   - 等待全部完成，逐个展示结果（✅ / ⏭️ 跳过）
4. **步骤 3 — 串行去重**：
   - 清除跳过标记：`skill-state.py write-info skip_dedup ""`
   - Claude 读取 CLAUDE.md / MEMORY.md，对比各 skill 核心文件，识别重复段落
   - 逐项展示 diff 预览，等用户确认后用 Edit 替换为指针
5. **步骤 4 — 汇总展示**

**`/xbase status`**：

1. `skill-state.py read` 获取状态
2. 逐个 skill 检查 `initialized` 字段是否有值
3. 对每个产出物路径 Glob 检查文件是否实际存在
4. 展示汇总表（skill 名 / 初始化日期 / 产出物 / 文件存在 ✅/❌）

**`/xbase reset`**：

1. AskUserQuestion 确认：「将重置所有 skill 的初始化状态。产出物文件不会被删除。确认？」
2. 确认后 `skill-state.py reset-all`
3. 展示重置后状态

**`/xbase reinit`**：

1. `skill-state.py delete-info` 清空项目信息段
2. 重新执行 init 流程

---

### 1. xtest — 测试（入口：发现问题）

**做什么**：自动化测试 + 手动逐项验证，维护测试清单和 Bug 队列。

**典型触发时机**：开发完功能后验证、日常回归测试、修复后复测。

**参数**：空 → 正常流程 | `自动化` → 跳到 2a | `手动` → 跳到 2b | `reinit` → 重新初始化

**产出物**：`TEST-CHECKLIST.md`（测试清单）、`TEST-ISSUES.md`（Bug 队列）

#### 执行流程

**阶段 0 — 初始化**（自动，不问用户）：

1. 预加载 `skill-state.py check-and-read xtest` → `initialized` 则跳过整个阶段
2. 项目探测（共享流程，如项目信息段已有值则跳过）
3. 验证调试基础设施：按 `xdebug/references/infra-setup.md` 检查四项能力（构建、后台启动、日志捕获、停止），缺失自动创建
4. 全项目搜索 TEST-CHECKLIST.md 同类文件：
   - **找到** → 迁移到 `output_dir` + 套用新格式（保留原始测试结果）
   - **没找到** → `artifact-create.py checklist <路径>` 创建骨架 → 执行步骤 5-7 全量生成
   - **已存在且格式正确** → 增量更新（只扫描 `git diff` 变更文件），跳到阶段 1
5. 全项目搜索 TEST-ISSUES.md 同类文件：同上三态处理
6. 并行子 agent 扫描代码生成测试功能点：
   - 子 agent A：自动化测试用例（`#[test]`、XCTest 等）
   - 子 agent B：公开接口、命令、状态管理
   - 子 agent C：交互入口（UI 事件、快捷键、手势）
   - 子 agent D：FFI/API 边界
7. 参考文档补充业务逻辑，为每个功能点分类（🤖 自动化 / 👤 手动 / 🤝 结合），生成 TEST-CHECKLIST.md
8. `skill-state.py write xtest test_checklist "<路径>" test_issues "<路径>"`
9. 去重子步骤（xtest 当前无重复内容 → 跳过）

**阶段 1 — 选择测试类型**（选项）：

- AskUserQuestion：「测试什么？」→ 自动化测试 / 手动测试（选模块逐项验证） / Other（指定编号）

**阶段 2a — 自动化测试**（自动）：

1. 根据项目构建系统运行测试命令
2. 解析输出，映射到 TEST-CHECKLIST.md 对应项
3. 更新状态和概览表
4. AskUserQuestion：「X 通过 / Y 失败。下一步？」→ 查看失败详情 / 继续手动测试 / 进入 /xdebug 修复 / 结束

**阶段 2b — 手动测试**（逐项选项）：

1. 选模块：从 TEST-CHECKLIST.md 按 ID 前缀统计 ⏳ 项，展示最多 4 个模块选项
2. 构建 + 后台启动项目（自动，构建失败自行修复）
3. 逐项测试：每项 AskUserQuestion 给出具体操作步骤 → 通过 / 失败 / 跳过 / Other（备注）
4. 结果暂存内存，一轮结束后批量写入 TEST-CHECKLIST.md

**阶段 3 — 失败处理**（每次选"失败"时自动触发）：

1. 启动后台子 agent（Task, run_in_background）分析日志
2. 在 TEST-CHECKLIST.md 标注 ❌ + 问题描述
3. `issues.py next-id <路径>` 获取编号 → Edit 写入 🔴 条目到 TEST-ISSUES.md
4. **不打断测试**，继续下一项

**阶段 4 — 汇总**（选项）：

1. 停止项目
2. 收集所有后台子 agent 分析结论
3. AskUserQuestion：「X 通过 / Y 失败 / Z 跳过。下一步？」
   - 立即修复 → 从 TEST-ISSUES.md 取 🔴 条目 → 衔接 `/xdebug`（传条目编号如 `#003`）
   - 复测已修复项 → 扫描 🟢 条目逐项验证，通过 → ✅，未通过 → 回 🔴
   - 提交变更 → `/xcommit`
   - 继续下一个模块 → 回阶段 1

---

### 2. xdebug — 调试（核心：定位修复）

**做什么**：引导式调试循环 — 加日志 → 构建运行 → 引导用户操作 → 分析日志 → 修复 → 验证。

**典型触发时机**：xtest 发现 Bug 后衔接过来、用户直接报告问题。

**参数**：空 → 正常流程 | `#003` → 从 TEST-ISSUES.md 取条目，设为 🟡 修复中，跳到阶段 2 | 其他文本 → 作为 Bug 描述跳到阶段 2 | `reinit` → 重新初始化

**产出物**：`DEBUG-LOG.md`（Bug 修复日志）、`scripts/run.sh`（调试运行脚本）

#### 执行流程

**阶段 0 — 探测项目**（自动）：

1. 预加载 `skill-state.py check-and-read xdebug` → `initialized` 则跳过
2. 项目探测（共享流程）
3. 验证调试基础设施：按 `references/infra-setup.md` 检查四项能力（构建、后台启动、日志捕获、停止），缺失自动创建
4. 全项目搜索 DEBUG-LOG.md 同类文件 → 找到迁移 / 没找到创建骨架
5. `skill-state.py write xdebug debug_log "<路径>"`
6. 去重：MEMORY.md 中 DEBUG_LOG 格式说明 → 替换为指针；「修复 Bug 必须更新」→ 保留（禁令）

**阶段 1 — 确认问题**（选项，同时后台启动构建）：

- AskUserQuestion：「这次调试什么？」
  - 从 TEST-ISSUES.md 选取（先检查 `xtest → test_issues` 字段，无值不展示。有值则 `issues.py list --status 待修` 展示 🔴 项，选中后 `issues.py status` 设为 🟡）
  - 探索性测试（先跑起来看日志）
  - 继续上次调试（从 TEST-ISSUES.md 找 🟡 条目）
  - Other → 直接输入 Bug 描述

**阶段 2 — 加日志 + 构建 + 运行**（全自动，不问用户）：

1. 判断现有日志是否覆盖问题区域（查 LOG-COVERAGE.md + 读相关代码）
   - 覆盖足够 → 直接构建
   - 覆盖不足 → 启动 Task 子 agent，传入目标文件和问题描述，让它读 `/xlog` SKILL.md 按 xlog 流程补日志
2. 执行构建命令
3. 编译失败 → 自己修复重试
4. 停止旧进程，后台启动项目

**阶段 3 — 引导用户操作**（选项）：

- AskUserQuestion：根据具体 Bug 给出 1-2-3 操作步骤（不泛泛说"请操作"）
  - 操作完了，看日志
  - 问题没复现
  - App 崩溃了 / 没启动

**阶段 4 — 分析日志**（选项，App 保持运行不停）：

1. 通过运行脚本 `logs` 命令读取，先按级别/模块过滤缩小范围
2. AskUserQuestion：「[分析摘要]。下一步？」
   - 已定位，修复代码
   - 日志不够，加日志再来一轮 → 回阶段 2
   - 放弃，记录到 TODO
   - Other → 补充信息

**阶段 5 — 修复 + 验证**（选项）：

1. 停止项目（改代码前才停）
2. 修改代码修复
3. 删除临时诊断日志（保留长期有价值的）
4. 重新构建 + 后台启动
5. AskUserQuestion：给出具体验证步骤 → 修好了 / 没修好继续调（→ 回阶段 2） / Other（发现新问题）

**阶段 6 — 收尾**（确认修好后自动执行 + 最后选项）：

1. 停止项目
2. 在 DEBUG-LOG.md 追加修复记录
3. 如来自 TEST-ISSUES.md：`issues.py status <path> <id> 已修复`（🟡 → 🟢）+ Edit 写入修复说明
4. AskUserQuestion：「修复完成。下一步？」
   - 继续修下一个 → 回阶段 1（如 TEST-ISSUES.md 还有 🔴）
   - 提交变更 → `/xcommit`
   - 记录决策 → `/xdecide`（传技术决策背景）
   - Other → 描述新问题

---

### 3. xlog — 日志补全（辅助：通常由 xdebug 自动调用）

**做什么**：建立日志规范，扫描代码补充诊断日志、纠正不规范日志。

**典型触发时机**：xdebug 阶段 2 发现日志不足时**自动**启动 xlog 子 agent；也可独立使用给特定模块补日志。

**参数**：空 → 正常流程 | 文件/模块路径 → 跳到阶段 2 | `reinit` → 重新初始化

**产出物**：`LOG-RULES.md`（日志规范）、`LOG-COVERAGE.md`（覆盖度跟踪）

#### 执行流程

**阶段 0 — 探测项目日志系统**（自动）：

1. 预加载 `skill-state.py check-and-read xlog` → `initialized` 则跳过
2. 项目探测（共享流程）
3. 读 CLAUDE.md 日志相关规则（如禁止 print）
4. 扫描代码找日志工具：Logger 文件、调用模式（`Log.xxx`/`log::xxx`）、可用 Logger 实例、消息语言
5. 全项目搜索 LOG-RULES.md 同类文件 → 找到迁移 / 没找到则基于扫描结果生成
6. 全项目搜索 LOG-COVERAGE.md 同类文件 → 同上
7. `skill-state.py write xlog log_rules "<路径>" log_coverage "<路径>"`
8. 去重：MEMORY.md 中日志规则重复部分 → 替换为指针；「禁止 print()」→ 保留

**阶段 1 — 选择范围**（选项，子 agent 调用时跳过）：

- 读取 LOG-COVERAGE.md 概览
- AskUserQuestion：「给哪里补日志？（✅ X 已覆盖 / ⚠️ Y 有盲区 / ⏳ Z 未扫描）」
  - 未扫描的模块（优先盲区最多的）
  - 指定文件/模块
  - 全项目扫描
  - Other

**阶段 2 — 扫描 + 补全 + 纠正**（全自动）：

1. 读 LOG-RULES.md 获取规则
2. 确定扫描范围：指定范围 → 扫描该范围 | 全项目 + 已有记录 → 只扫 `git diff` 变更 | 首次 → 全量
3. 检查两类问题：
   - **盲区**：该有日志但没有 → 补充（决策点、模块边界、FFI 边界）
   - **不规范**：违反禁忌（print 代替 Logger）、级别错误、Logger 不匹配、消息风格不符
4. 构建确认编译通过（失败自修复）
5. 更新 LOG-COVERAGE.md 状态和扫描日期

**阶段 3 — 汇报**（选项）：

- AskUserQuestion：「已处理 X 个文件：补充 Y 条 / 纠正 Z 条。」
  - 完成 / 继续下一个模块 → 回阶段 1 / 看详细变更 / 撤回部分变更

---

### 4. xreview — 代码审查（质量：修复后检查）

**做什么**：基于 REVIEW-RULES.md 进行三维度审查（规范合规 / 架构质量 / 安全健壮），逐项决策。

**典型触发时机**：修复完 Bug 后审查代码质量、提交前代码检查、定期代码审计。

**参数**：空 → 正常流程 | 文件/目录路径 → 跳到阶段 2 | `reinit` → 重新初始化

**产出物**：`REVIEW-RULES.md`（审查规范）

#### 执行流程

**阶段 0 — 探测项目**（自动）：

1. 预加载 `skill-state.py check-and-read xreview` → `initialized` 则跳过
2. 项目探测（共享流程）
3. 全项目搜索 REVIEW-RULES.md 同类文件 → 找到迁移 / 没找到则生成
4. 生成 REVIEW-RULES.md（两层规则提取）：
   - a) CLAUDE.md 提取：禁忌类（"禁止"/"NEVER"）、必须类（"必须"/"MUST"）、规范类（"命名"/"格式"）、架构类（"依赖"/"层"/"耦合"）
   - b) 代码扫描：缩进风格、命名风格、注释语言、目录结构、错误处理模式、安全检查点
   - 每条规则标注来源（`CLAUDE.md` 或 `代码扫描`）
5. `skill-state.py write xreview review_rules "<路径>"`
6. 去重：CLAUDE.md `## 代码规范` 段 → 替换为指针；「禁止 print()」→ 保留

**阶段 1 — 确定范围**（选项）：

- AskUserQuestion：「审查什么代码？」
  - 未提交变更（git diff）
  - 最近一次提交（git show HEAD）
  - 指定路径
  - Other → 路径或 git range

**阶段 2 — 执行审查**（逐项选项）：

1. 获取目标代码：git diff / git show / 读文件
2. 上下文感知调整重点：Bug 修复 → 根因是否真正修复；新功能 → 架构一致性；重构 → 行为一致性
3. 读取 REVIEW-RULES.md，三维度审查：
   - **A. 规范合规**：逐条核对禁忌/必须/编码规范
   - **B. 架构质量**：依赖方向、职责划分、重复代码、接口设计
   - **C. 安全健壮**：边界条件、并发安全、资源管理、安全漏洞
4. 每发现问题 → AskUserQuestion：「[维度] 文件:行 — 问题描述 + 建议修复」
   - 立即修复（→ 执行修复后继续审查）
   - 记录到重构清单
   - 记录决策 → `/xdecide`
   - 忽略

**阶段 3 — 收尾**（选项）：

- AskUserQuestion：「审查完成。N 个问题（已修复 X / 记录 Y / 忽略 Z）。」
  - 提交变更 → `/xcommit`
  - 记录决策 → `/xdecide`
  - 继续审查其他代码 → 回阶段 1
  - 结束

---

### 5. xdecide — 决策记录（按需：涉及技术决策时）

**做什么**：引导式决策（分析方案 + 利弊权衡 + 结论记录）+ 快速录入 + 回顾修订。

**典型触发时机**：xdebug 修复涉及架构选择、xreview 发现需要决策的问题、独立的技术方案讨论。

**参数**：空 → 正常流程 | `review` → 跳到阶段 2c 回顾 | 其他文本 → 作为决策描述跳到阶段 2a | `reinit` → 重新初始化

**产出物**：`DECIDE-LOG.md`（决策记录）

#### 执行流程

**阶段 0 — 探测项目**（自动）：

1. 预加载 `skill-state.py check-and-read xdecide` → `initialized` 则跳过
2. 项目探测（共享流程）
3. 搜索 `DECIDE-LOG.md` 或含 `决策记录`、`decision`、`ADR` 关键词的文件（文档目录 + 根目录）
4. 三态处理：找到迁移 / 没找到在 `output_dir` 创建 / 已就绪用 `decision-log.py list` 展示概览
5. `skill-state.py write xdecide decision_log "<路径>"`
6. 去重：MEMORY.md 中决策记录格式说明 → 替换为指针；「任何决策必须记录」→ 保留

**阶段 1 — 选择模式**（选项）：

- AskUserQuestion：「决策记录。选择操作：」
  - 新决策（引导式）
  - 快速录入
  - 回顾已有决策
  - Other → 直接描述决策主题

**阶段 2a — 引导式决策**（逐步选项）：

1. **理清背景**（从其他 skill 衔接时参数已包含描述则跳过）：AskUserQuestion 获取背景
2. **分析方案**：
   - 扫描相关代码理解当前实现
   - `decision-log.py search <路径> <关键词>` 搜索历史相关决策，避免重复
   - 分析可行方案列出利弊
   - AskUserQuestion：「方案 A（优势/劣势）/ 方案 B / 推荐方案 X」→ 选方案 / Other 补充
3. **确认结论**：`decision-log.py next-id <路径>` 获取编号 → 格式化预览 → AskUserQuestion 确认写入
4. **写入**：Edit 在决策记录文件末尾追加

**阶段 2b — 快速录入**（选项）：

1. AskUserQuestion 获取一句话背景 + 结论
2. 自动格式化为标准条目，获取编号
3. 预览确认后写入

**阶段 2c — 回顾修订**（选项）：

1. `decision-log.py list` 展示所有决策
2. AskUserQuestion 选择条目（超过 4 个则展示最近 3 个 + Other 可搜索）
3. 展示完整内容
4. AskUserQuestion → 追加修订（在原条目末尾加 `**修订（日期）**：`，不删除原文）/ 查看相关代码 / 查看其他 / 结束

**阶段 3 — 收尾**（选项）：

- AskUserQuestion：「决策记录完成。」→ 继续下一条 → 回阶段 1 / 提交变更 → `/xcommit` / 结束

---

### 6. xdoc — 文档维护（按需：文档不同步时）

**做什么**：文档健康检查（断链 / 格式 / 结构）+ 代码-文档一致性验证。

**典型触发时机**：代码改了但文档没跟上、定期文档清理、发布前检查。

**参数**：空 → 正常流程 | `健康检查` → 跳到 2a | `一致性` → 跳到 2b | 文件/目录路径 → 检查该路径 | `reinit` → 重新初始化

**产出物**：`DOC-RULES.md`（文档规范）

#### 执行流程

**阶段 0 — 探测项目**（自动）：

1. 预加载 `skill-state.py check-and-read xdoc` → `initialized` 则跳过
2. 项目探测（共享流程）
3. 全项目搜索 DOC-RULES.md 同类文件 → 找到迁移 / 没找到则生成
4. 生成 DOC-RULES.md（两层规则提取）：
   - a) CLAUDE.md 提取：文档优先级（"文档"/"优先"）、维护要求（"必须"/"同步"）、批量编辑规则（"verify"/"验证"）
   - b) 项目扫描：文档目录结构、检查脚本（`check_links`/`check_structure`/`generate_index`/`verify_edits`）、格式规范、代码-文档映射
5. `skill-state.py write xdoc doc_rules "<路径>"`
6. 去重（xdoc 当前无重复内容 → 跳过）

**阶段 1 — 选择任务**（选项）：

- AskUserQuestion：「文档维护。选择操作：」
  - 健康检查（断链、格式、结构）
  - 一致性验证（代码 ↔ 文档）
  - 指定文件检查
  - Other

**阶段 2a — 健康检查**（自动）：

1. 运行 DOC-RULES.md 中列出的检查脚本（逐个运行，汇总问题）
2. 格式规范检查：内部链接验证、标题层级、代码块标注、空文件检测
3. 汇总问题清单按严重程度排序（断链 > 格式 > 建议）

**阶段 2b — 一致性验证**（自动）：

1. `git log --oneline -20` + `git diff HEAD~5..HEAD --stat` 获取最近变更
2. 读取 DOC-RULES.md「代码-文档映射」，对照变更文件识别应更新的文档
3. 检查映射项：代码变更提交中是否包含对应文档更新
4. 汇总不一致清单

**阶段 3 — 修复**（逐项选项）：

- 逐项 AskUserQuestion：「[问题类型] [文件路径] — 问题描述 + 建议修复」
  - 自动修复 / 手动处理（跳过）/ 忽略
- 批量修复后验证：10+ 文件修改 → 按 DOC-RULES.md 运行验证脚本

**阶段 4 — 汇报**（选项）：

- AskUserQuestion：「检查 N 文件，发现 X 问题（已修复 Y / 跳过 Z）。」
  - 重新检查 / 提交变更 → `/xcommit` / 结束

---

### 7. xcommit — 提交（出口：所有变更的终点）

**做什么**：预检脚本 + 文档完整性检查 + 规范化 commit。

**典型触发时机**：任何 skill 完成工作后的最后一步，也可独立使用。几乎所有 skill 的收尾选项都能衔接到这里。

**参数**：空 → 自动生成 message | commit 消息文本 → 用作候选 message | `reinit` → 重新初始化

**产出物**：`COMMIT-RULES.md`（提交规范）

#### 执行流程

**阶段 0 — 探测项目**（自动）：

1. 预加载 `skill-state.py check-and-read xcommit` → `initialized` 则跳过
2. 项目探测（共享流程）
3. 全项目搜索 COMMIT-RULES.md 同类文件 → 找到迁移 / 没找到则生成
4. 生成 COMMIT-RULES.md（两层规则提取）：
   - a) CLAUDE.md 提取：提交规则（"提交"/"commit"/"暂存"）、文档要求（"DEBUG-LOG"/"必须"）、禁忌类（"禁止"/"NEVER"）
   - b) 项目扫描：最近 10 条 commit 分析消息语言/前缀/长度风格；`scripts/` 下搜索预检脚本（preflight/precommit/lint/verify）；扫描文档映射（DEBUG-LOG.md、DECIDE-LOG.md 等）
5. `skill-state.py write xcommit commit_rules "<路径>"`
6. 去重：CLAUDE.md `## Git 提交规范` 段 → 替换为指针

**阶段 1 — 检查变更**（选项）：

1. `git-context.py commit-context` 收集 status/diff/log/commit_style
2. 无变更 → 提示结束
3. 全部已暂存 → 直接进入阶段 2
4. 有未暂存 → AskUserQuestion：「有未暂存文件：[列表]」
   - 全部暂存
   - 选择暂存（展示列表）
   - 仅提交已暂存的
   - Other → 指定文件
5. 暂存用具体文件名 `git add <file>`，不用 `git add -A`

**阶段 2 — 预检**（自动 / 失败时选项）：

1. 读 COMMIT-RULES.md「预检脚本」列表，逐个运行
2. 全部通过 → 阶段 3
3. 有失败 → AskUserQuestion：「[脚本名] 失败：[摘要]」
   - 自动修复（修复后重新运行）
   - 跳过此检查
   - 取消提交
4. 无预检脚本 → 跳过此阶段

**阶段 3 — 文档完整性**（建议不阻断）：

1. `git diff --cached` 分析暂存变更
2. 推断变更类型：Bug 修复 / 架构变更 / 新功能
3. 读 COMMIT-RULES.md「变更类型 → 文档映射」，检查对应文档是否在暂存中
4. 疑似遗漏 → AskUserQuestion：「本次看起来是 [Bug 修复]，但 [DEBUG-LOG.md] 未在暂存中。」
   - 先补文档再提交
   - 不需要，继续提交
   - Other
5. 无遗漏 → 直接阶段 4

**阶段 4 — 生成提交**（选项）：

1. 生成 commit message：参数已提供 → 优先使用；否则参照 COMMIT-RULES.md 风格分析 diff 生成
2. AskUserQuestion：「准备提交。文件列表 + message 预览」
   - 确认提交
   - 修改 message
   - 取消
   - Other → 输入新 message
3. `git commit -m "<message>"`
4. `git status` 确认成功（不自动 push）

---

## 工作流衔接

skill 之间通过 AskUserQuestion 选项衔接，**不自动跳转**，用户主动选择。

```
xtest ──→ xdebug ──→ xlog        (测试发现 Bug → 调试 → 补日志)
              ├──→ xdecide       (修复涉及技术决策 → 记录)
              └──→ xcommit       (修复完成 → 提交)

xreview ──→ xdecide              (审查发现架构问题 → 记录决策)
        └──→ xcommit             (审查修复后 → 提交)

xdoc ──→ xcommit                 (文档修复后 → 提交)

xdecide ──→ xcommit              (决策记录后 → 提交)
```

| 源 → 目标 | 触发时机 | 传递什么 |
|-----------|---------|---------|
| xtest → xdebug | 测试失败选"立即修复" | TEST-ISSUES.md 的 🔴 条目编号 |
| xdebug → xlog | 日志不足时自动触发 | 目标文件路径 + 问题描述（Task 子 agent） |
| xdebug → xdecide | 收尾选"记录决策" | 技术决策的背景描述 |
| xdebug → xcommit | 收尾选"提交变更" | 无（xcommit 自行读 git） |
| xreview → xdecide | 发现架构问题选"记录决策" | 架构问题描述 |
| xreview → xcommit | 收尾选"提交变更" | 无 |
| xdoc → xcommit | 汇报选"提交变更" | 无 |
| xdecide → xcommit | 收尾选"提交变更" | 无 |

---

## 产出物一览

所有产出物都存放在同一个目录（由 `output_dir` 字段指定，通常是项目的文档目录）：

| 产出物 | 谁创建 | 谁维护 | 说明 |
|--------|-------|--------|------|
| `SKILL-STATE.md` | 首个 skill | 所有 skill | 运行时状态（项目类型、路径、初始化日期） |
| `DEBUG-LOG.md` | xdebug | xdebug | Bug 修复日志（症状→根因→解决） |
| `scripts/run.sh` | xdebug | xdebug, xtest | 调试运行脚本（构建/启动/停止/日志） |
| `TEST-CHECKLIST.md` | xtest | xtest | 测试清单（按模块，记录结果 ✅/❌/⏳） |
| `TEST-ISSUES.md` | xtest | xtest 写入, xdebug 更新 | Bug 队列（状态流转 🔴→🟡→🟢→✅） |
| `LOG-RULES.md` | xlog | xlog | 日志规范（Logger 列表、级别用法） |
| `LOG-COVERAGE.md` | xlog | xlog | 日志覆盖度跟踪 |
| `REVIEW-RULES.md` | xreview | xreview | 审查规范（三维度规则） |
| `COMMIT-RULES.md` | xcommit | xcommit | 提交规范（风格、预检脚本、文档映射） |
| `DOC-RULES.md` | xdoc | xdoc | 文档规范（目录结构、检查脚本） |
| `DECIDE-LOG.md` | xdecide | xdecide | 决策条目（编号递增，含背景/选项/结论） |

---

## 核心机制详解

### 1. 阶段 0 — 统一初始化流程

每个 skill 的第一个阶段都是"阶段 0"，采用**完全相同的模板**（`xbase/references/phase0-template.md`），流程如下：

```
预加载（!`command`）
    ↓
check 返回 initialized? ──→ 是：跳过整个阶段 0
    ↓ 否
项目信息段已有值? ──→ 是：复用，不重复探测
    ↓ 否
项目探测（Claude 直接执行）
    ↓
确定产出物目录（output_dir）
    ↓
产出物搜索（Claude 全项目搜索同类文件）
    ├─ 找到 → 迁移到 output_dir + 改造格式
    └─ 没找到 → artifact-create.py 创建骨架
    ↓
写入状态（skill-state.py write）
    ↓
去重（Claude 对比核心文件与 CLAUDE.md，逐条确认）
```

**为什么这样设计**：
- **`check` 快速跳过**：已初始化的 skill 只需一次进程调用就知道可以跳过，不做任何多余工作
- **项目信息共享**：第一个初始化的 skill 写入项目信息，后续 skill 直接复用
- **全项目搜索**：兼容已有文件 — 无论用户的文件叫什么名字、放在哪里，只要内容用途匹配就会迁移复用，不会从零覆盖

### 2. 状态管理 — SKILL-STATE.md

所有 skill 通过一个共享文件 `SKILL-STATE.md` 管理状态，避免跨 session 重复探测。

**结构**：
```markdown
## 项目信息                        # 全局共享
- 类型: GUI 应用
- 构建命令: (见 CLAUDE.md)
- output_dir: document/90-开发
- skip_dedup:                      # 非空时跳过去重

## xdebug                          # 每个 skill 一段
- debug_log: document/90-开发/DEBUG-LOG.md
- initialized: 2026-02-14          # 有值 = 已初始化

## xtest
- test_checklist: document/90-开发/TEST-CHECKLIST.md
- test_issues: document/90-开发/TEST-ISSUES.md
- initialized: 2026-02-14

## xlog / xcommit / xreview / xdoc / xdecide
- <产出物字段>: <路径>
- initialized: <日期>
```

**关键设计**：
- 文件是**模板预置**的 — 所有段和字段已定义好，skill 只需填值
- `initialized` 字段有值 = 已初始化，`check` 命令就靠这个判断
- 所有写操作通过 `fcntl.LOCK_EX` 排他锁保护，并行初始化时不会数据竞争

### 3. 初始化编排 — `/xbase init`

`/xbase init` 采用**编排模式**，xbase 自身只做项目探测，产出物创建全部委派给各 skill：

```
步骤 1：项目探测（Claude 直接扫描根目录 + 读 CLAUDE.md）
步骤 2：并行执行各 skill 阶段 0（7 个 Task 子 agent 同时启动）
步骤 3：串行去重（逐个 skill 清理 CLAUDE.md / MEMORY.md 中的重复内容）
步骤 4：汇总展示
```

**为什么用编排模式**：此前 xbase 硬编码了所有产出物的创建逻辑，与各 skill 阶段 0 大量重复。改为编排后，谁的产出物谁负责创建，xbase 只做调度。

**为什么步骤 2 可以并行**：各 skill 的阶段 0 互不依赖 — 它们只读 SKILL-STATE.md 项目信息段（步骤 1 已写入），不互相写入。

**为什么步骤 3 必须串行**：多个 skill 可能修改同一个文件（如 CLAUDE.md），串行避免冲突。

### 4. 去重机制

问题：项目 CLAUDE.md 里可能写了"Git 提交规范"的具体规则，而 xcommit 又生成了 COMMIT-RULES.md 覆盖同样的内容。两处维护容易不同步。

解决：各 skill 初始化后检查 CLAUDE.md / MEMORY.md 中是否有被自己产出物覆盖的内容，提议替换为指针。

**原则**：
- **方法论/禁令** → 保留原文（如"禁止 print()"、"先加日志不要盲猜"）
- **具体规范** → 替换为一句话指针（如"提交规范详见 COMMIT-RULES.md"）

| Skill | 替换什么 |
|-------|---------|
| xcommit | CLAUDE.md `## Git 提交规范` → 指向 COMMIT-RULES.md |
| xreview | CLAUDE.md `## 代码规范` → 指向 REVIEW-RULES.md |
| xdebug | MEMORY.md 中 DEBUG_LOG 格式说明 → 指向 DEBUG-LOG.md |
| xdecide | MEMORY.md 中决策记录格式说明 → 指向 DECIDE-LOG.md |
| xlog | MEMORY.md 中日志规则重复部分 → 指向 LOG-RULES.md |
| xtest / xdoc | 当前无重复内容 → 跳过 |

Claude 判断禁令/方法论类内容保留原文，具体规范替换为指针。替换前展示 diff 预览，等用户确认。

### 5. 规则来源两层

xcommit、xreview、xdoc、xlog 在生成规范类产出物时采用两层规则提取：

1. **CLAUDE.md 提取**（如存在）— 搜索关键词提取禁忌/必须/规范/架构约束
2. **代码扫描推导**（始终执行）— 扫描源文件推导缩进/命名/注释语言/目录结构等

每条规则标注来源（`CLAUDE.md` 或 `代码扫描`），便于后续维护和溯源。没有 CLAUDE.md 的项目也能用（只用代码扫描结果）。

### 6. TEST-ISSUES.md 协作

这是 xtest 和 xdebug 之间的协作桥梁：

**状态流转**：`🔴 待修 → 🟡 修复中 → 🟢 已修复 → ✅ 复测通过`

| 操作 | 谁做 | 什么时候 |
|------|------|---------|
| 创建文件 | xtest | 阶段 0 初始化 |
| 写入 🔴 条目 | xtest | 测试失败时 |
| 🔴 → 🟡 修复中 | xdebug | 选取条目开始修复 |
| 🟡 → 🟢 已修复 | xdebug | 修复完成 |
| 🟢 → ✅ 复测通过 | xtest | 复测确认 |

---

## Python 工具详解

共享工具在 `xbase/scripts/`，领域工具在各自 skill 的 `scripts/` 下。下面按**初始化阶段的调用顺序**排列，然后是工作阶段的工具。

### 初始化阶段（阶段 0 按顺序调用）

---

#### 1. 项目探测（Claude 直接执行，无脚本）

**解决什么问题**：skill 需要知道"这是什么项目、怎么构建、文档放哪"，但不能硬编码。

**谁执行**：`/xbase init` 步骤 1；各 skill 阶段 0 在项目信息段为空时也会执行。

**怎么工作**：
1. 用 Glob 扫描项目根目录，识别标志文件（Cargo.toml、Package.swift、*.xcodeproj、package.json 等）
2. 读 CLAUDE.md，提取构建命令、项目类型、日志系统等信息
3. 找到文档目录（`document/`、`docs/`、`doc/` 等），未找到则创建 `docs/`
4. 用 `skill-state.py write-info` 写入 SKILL-STATE.md

**为什么不用脚本**：项目探测是语义理解任务（需理解 CLAUDE.md 自然语言、识别混合技术栈、推断构建命令），Claude 直接执行比正则匹配更准确、更通用。

---

#### 2. skill-state.py — 状态管理

**解决什么问题**：所有 skill 需要共享状态（项目信息、各 skill 的初始化状态和产出物路径），而且要支持并行写入不冲突。这个脚本是 SKILL-STATE.md 的唯一读写接口。

**谁调用**：**所有 skill** 都调用 — 阶段 0 开头 `check` 判断是否跳过，结尾 `write` 写入状态；`/xbase init` 用 `write-info` 写项目信息；`reinit` 用 `delete` 清空。

**怎么工作**：
- SKILL-STATE.md 是**模板预置**的（所有段和字段已定义好，值留空）
- `check` 看 `initialized` 字段是否有值 → 有值返回 `initialized`，无值返回 `not_found`
- `write` 写入时自动添加 `initialized: 当前日期`
- 所有写操作使用 `fcntl.LOCK_EX` 排他锁，`/xbase init` 并行启动 7 个 skill 时不会冲突

**API**：
```bash
# 检查 skill 是否已初始化（最常用，每个 skill 阶段 0 第一步就调它）
python3 .claude/skills/xbase/scripts/skill-state.py check <skill>
# → 输出 "initialized" 或 "not_found"

# check + read 合并（省一次进程启动，用于预加载）
python3 .claude/skills/xbase/scripts/skill-state.py check-and-read <skill>

# 读取完整状态文件
python3 .claude/skills/xbase/scripts/skill-state.py read

# 写入 skill 段（支持多个 key-value 对，自动添加 initialized 日期）
python3 .claude/skills/xbase/scripts/skill-state.py write <skill> <key> <value> [<key2> <value2> ...]
# 例：write xdebug debug_log document/90-开发/DEBUG-LOG.md

# 写入项目信息段
python3 .claude/skills/xbase/scripts/skill-state.py write-info <key> <value> [<key2> <value2> ...]
# 例：write-info 类型 "GUI 应用" output_dir document/90-开发

# 清空某个 skill 段的值（reinit 时用，保留段结构）
python3 .claude/skills/xbase/scripts/skill-state.py delete <skill>

# 清空项目信息段
python3 .claude/skills/xbase/scripts/skill-state.py delete-info

# 恢复初始模板（全量重置，/xbase reset 调用）
python3 .claude/skills/xbase/scripts/skill-state.py reset-all
```

---

#### 3. artifact-create.py — 产出物骨架创建

**解决什么问题**：当全项目搜索后确认没有同类文件时，需要从零创建产出物。这个脚本从 `references/*-format.md` 自动提取格式结构，生成骨架文件。

**谁调用**：各 skill 阶段 0，在 Claude 全项目搜索确认无同类文件后调用。

**怎么工作**：
1. 动态扫描所有 `references/*-format.md`，从 H1 提取文件名，从 H2 提取段落结构
2. 生成包含正确标题和段落骨架的文件，Claude 再用 Edit 填充内容

**新增 skill 如何适配**：只需在 `references/` 放一个 `xxx-format.md`，脚本自动发现。

**API**：
```bash
# 创建骨架文件
python3 .claude/skills/xbase/scripts/artifact-create.py <artifact_name> <target_path>
# 例：artifact-create.py commit-rules document/90-开发/COMMIT-RULES.md

# 列出所有可创建的产出物
python3 .claude/skills/xbase/scripts/artifact-create.py --list
```

---

#### 4. 去重（Claude 直接执行）

**解决什么问题**：CLAUDE.md 里可能写了"Git 提交规范"的详细规则，xcommit 又生成了 COMMIT-RULES.md 覆盖同样内容。两处维护容易不同步，需要把 CLAUDE.md 中已被核心文件覆盖的段落替换为一句话指针。

**怎么工作**：无脚本，由 Claude 直接执行（见 `dedup-steps.md`）：
1. 读取 CLAUDE.md / MEMORY.md
2. 对比各 skill 核心文件内容，识别重复段落
3. 逐条展示 diff 预览，等用户确认后用 Edit 替换为指针

**判断标准**：方法论/禁令/哲学 → 保留原文；已被核心文件覆盖的具体规范 → 替换为一句话指针。

### 工作阶段（skill 执行具体任务时调用）

---

#### 5. git-context.py — Git 上下文收集

**解决什么问题**：xcommit 需要 `git status` + `git diff` + `git log` 等多个命令的输出；xreview 需要 diff；xtest 需要变更文件列表。每次单独调 Bash 很慢（每次一个进程），这个脚本一次调用收集所有需要的 git 信息。

**谁调用**：
- **xcommit** 阶段 1 调用 `commit-context` — 获取 status、diff、最近 log、提交风格分析
- **xreview** 阶段 1 调用 `diff-context` — 获取 staged/unstaged diff
- **xtest** 阶段 0 调用 `changed-files` — 获取变更文件列表做增量更新

**API**：
```bash
# xcommit 用：收集 status + diff + staged diff + 最近 10 条 log + 分析提交风格
python3 .claude/skills/xcommit/scripts/git-context.py commit-context

# xreview 用：收集 diff（可选 staged/unstaged/both）
python3 .claude/skills/xcommit/scripts/git-context.py diff-context [--scope staged|unstaged|both]

# xtest 用：收集变更文件列表（staged 或最近 5 次提交）
python3 .claude/skills/xcommit/scripts/git-context.py changed-files [--scope staged|recent]
```

**commit-context 输出示例**：
```json
{
  "status": "M  README.md\nA  new-file.py",
  "cached_diff": "diff --git a/...",
  "recent_log": ["abc1234 上一次提交消息", "def5678 再上一次"],
  "commit_style": {
    "language": "zh",
    "prefix_pattern": "none",
    "avg_length": 25
  },
  "has_staged": true,
  "has_unstaged": false
}
```

**异常处理**：git 未安装返回空字符串（`FileNotFoundError`）；大仓库超时 30 秒也返回空（`TimeoutExpired`），不会抛异常。

---

#### 6. issues.py — Bug 队列管理（TEST-ISSUES.md）

**解决什么问题**：xtest 发现测试失败时需要写入 Bug 条目，xdebug 修复后需要更新状态。这涉及编号分配、状态流转、并发写入等问题。这个脚本封装了所有 TEST-ISSUES.md 的读写操作。

**谁调用**：
- **xtest** 阶段 3 — `next-id` 获取编号 + Edit 写入 🔴 条目；阶段 4 — `list --status 已修复` 找 🟢 条目做复测；`status` 改为 ✅
- **xdebug** 阶段 1 — `list --status 待修` 展示可修复的条目；`status` 改为 🟡（修复中）；阶段 6 — `status` 改为 🟢（已修复）
- **`/xbase status`** — `stats` 展示各状态计数

**状态流转**：`🔴 待修 → 🟡 修复中 → 🟢 已修复 → ✅ 复测通过`

**API**：
```bash
# 列出全部问题
python3 .claude/skills/xtest/scripts/issues.py list <path>
# 输出：#001 🔴 待修 — 拖拽偏移问题

# 按状态过滤（待修 / 修复中 / 已修复 / 复测通过）
python3 .claude/skills/xtest/scripts/issues.py list <path> --status 待修

# 各状态计数统计
python3 .claude/skills/xtest/scripts/issues.py stats <path>
# 输出：🔴 3 / 🟡 1 / 🟢 2 / ✅ 5 / 总计 11

# 更新问题状态（原子操作，文件锁保护）
python3 .claude/skills/xtest/scripts/issues.py status <path> <id> <new_status>
# 例：status document/90-开发/TEST-ISSUES.md 003 修复中
# 也支持 emoji 别名：status ... 003 🟡
# 输出：#003: 🔴 待修 → 🟡 修复中

# 获取下一个可用编号并写入占位行（原子操作）
python3 .claude/skills/xtest/scripts/issues.py next-id <path>
# 输出：012（三位数编号）
# 文件末尾追加：### #012 🔴 [待填入]
# 如果上次的占位行还没填入，会复用已有编号，不重复追加
```

**并发安全**：所有写操作（`status`、`next-id`）使用 `fcntl.LOCK_EX` 文件锁 + read-modify-write 原子操作。多个 skill 同时操作同一个文件不会数据丢失。

---

#### 7. decision-log.py — 决策记录管理（DECIDE-LOG.md）

**解决什么问题**：和 issues.py 类似，封装 DECIDE-LOG.md 的读写操作 — 编号分配、搜索、列表展示。

**谁调用**：
- **xdecide** 阶段 2a — `next-id` 获取编号；阶段 2c — `list` 展示 + `search` 搜索
- **xdecide** 阶段 2a 步骤 2 — `search` 搜索历史相关决策，避免重复
- **xcommit** 阶段 3 — `list` 检查是否有未记录的决策

**API**：
```bash
# 列出所有决策
python3 .claude/skills/xdecide/scripts/decision-log.py list <path>
# 输出：D-001 双模型设计
#        D-002 命令系统放 Rust 侧

# 获取下一个可用编号（原子操作，复用未填占位行）
python3 .claude/skills/xdecide/scripts/decision-log.py next-id <path>
# 输出：003

# 按关键词搜索决策段落（搜索完整段落内容，不只是标题）
python3 .claude/skills/xdecide/scripts/decision-log.py search <path> <关键词>
# 例：search document/90-开发/DECIDE-LOG.md 动画
# 输出匹配的决策条目标题
```

**并发安全**：同 issues.py，写操作使用文件锁保护。

---

## 文件结构

```
.claude/skills/
├── README.md                 # 本文档
├── PRINCIPLES.md             # 设计原则
│
├── xbase/                    # ⓪ 共享基础设施（初始化入口）
│   ├── SKILL.md              # 初始化编排（/xbase init/status/reset）
│   ├── SKILL-STATE.md        # 运行时状态（模板预置，skill 初始化时填值）
│   ├── scripts/
│   │   ├── skill-state.py        # 状态管理（check/read/write/delete/reset-all）
│   │   └── artifact-create.py    # 产出物骨架创建（从 format 模板生成）
│   └── references/
│       ├── phase0-template.md    # 阶段 0 标准流程模板（所有 skill 共享）
│       └── dedup-protocol.md     # 去重流程模板
│
├── xtest/                    # ① 测试（入口）
│   ├── SKILL.md              # 自动化 + 手动逐项验证
│   ├── scripts/
│   │   └── issues.py             # TEST-ISSUES.md 操作（list/status/next-id/stats）
│   └── references/
│       ├── checklist-format.md       # TEST-CHECKLIST.md 格式规范
│       └── test-issues-format.md     # TEST-ISSUES.md 格式规范
│
├── xdebug/                   # ② 调试（核心）
│   ├── SKILL.md              # 6 个阶段：确认问题→加日志→引导操作→分析→修复→收尾
│   └── references/
│       ├── debug-log-format.md   # DEBUG-LOG.md 格式规范
│       └── infra-setup.md        # 调试基础设施检查流程（xtest 也引用）
│
├── xlog/                     # ③ 日志补全（辅助，常被 xdebug 自动调用）
│   ├── SKILL.md              # 扫描 + 补盲区 + 纠正不规范
│   └── references/
│       ├── log-rules-format.md      # LOG-RULES.md 格式规范
│       └── log-coverage-format.md   # LOG-COVERAGE.md 格式规范
│
├── xreview/                  # ④ 代码审查
│   ├── SKILL.md              # 三维度审查（规范/架构/安全）
│   └── references/
│       └── review-rules-format.md   # REVIEW-RULES.md 格式规范
│
├── xdecide/                  # ⑤ 决策记录（按需）
│   ├── SKILL.md              # 引导式决策 + 快速录入 + 回顾修订
│   ├── scripts/
│   │   └── decision-log.py       # DECIDE-LOG.md 操作（list/next-id/search）
│   └── references/
│       └── decision-format.md       # DECIDE-LOG.md 格式规范
│
├── xdoc/                     # ⑥ 文档维护（按需）
│   ├── SKILL.md              # 健康检查 + 一致性验证
│   └── references/
│       └── doc-rules-format.md      # DOC-RULES.md 格式规范
│
└── xcommit/                  # ⑦ 提交（出口）
    ├── SKILL.md              # 预检 + 文档完整性 + 规范化提交
    ├── scripts/
    │   └── git-context.py        # Git 上下文收集（commit/diff/changed-files）
    └── references/
        └── commit-rules-format.md   # COMMIT-RULES.md 格式规范
```

---

## 使用的 Claude Code 官方特性

| 特性 | 说明 | 使用情况 |
|------|------|----------|
| `user-invocable` | 用户可通过 `/` 菜单直接调用 | 所有 8 个 skill |
| `argument-hint` | `/` 菜单中显示参数提示 | 所有 skill 均有提示 |
| `$ARGUMENTS` | 接收用户传入的参数 | 支持快捷跳过阶段（如 `/xdebug 拖拽偏移`） |
| `!`command`` | Skill 加载时自动执行命令 | 预加载 SKILL-STATE.md 状态 |
| `allowed-tools` | 限制 skill 可使用的工具集 | 各 skill 按需配置 |

## 设计原则

详见 `PRINCIPLES.md`：

1. **所有项目通用** — 不硬编码路径/命令，项目差异通过动态探测解决
2. **选项优先于打字** — AskUserQuestion 选项驱动，Other 兜底自由输入，每轮一个问题
3. **操作步骤要具体** — 给用户 1-2-3 具体步骤，不泛泛说"请操作"

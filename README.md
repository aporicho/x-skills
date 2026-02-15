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
| `/xbase reinit <skill>` | 重新初始化单个 skill |

**管理的共享资源**：
- `SKILL-STATE.md` — 所有 skill 的运行时状态（项目类型、路径、初始化日期）
- 3 个共享 Python 工具（`xbase/scripts/`）— 状态管理、产出物检测、去重扫描
- 3 个领域 Python 工具 — Git 上下文（`xcommit/scripts/`）、Bug 队列（`xtest/scripts/`）、决策记录（`xdecide/scripts/`）

**关键设计**：xbase 自身不创建任何工作产出物，只做编排 — "谁的产出物谁负责创建"。`/xbase init` 启动 7 个并行 Task 子 agent，各自执行自己的阶段 0。

---

### 1. xtest — 测试（入口：发现问题）

**做什么**：自动化测试 + 手动逐项验证，维护测试清单和 Bug 队列。

**典型触发时机**：开发完功能后验证、日常回归测试、修复后复测。

**阶段**：
| 阶段 | 做什么 | 是否需要用户参与 |
|------|--------|---------------|
| 0 | 探测项目 + 扫描代码生成测试清单 + 创建 TEST-ISSUES.md | 否（自动） |
| 1 | 选择测试类型（自动化 / 手动 / 指定编号） | 选项 |
| 2a | 运行自动化测试命令，映射结果到清单 | 否（自动） |
| 2b | 逐项引导手动测试（每项给具体操作步骤） | 逐项选项 |
| 3 | 失败 → 后台分析日志 + 写入 TEST-ISSUES.md，不打断测试 | 自动 |
| 4 | 汇总 → 衔接 xdebug 修复 / xcommit 提交 / 继续 | 选项 |

**产出物**：`TEST-CHECKLIST.md`（测试清单）、`TEST-ISSUES.md`（Bug 队列）

**关键设计**：首次生成清单时用**并行子 agent** 扫描不同代码区域加速；增量更新时只扫描 `git diff` 变更文件。

**下一步去哪**：测试失败 → 选"立即修复" → 进入 **xdebug**

---

### 2. xdebug — 调试（核心：定位修复）

**做什么**：引导式调试循环 — 加日志 → 构建运行 → 引导用户操作 → 分析日志 → 修复 → 验证。

**典型触发时机**：xtest 发现 Bug 后衔接过来、用户直接报告问题。

**阶段**：
| 阶段 | 做什么 | 是否需要用户参与 |
|------|--------|---------------|
| 0 | 探测项目 + 创建 DEBUG-LOG.md + 验证调试基础设施 | 否（自动） |
| 1 | 确认要调试什么（从 issue 选 / 探索 / 描述） | 选项 |
| 2 | 判断日志是否足够 → 不够则启动 **xlog** 子 agent 补 → 构建运行 | 否（自动） |
| 3 | 给用户**具体操作步骤**去复现 Bug | 选项 |
| 4 | 读取日志分析根因 | 选项（确认分析） |
| 5 | 修改代码修复 → 重新构建运行 → 引导验证 | 选项（确认修复） |
| 6 | 更新 DEBUG-LOG.md + TEST-ISSUES.md 状态 → 衔接下一步 | 选项 |

**产出物**：`DEBUG-LOG.md`（Bug 修复日志）、`scripts/run.sh`（调试运行脚本）

**关键设计**："先加日志后改代码，不盲猜"。阶段 2 自动调用 xlog 补日志，阶段 4 基于日志分析，不靠猜。

**下一步去哪**：修复完成 → 选"提交变更" → **xcommit**；涉及技术决策 → **xdecide**

---

### 3. xlog — 日志补全（辅助：通常由 xdebug 自动调用）

**做什么**：建立日志规范，扫描代码补充诊断日志、纠正不规范日志。

**典型触发时机**：xdebug 阶段 2 发现日志不足时**自动**启动 xlog 子 agent；也可独立使用给特定模块补日志。

**阶段**：
| 阶段 | 做什么 | 是否需要用户参与 |
|------|--------|---------------|
| 0 | 扫描项目日志系统 + 生成 LOG-RULES.md 和 LOG-COVERAGE.md | 否（自动） |
| 1 | 选择范围（盲区模块 / 指定文件 / 全项目） | 选项 |
| 2 | 读规范 → 扫描目标代码 → 补盲区 + 纠正不规范 → 确认编译 | 否（自动） |
| 3 | 汇报变更 | 选项 |

**产出物**：`LOG-RULES.md`（日志规范）、`LOG-COVERAGE.md`（覆盖度跟踪）

**关键设计**：被 xdebug 调用时以 Task 子 agent 运行，自动完成后返回，不打断调试主流程。

---

### 4. xreview — 代码审查（质量：修复后检查）

**做什么**：基于 REVIEW-RULES.md 进行三维度审查（规范合规 / 架构质量 / 安全健壮），逐项决策。

**典型触发时机**：修复完 Bug 后审查代码质量、提交前代码检查、定期代码审计。

**阶段**：
| 阶段 | 做什么 | 是否需要用户参与 |
|------|--------|---------------|
| 0 | 扫描代码 + CLAUDE.md → 生成 REVIEW-RULES.md | 否（自动） |
| 1 | 选择审查范围（未提交 / 最近提交 / 指定路径） | 选项 |
| 2 | 逐条审查，每发现问题 → 立即修 / 记录 / 忽略 | 逐项选项 |
| 3 | 汇总 → 衔接 xcommit / xdecide | 选项 |

**产出物**：`REVIEW-RULES.md`（审查规范）

**关键设计**：规则来源两层 — CLAUDE.md 提取禁忌/必须/架构约束 + 代码扫描推导缩进/命名/注释语言等。每条规则标注来源。

**下一步去哪**：发现架构问题 → **xdecide**；审查通过 → **xcommit**

---

### 5. xdecide — 决策记录（按需：涉及技术决策时）

**做什么**：引导式决策（分析方案 + 利弊权衡 + 结论记录）+ 快速录入 + 回顾修订。

**典型触发时机**：xdebug 修复涉及架构选择、xreview 发现需要决策的问题、独立的技术方案讨论。

**阶段**：
| 阶段 | 做什么 | 是否需要用户参与 |
|------|--------|---------------|
| 0 | 探测已有决策文件 + 创建 DECIDE-LOG.md | 否（自动） |
| 1 | 选择模式（新决策 / 快速录入 / 回顾） | 选项 |
| 2a | 引导式：背景 → 扫描代码分析方案 → 推荐 → 确认 → 写入 | 逐步选项 |
| 2b | 快速录入：一句话背景 + 结论 → 格式化写入 | 选项 |
| 2c | 回顾：列表展示 → 选择 → 追加修订 | 选项 |
| 3 | 衔接 xcommit / 继续 / 结束 | 选项 |

**产出物**：`DECIDE-LOG.md`（决策记录）

**关键设计**：新决策前搜索历史决策，避免重复或矛盾。修订不删除原文，保留决策演化历史。

**下一步去哪**：记录完成 → **xcommit**

---

### 6. xdoc — 文档维护（按需：文档不同步时）

**做什么**：文档健康检查（断链 / 格式 / 结构）+ 代码-文档一致性验证。

**典型触发时机**：代码改了但文档没跟上、定期文档清理、发布前检查。

**阶段**：
| 阶段 | 做什么 | 是否需要用户参与 |
|------|--------|---------------|
| 0 | 扫描文档目录 + 检查脚本 → 生成 DOC-RULES.md | 否（自动） |
| 1 | 选择任务（健康检查 / 一致性验证 / 指定文件） | 选项 |
| 2a | 运行检查脚本 + 格式规范检查 | 否（自动） |
| 2b | 对比 git log 和代码-文档映射，找不一致 | 否（自动） |
| 3 | 逐项修复（自动修 / 跳过 / 忽略） | 逐项选项 |
| 4 | 汇报 → 衔接 xcommit | 选项 |

**产出物**：`DOC-RULES.md`（文档规范）

**下一步去哪**：文档修复后 → **xcommit**

---

### 7. xcommit — 提交（出口：所有变更的终点）

**做什么**：预检脚本 + 文档完整性检查 + 规范化 commit。

**典型触发时机**：任何 skill 完成工作后的最后一步，也可独立使用。几乎所有 skill 的收尾选项都能衔接到这里。

**阶段**：
| 阶段 | 做什么 | 是否需要用户参与 |
|------|--------|---------------|
| 0 | 分析 git log + CLAUDE.md → 生成 COMMIT-RULES.md | 否（自动） |
| 1 | 检查变更（未暂存文件处理） | 选项 |
| 2 | 运行 COMMIT-RULES.md 中列出的预检脚本 | 选项（失败时） |
| 3 | 文档完整性检查（Bug 修复是否更新了 DEBUG-LOG.md 等） | 选项（提醒，不阻断） |
| 4 | 生成 commit message + 确认 + 执行提交 | 选项 |

**产出物**：`COMMIT-RULES.md`（提交规范）

**关键设计**：文档完整性检查是建议不是阻断 — 只提醒"看起来是 Bug 修复但 DEBUG-LOG.md 没更新"，用户可选择忽略。

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
产出物三态检测（artifact-check.py）
    ├─ 不存在 → 按 references/*-format.md 生成
    ├─ 格式不符 → 问用户是否迁移
    └─ 已就绪 → 跳过
    ↓
写入状态（skill-state.py write）
    ↓
去重（dedup-scan.py）
```

**为什么这样设计**：
- **`check` 快速跳过**：已初始化的 skill 只需一次进程调用就知道可以跳过，不做任何多余工作
- **项目信息共享**：第一个初始化的 skill 写入项目信息，后续 skill 直接复用
- **三态检测**：兼容已有文件 — 如果用户已经手写了 REVIEW-RULES.md，不会覆盖

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

`dedup-scan.py` 内置 `KEEP_PATTERNS` 保护禁令行不被误替换。替换前展示 diff 预览，等用户确认。

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

#### 3. artifact-check.py — 产出物三态检测 + 骨架创建

**解决什么问题**：每个 skill 的阶段 0 需要判断"我的产出物文件已存在？格式对不对？需要创建吗？"。这个脚本统一处理这个逻辑，避免每个 skill 各写一套。

**谁调用**：各 skill 阶段 0 的"产出物三态检测"步骤。`/xbase status` 也用 `batch-check` 查看全部状态。

**怎么工作**：
1. 动态扫描所有 `references/*-format.md` 文件，从 H1 标题提取产出物文件名，从 H2 标题提取必需段落标记
2. `check` 时：文件不存在 → `not_found`；存在但缺少必需段落 → `format_mismatch`；段落齐全 → `ready`
3. `create` 时：读取 format 文件，提取标题结构生成骨架文件
4. 如果 format 文件的 H1 不是标准命名，会从**文件名 fallback 推导**（如 `commit-rules-format.md` → `COMMIT-RULES.md`）

**新增 skill 如何适配**：只需在 `references/` 目录放一个 `xxx-format.md` 文件，artifact-check.py 会自动发现并纳入检测。不需要改任何代码。

**API**：
```bash
# 检测单个产出物状态
python3 .claude/skills/xbase/scripts/artifact-check.py check <artifact_name> <expected_path>
# → 输出 "ready" / "format_mismatch" / "not_found"
# 例：check commit-rules document/90-开发/COMMIT-RULES.md

# 从 format 文件生成骨架
python3 .claude/skills/xbase/scripts/artifact-check.py create <artifact_name> <target_path>
# 例：create commit-rules document/90-开发/COMMIT-RULES.md

# 批量检测所有已知产出物（JSON 输出）
python3 .claude/skills/xbase/scripts/artifact-check.py batch-check <output_dir>
# 例：batch-check document/90-开发
```

---

#### 4. dedup-scan.py — 去重扫描

**解决什么问题**：CLAUDE.md 里可能写了"Git 提交规范"的详细规则，xcommit 又生成了 COMMIT-RULES.md 覆盖同样内容。两处维护容易不同步。这个脚本找出这些重复，建议替换为指针。

**谁调用**：各 skill 阶段 0 末尾的"去重子步骤"；`/xbase init` 步骤 3 串行去重时用 `scan-all` 一次扫描所有 skill。

**怎么工作**：
1. 每个 skill 有预定义的去重规则（关键词 + 目标段落 + 替换指针文本）
2. 扫描 CLAUDE.md / MEMORY.md 中匹配关键词的行
3. 匹配到的行如果**命中 KEEP_PATTERNS**（禁令/方法论）→ 保留不替换
4. 其余匹配行 → 输出为 JSON，skill 拿到后展示 diff 预览让用户确认

**KEEP_PATTERNS（9 条保护规则）**：
- `禁止.*print` / `修复 Bug.*必须.*更新` / `任何.*决策.*必须.*记录`
- `日志规范详见.*skill` / `先加日志.*不要盲猜` / `绝对不修改.*pbxproj`
- `禁止部分提交` / `文档优先` / `先规划后执行`

**API**：
```bash
# 扫描单个 skill 的重复内容
python3 .claude/skills/xbase/scripts/dedup-scan.py scan --skill <name> --claude-md <path> [--memory-md <path>]
# 例：scan --skill xcommit --claude-md CLAUDE.md --memory-md ~/.claude/.../MEMORY.md

# 一次扫描所有 skill（/xbase init 步骤 3 用）
python3 .claude/skills/xbase/scripts/dedup-scan.py scan-all --claude-md <path> [--memory-md <path>]
```

**输出示例**：
```json
{
  "matches": [
    {
      "skill": "xcommit",
      "file": "CLAUDE.md",
      "lines": [45, 46, 47],
      "action": "replace",
      "pointer": "Git 提交规范详见 COMMIT-RULES.md（路径见 SKILL-STATE.md）"
    }
  ]
}
```

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
│   │   ├── artifact-check.py     # 产出物三态检测 + 骨架创建
│   │   └── dedup-scan.py         # 去重扫描（CLAUDE.md/MEMORY.md 重复检测）
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

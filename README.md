# xSkills

Claude Code 自定义工作流 skill 集合 — 用 `/x*` 命令驱动调试、测试、日志、审查、提交、文档、决策的完整开发循环。

**核心理念**：每个 skill 都是"阶段化推进的交互式工作流"，通过 `AskUserQuestion` 选项一步步引导，可独立使用也可互相衔接。skill 自动适配任何项目（不硬编码路径和命令）。

## Quick Start

```bash
/xbase init          # 一键初始化所有 skill（探测项目 → 并行创建产出物 → 去重）
/xdebug 拖拽偏移      # 直接开始调试一个 bug
/xtest 手动           # 启动手动测试流程
/xcommit             # 预检 + 文档完整性 + 规范化提交
/xbase status        # 查看所有 skill 的初始化状态
```

各 skill 可独立运行（首次使用时自动初始化），`/xbase init` 只是批量快捷入口。

---

## 整体架构

### 两层结构

```
┌──────────────────────────────────────────────────────┐
│  7 个工作流 skill（用户直接交互）                       │
│  xdebug  xtest  xlog  xreview  xcommit  xdoc  xdecide │
├──────────────────────────────────────────────────────┤
│  xbase — 共享基础设施                                  │
│  状态管理 · 项目探测 · 产出物检测 · 去重 · Git 上下文     │
│  (skill-state.py · project-detect.py · artifact-check.py │
│   dedup-scan.py · git-context.py · issues.py · ...)     │
└──────────────────────────────────────────────────────┘
```

- **上层**：7 个工作流 skill，每个有自己的 `SKILL.md`（定义阶段和流程）和 `references/` 目录（格式规范）
- **下层**：xbase 提供共享 Python 工具，所有 skill 复用，不各自造轮子

### 三类文件

| 类别 | 位置 | 作用 | 谁读 |
|------|------|------|------|
| **SKILL.md** | 每个 skill 目录下 | Claude 读取后知道怎么执行工作流 | Claude（prompt） |
| **references/*.md** | 每个 skill 的 references/ | 产出物的格式规范，生成时参照 | Claude（生成时参考） |
| **产出物** | 目标项目的文档目录 | skill 运行后创建的实际文件 | Claude + 用户 |

**一句话总结**：SKILL.md 告诉 Claude "做什么"，references/ 告诉 Claude "格式长什么样"，产出物是最终结果。

---

## 每个 Skill 详解

### xdebug — 调试

**做什么**：引导式调试循环 — 加日志 → 构建运行 → 引导用户操作 → 分析日志 → 修复 → 验证。

**阶段**：
| 阶段 | 做什么 | 是否需要用户参与 |
|------|--------|---------------|
| 0 | 探测项目 + 创建 DEBUG-LOG.md + 验证调试基础设施 | 否（自动） |
| 1 | 确认要调试什么（从 issue 选 / 探索 / 描述） | 选项 |
| 2 | 判断日志是否足够 → 不够则启动 xlog 子 agent 补 → 构建运行 | 否（自动） |
| 3 | 给用户**具体操作步骤**去复现 Bug | 选项 |
| 4 | 读取日志分析根因 | 选项（确认分析） |
| 5 | 修改代码修复 → 重新构建运行 → 引导验证 | 选项（确认修复） |
| 6 | 更新 DEBUG-LOG.md + TEST-ISSUES.md 状态 → 衔接下一步 | 选项 |

**产出物**：`DEBUG-LOG.md`（Bug 修复日志）、`scripts/run.sh`（调试运行脚本）

**关键设计**："先加日志后改代码，不盲猜"。阶段 2 自动调用 xlog 补日志，阶段 4 基于日志分析，不靠猜。

---

### xtest — 测试

**做什么**：自动化测试 + 手动逐项验证，维护测试清单和 Bug 队列。

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

---

### xlog — 日志补全

**做什么**：建立日志规范，扫描代码补充诊断日志、纠正不规范日志。

**阶段**：
| 阶段 | 做什么 | 是否需要用户参与 |
|------|--------|---------------|
| 0 | 扫描项目日志系统 + 生成 LOG-RULES.md 和 LOG-COVERAGE.md | 否（自动） |
| 1 | 选择范围（盲区模块 / 指定文件 / 全项目） | 选项 |
| 2 | 读规范 → 扫描目标代码 → 补盲区 + 纠正不规范 → 确认编译 | 否（自动） |
| 3 | 汇报变更 | 选项 |

**产出物**：`LOG-RULES.md`（日志规范）、`LOG-COVERAGE.md`（覆盖度跟踪）

**关键设计**：也被 xdebug 作为子 agent 调用 — xdebug 阶段 2 判断日志不足时，自动启动 xlog 子 agent 给目标区域补日志。

---

### xreview — 代码审查

**做什么**：基于 REVIEW-RULES.md 进行三维度审查（规范合规 / 架构质量 / 安全健壮），逐项决策。

**阶段**：
| 阶段 | 做什么 | 是否需要用户参与 |
|------|--------|---------------|
| 0 | 扫描代码 + CLAUDE.md → 生成 REVIEW-RULES.md | 否（自动） |
| 1 | 选择审查范围（未提交 / 最近提交 / 指定路径） | 选项 |
| 2 | 逐条审查，每发现问题 → 立即修 / 记录 / 忽略 | 逐项选项 |
| 3 | 汇总 → 衔接 xcommit / xdecide | 选项 |

**产出物**：`REVIEW-RULES.md`（审查规范）

**关键设计**：规则来源两层 — CLAUDE.md 提取禁忌/必须/架构约束 + 代码扫描推导缩进/命名/注释语言等。每条规则标注来源。

---

### xcommit — 提交

**做什么**：预检脚本 + 文档完整性检查 + 规范化 commit。

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

### xdoc — 文档维护

**做什么**：文档健康检查（断链 / 格式 / 结构）+ 代码-文档一致性验证。

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

---

### xdecide — 决策记录

**做什么**：引导式决策（分析方案 + 利弊权衡 + 结论记录）+ 快速录入 + 回顾修订。

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
项目探测（project-detect.py）
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
步骤 1：项目探测（xbase 直接执行 project-detect.py）
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

## Python 工具 API 参考

所有工具在 `xbase/` 目录下，被各 skill 共同复用。

### skill-state.py — 状态管理

```bash
python3 .claude/skills/xbase/skill-state.py check <skill>            # → "initialized" / "not_found"
python3 .claude/skills/xbase/skill-state.py check-and-read <skill>   # check + read 合并（省一次进程启动）
python3 .claude/skills/xbase/skill-state.py read                     # 输出完整状态
python3 .claude/skills/xbase/skill-state.py write <skill> <k> <v> [...]  # 写入 skill 段（自动加 initialized 日期）
python3 .claude/skills/xbase/skill-state.py write-info <k> <v> [...]     # 写入项目信息段
python3 .claude/skills/xbase/skill-state.py delete <skill>           # 清空 skill 段的值（reinit 用）
python3 .claude/skills/xbase/skill-state.py delete-info              # 清空项目信息段
python3 .claude/skills/xbase/skill-state.py reset-all                # 恢复初始模板（清空所有）
```

### issues.py — TEST-ISSUES.md 操作

```bash
python3 .claude/skills/xbase/issues.py list <path>                    # 列出全部
python3 .claude/skills/xbase/issues.py list <path> --status <状态>    # 按状态过滤（待修/修复中/已修复/复测通过）
python3 .claude/skills/xbase/issues.py stats <path>                   # 各状态计数
python3 .claude/skills/xbase/issues.py status <path> <id> <new>       # 更新状态（支持 emoji 别名如 🟡）
python3 .claude/skills/xbase/issues.py next-id <path>                 # 获取下一个编号（自动检测未填占位行）
```

所有写操作使用 `fcntl.LOCK_EX` 文件锁，原子执行。`next-id` 会检测是否有未填入的 `[待填入]` 占位行，避免重复追加。

### decision-log.py — DECIDE-LOG.md 操作

```bash
python3 .claude/skills/xbase/decision-log.py list <path>              # 列出全部
python3 .claude/skills/xbase/decision-log.py next-id <path>           # 下一个编号（自动检测未填占位行）
python3 .claude/skills/xbase/decision-log.py search <path> <关键词>   # 搜索
```

### artifact-check.py — 产出物三态检测 + 骨架创建

```bash
python3 .claude/skills/xbase/artifact-check.py check <name> <path>        # → "ready" / "format_mismatch" / "not_found"
python3 .claude/skills/xbase/artifact-check.py create <name> <path>        # 从 format 文件生成骨架
python3 .claude/skills/xbase/artifact-check.py batch-check <output_dir>    # JSON 汇总所有产出物状态
```

动态扫描 `references/*-format.md` 建立 artifact → format 映射。新增 skill 只需放格式文件即可自动适配。

### dedup-scan.py — 去重扫描

```bash
python3 .claude/skills/xbase/dedup-scan.py scan --skill <name> --claude-md <path> [--memory-md <path>]
python3 .claude/skills/xbase/dedup-scan.py scan-all --claude-md <path> [--memory-md <path>]
```

扫描 CLAUDE.md / MEMORY.md 中与产出物重复的内容，输出 JSON。内置 `KEEP_PATTERNS` 保护禁令/方法论行。

### git-context.py — Git 上下文收集

```bash
python3 .claude/skills/xbase/git-context.py commit-context                           # xcommit 全流程所需（含提交风格分析）
python3 .claude/skills/xbase/git-context.py diff-context [--scope staged|unstaged|both]  # xreview 差异
python3 .claude/skills/xbase/git-context.py changed-files [--scope staged|recent]    # xtest 增量
```

一次调用收集多个 git 命令输出（JSON），替代多次 Bash 调用。

### project-detect.py — 项目探测

```bash
python3 .claude/skills/xbase/project-detect.py detect [--project-root <path>]            # JSON 输出探测结果
python3 .claude/skills/xbase/project-detect.py detect-and-write [--project-root <path>]  # 探测并写入 SKILL-STATE.md
```

扫描项目根目录标志文件（Cargo.toml、package.json、*.xcodeproj 等）识别语言/框架/构建命令，读取 CLAUDE.md 提取日志系统等额外信息。

---

## 文件结构

```
.claude/skills/
├── README.md                 # 本文档
├── PRINCIPLES.md             # 设计原则
│
├── xbase/                    # 共享基础设施
│   ├── SKILL.md              # 初始化编排（/xbase init/status/reset）
│   ├── SKILL-STATE.md        # 运行时状态（模板预置，skill 初始化时填值）
│   ├── skill-state.py        # 状态管理（check/read/write/delete/reset-all）
│   ├── project-detect.py     # 项目探测（语言/框架/构建命令自动识别）
│   ├── artifact-check.py     # 产出物三态检测 + 骨架创建
│   ├── dedup-scan.py         # 去重扫描（CLAUDE.md/MEMORY.md 重复检测）
│   ├── git-context.py        # Git 上下文收集（commit/diff/changed-files）
│   ├── issues.py             # TEST-ISSUES.md 操作（list/status/next-id/stats）
│   ├── decision-log.py       # DECIDE-LOG.md 操作（list/next-id/search）
│   └── references/
│       ├── phase0-template.md    # 阶段 0 标准流程模板（所有 skill 共享）
│       ├── infra-setup.md        # 调试基础设施检查流程（xdebug/xtest 共享）
│       ├── dedup-protocol.md     # 去重流程模板
│       └── test-issues-format.md # TEST-ISSUES.md 格式规范
│
├── xdebug/                   # 调试工作流
│   ├── SKILL.md              # 6 个阶段：确认问题→加日志→引导操作→分析→修复→收尾
│   └── references/
│       └── debug-log-format.md   # DEBUG-LOG.md 格式规范
│
├── xtest/                    # 测试工作流
│   ├── SKILL.md              # 自动化 + 手动逐项验证
│   └── references/
│       └── checklist-format.md   # TEST-CHECKLIST.md 格式规范
│
├── xlog/                     # 日志补全
│   ├── SKILL.md              # 扫描 + 补盲区 + 纠正不规范
│   └── references/
│       ├── log-rules-format.md      # LOG-RULES.md 格式规范
│       └── log-coverage-format.md   # LOG-COVERAGE.md 格式规范
│
├── xreview/                  # 代码审查
│   ├── SKILL.md              # 三维度审查（规范/架构/安全）
│   └── references/
│       └── review-rules-format.md   # REVIEW-RULES.md 格式规范
│
├── xcommit/                  # 提交工作流
│   ├── SKILL.md              # 预检 + 文档完整性 + 规范化提交
│   └── references/
│       └── commit-rules-format.md   # COMMIT-RULES.md 格式规范
│
├── xdoc/                     # 文档维护
│   ├── SKILL.md              # 健康检查 + 一致性验证
│   └── references/
│       └── doc-rules-format.md      # DOC-RULES.md 格式规范
│
└── xdecide/                  # 决策记录
    ├── SKILL.md              # 引导式决策 + 快速录入 + 回顾修订
    └── references/
        └── decision-format.md       # DECIDE-LOG.md 格式规范
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

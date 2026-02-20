# xSkills

Claude Code 自定义工作流 skill 集合 — 用 `/x*` 命令驱动调试、测试、日志、审查、提交、文档、决策的完整开发循环。

## Quick Start

```bash
/xbase   init          # 一键初始化所有 skill
/xdebug  拖拽偏移      # 调试一个 bug
/xtest   手动          # 手动测试
/xcommit               # 规范化提交
/xbase   status        # 查看初始化状态
```

各 skill 可独立运行（首次使用时自动初始化），`/xbase init` 只是批量快捷入口。

## Skills

| 命令 | 用途 | 产出物 |
|------|------|--------|
| `/xbase` | 初始化编排 + 状态管理 | `SKILL-STATE.md` |
| `/xtest` | 自动化 + 手动测试，维护 Bug 队列 | `TEST-CHECKLIST.md`、`TEST-ISSUES.md` |
| `/xdebug` | 引导式调试循环（加日志→运行→分析→修复） | `DEBUG-LOG.md`、`scripts/run.sh` |
| `/xlog` | 日志规范 + 盲区扫描补全 | `LOG-RULES.md`、`LOG-COVERAGE.md` |
| `/xreview` | 三维度代码审查（规范/架构/安全） | `REVIEW-RULES.md` |
| `/xdecide` | 引导式技术决策记录 | `DECIDE-LOG.md` |
| `/xdoc` | 文档健康检查 + 代码-文档一致性 | `DOC-RULES.md` |
| `/xcommit` | 预检 + 文档完整性 + 规范化 commit | `COMMIT-RULES.md` |

每个 skill 的详细流程见各自的 `SKILL.md`。

## 架构

```
┌─────────────────────────────────────────────────────┐
│  7 个工作流 skill（典型使用顺序）                      │
│  xtest → xdebug → xlog → xreview → xdecide → xdoc → xcommit │
├─────────────────────────────────────────────────────┤
│  xbase — 共享基础设施                                │
│  状态管理 · 项目探测 · 产出物骨架创建 · 去重          │
└─────────────────────────────────────────────────────┘
```

**三类文件**：

- **SKILL.md** — Claude 读取后知道怎么执行工作流（prompt）
- **references/*.md** — 产出物的格式规范（生成时参考）
- **产出物** — skill 运行后在目标项目中创建的实际文件

## Skill 间衔接

skill 之间通过 AskUserQuestion 选项衔接，用户主动选择，不自动跳转：

```
xtest ──→ xdebug ──→ xlog       (测试发现 Bug → 调试 → 补日志)
              ├──→ xdecide      (修复涉及技术决策)
              └──→ xcommit      (修复完成 → 提交)
xreview ──→ xdecide / xcommit
xdoc ──→ xcommit
xdecide ──→ xcommit
```

## 共享工具

`xbase/scripts/` 下的共享工具：

| 工具 | 用途 |
|------|------|
| `skill-state.py` | SKILL-STATE.md 读写接口（check/read/write/delete/reset-all） |
| `artifact-create.py` | 从 `references/*-format.md` 生成产出物骨架 |
| `extract-section.py` | 从 init-steps.md 按节名（探测/创建/去重）提取内容 |

各 skill 的领域工具：

| 工具 | 位置 | 用途 |
|------|------|------|
| `git-context.py` | `xcommit/scripts/` | Git 上下文收集（status/diff/log） |
| `issues.py` | `xtest/scripts/` | TEST-ISSUES.md 操作（list/status/next-id/stats） |
| `decision-log.py` | `xdecide/scripts/` | DECIDE-LOG.md 操作（list/next-id/search） |

## 文件结构

```
.claude/skills/
├── README.md
├── PRINCIPLES.md
│
├── xbase/                        # 共享基础设施
│   ├── SKILL.md
│   ├── SKILL-STATE.md
│   ├── scripts/
│   │   ├── skill-state.py
│   │   ├── artifact-create.py
│   │   └── extract-section.py
│   └── references/
│       ├── init-steps.md               # 项目级探测/创建流程
│       ├── prep-steps.md               # 阶段 0 标准流程模板
│       └── infra-setup.md              # 调试基础设施检查（run.sh 格式规范）
│
├── xtest/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── issues.py
│   └── references/
│       ├── init-steps.md
│       ├── checklist-format.md
│       └── test-issues-format.md
│
├── xdebug/
│   ├── SKILL.md
│   └── references/
│       ├── init-steps.md
│       └── debug-log-format.md
│
├── xlog/
│   ├── SKILL.md
│   └── references/
│       ├── init-steps.md
│       ├── log-rules-format.md
│       └── log-coverage-format.md
│
├── xreview/
│   ├── SKILL.md
│   └── references/
│       ├── init-steps.md
│       └── review-rules-format.md
│
├── xdecide/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── decision-log.py
│   └── references/
│       ├── init-steps.md
│       └── decision-format.md
│
├── xdoc/
│   ├── SKILL.md
│   └── references/
│       ├── init-steps.md
│       └── doc-rules-format.md
│
└── xcommit/
    ├── SKILL.md
    ├── scripts/
    │   └── git-context.py
    └── references/
        ├── init-steps.md
        └── commit-rules-format.md
```

## 设计原则

详见 `PRINCIPLES.md`：

1. **所有项目通用** — 不硬编码路径/命令，项目差异通过动态探测解决
2. **选项优先于打字** — AskUserQuestion 选项驱动，Other 兜底自由输入
3. **操作步骤要具体** — 给用户 1-2-3 具体步骤，不泛泛说"请操作"

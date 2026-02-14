# xSkills

Claude Code 自定义工作流 skill 集合。通过 `/x*` 命令调用，引导式完成调试、测试、日志、审查、提交、文档、决策等开发任务。

## Skills 一览

| Skill | 命令 | 参数 | 用途 | 产出物 |
|-------|------|------|------|--------|
| xdebug | `/xdebug` | `[bug描述 \| #issue编号 \| reinit]` | 调试：构建运行 → 加日志 → 引导复现 → 定位修复 | DEBUG-LOG.md, run.sh |
| xtest | `/xtest` | `[自动化 \| 手动 \| reinit]` | 测试：自动化 + 手动逐项验证 | TEST-CHECKLIST.md, TEST-ISSUES.md |
| xlog | `/xlog` | `[文件/模块路径 \| reinit]` | 日志补全：建立规范，扫描代码补日志 | LOG-RULES.md, LOG-COVERAGE.md |
| xreview | `/xreview` | `[文件/目录路径 \| reinit]` | 代码审查：基于 REVIEW-RULES.md 三维度审查 | REVIEW-RULES.md |
| xcommit | `/xcommit` | `[commit消息 \| reinit]` | 提交：基于 COMMIT-RULES.md 预检 + 文档完整性 + 规范化 | COMMIT-RULES.md |
| xdoc | `/xdoc` | `[健康检查 \| 一致性 \| reinit]` | 文档维护：基于 DOC-RULES.md 健康检查 + 一致性验证 | DOC-RULES.md |
| xdecide | `/xdecide` | `[决策描述 \| review \| reinit]` | 决策记录：引导式决策 + 快速录入 + 回顾修订 | DECIDE-LOG.md |
| xbase | `/xbase` | `[init \| status \| reset \| reinit]` | 初始化与状态管理 + 共享基础 | SKILL-STATE.md |

所有 skill 共享 `reinit` 参数：强制重新初始化（删除状态 + 重新探测项目）。

## 产出物

各 skill 在目标项目中创建和维护的文件（位置根据项目结构动态判断）：

| 产出物 | 说明 | 创建 | 维护 |
|--------|------|------|------|
| `SKILL-STATE.md` | 运行时状态（项目类型、构建命令等探测结果） | 首个运行的 skill | 所有 skill 共同维护 |
| `DEBUG-LOG.md` | Bug 修复日志 | xdebug | xdebug |
| `scripts/run.sh`（或等价物） | 调试运行脚本（构建/启动/停止/日志） | xdebug 或 xtest（谁先需要） | xdebug、xtest |
| `TEST-CHECKLIST.md` | 测试清单（扫描代码生成，记录结果） | xtest | xtest |
| `TEST-ISSUES.md` | Bug 队列（状态流转：🔴→🟡→🟢→✅） | xtest | xtest 写入、xdebug 更新状态 |
| `LOG-RULES.md` | 日志规范（从代码扫描提取） | xlog | xlog |
| `LOG-COVERAGE.md` | 日志覆盖度跟踪 | xlog | xlog |
| `REVIEW-RULES.md` | 审查规范（代码扫描 + CLAUDE.md 提取） | xreview | xreview |
| `DECIDE-LOG.md` | 决策条目（编号递增，含背景/选项/结论） | xdecide | xdecide |
| `COMMIT-RULES.md` | 提交规范（git log 分析 + CLAUDE.md 提取） | xcommit | xcommit |
| `DOC-RULES.md` | 文档规范（目录结构 + 检查脚本 + 映射规则） | xdoc | xdoc |

## 工作流衔接

```
xtest ──→ xdebug ──→ xlog        (测试发现 Bug → 调试 → 补日志)
              ├──→ xdecide       (修复涉及技术决策 → 记录)
              └──→ xcommit       (修复完成 → 提交)

xreview ──→ xdecide              (审查发现架构问题 → 记录决策)
        └──→ xcommit             (审查修复后 → 提交)

xdoc ──→ xcommit                 (文档修复后 → 提交)

xdecide ──→ xcommit              (决策记录后 → 提交)
```

所有衔接通过 AskUserQuestion 选项触发，不自动跳转。

## 知识 Skill（非工作流）

以下 skill 不可直接调用（`user-invocable: false`），由 Claude Code 根据上下文自动匹配激活：

| Skill | 用途 |
|-------|------|
| appkit | AppKit/SwiftUI 平台专家 |
| calayer | CALayer/Core Animation 专家 |
| doc-sync | 文档维护专员 |
| logging | 日志补全专家 |
| rust-ffi | Rust FFI 专家 |
| sandbox | macOS 沙盒专家 |
| uiux | UI/UX 架构师 |

## 共享基础（xbase）

`/xbase` 既是可调用命令（一键初始化、查看状态、重置），也是所有 skill 引用的共享基础（项目探测流程、状态规范、衔接协议）。未运行 `/xbase` 时，各 skill 仍可独立初始化。

### 初始化架构

`/xbase init` 采用**编排模式**：xbase 自身只做项目探测，产出物创建委派给各 skill：

```
步骤 1：项目探测（xbase 直接执行）
步骤 2：并行执行各 skill 阶段 0（7 个 Task 子 agent 同时启动）
步骤 3：串行去重（逐个 skill 清理 CLAUDE.md / MEMORY.md 中的重复内容）
步骤 4：汇总展示
```

### 去重机制

各 skill 在阶段 0 末尾有**去重子步骤**：将 CLAUDE.md / MEMORY.md 中已被产出物覆盖的具体规范替换为指针，保留方法论/禁令。谁创建产出物，谁负责清理对应的重复内容。

| Skill | 可替换内容 |
|-------|-----------|
| xcommit | CLAUDE.md `## Git 提交规范` → 指向 COMMIT-RULES.md |
| xreview | CLAUDE.md `## 代码规范` → 指向 REVIEW-RULES.md |
| xdebug | MEMORY.md 中 DEBUG_LOG 格式说明 → 指向 DEBUG-LOG.md |
| xdecide | MEMORY.md 中决策记录格式说明 → 指向 DECIDE-LOG.md |
| xlog | MEMORY.md 中日志规则重复部分 → 指向 LOG-RULES.md |

### 状态管理（skill-state.py）

各 skill 在阶段 0 探测项目后将结果写入 `SKILL-STATE.md`，后续 session 直接复用，避免重复探测。也可通过 `/xbase init` 一次性完成所有 skill 的初始化。

```bash
python3 .claude/skills/xbase/skill-state.py check <skill>       # initialized / not_found
python3 .claude/skills/xbase/skill-state.py read                 # 输出完整状态
python3 .claude/skills/xbase/skill-state.py write <skill> <k> <v> [...]  # 写入 skill 段
python3 .claude/skills/xbase/skill-state.py write-info <k> <v> [...]     # 写入项目信息段
python3 .claude/skills/xbase/skill-state.py delete <skill>       # 删除 skill 段（reinit）
```

### TEST-ISSUES.md 管理（issues.py）

xtest 发现失败时写入 🔴 条目，xdebug 修复后改为 🟢，复测通过后改为 ✅。

```bash
python3 .claude/skills/xbase/issues.py list <path>                    # 列出全部
python3 .claude/skills/xbase/issues.py list <path> --status <状态>    # 按状态过滤
python3 .claude/skills/xbase/issues.py stats <path>                   # 各状态计数
python3 .claude/skills/xbase/issues.py status <path> <id> <new>       # 更新状态
python3 .claude/skills/xbase/issues.py next-id <path>                 # 下一个编号
```

状态流转：🔴 待修 → 🟡 修复中 → 🟢 已修复 → ✅ 复测通过

### 决策记录管理（decision-log.py）

```bash
python3 .claude/skills/xbase/decision-log.py list <path>              # 列出全部
python3 .claude/skills/xbase/decision-log.py next-id <path>           # 下一个编号
python3 .claude/skills/xbase/decision-log.py search <path> <关键词>   # 搜索
```

### 文件结构

```
xbase/
├── SKILL.md                  # 初始化编排 + 共享规范（项目探测、状态格式、衔接协议）
├── skill-state.py            # 状态管理脚本
├── issues.py                 # TEST-ISSUES.md 操作脚本
├── decision-log.py           # 决策记录操作脚本
├── SKILL-STATE.md            # 运行时状态（模板预置，skill 初始化时填值）
└── references/
    ├── infra-setup.md        # 调试基础设施检查流程（xdebug/xtest 共享）
    ├── phase0-template.md    # 阶段 0 标准流程模板
    └── test-issues-format.md # TEST-ISSUES.md 格式规范

xdebug/
├── SKILL.md
└── references/
    └── debug-log-format.md   # DEBUG-LOG.md 格式规范

xtest/
├── SKILL.md
└── references/
    └── checklist-format.md   # TEST-CHECKLIST.md 格式规范

xlog/
├── SKILL.md
└── references/
    ├── log-rules-format.md   # LOG-RULES.md 格式规范
    └── log-coverage-format.md   # LOG-COVERAGE.md 格式规范

xreview/
├── SKILL.md
└── references/
    └── review-rules-format.md   # REVIEW-RULES.md 格式规范
xcommit/
├── SKILL.md
└── references/
    └── commit-rules-format.md   # COMMIT-RULES.md 格式规范
xdoc/
├── SKILL.md
└── references/
    └── doc-rules-format.md      # DOC-RULES.md 格式规范
xdecide/
├── SKILL.md
└── references/
    └── decision-format.md   # 决策记录格式规范
```

## 使用的 Claude Code 官方特性

| 特性 | 说明 | 使用情况 |
|------|------|----------|
| `argument-hint` | `/` 菜单中显示参数提示 | 所有工作流 skill |
| `$ARGUMENTS` | 接收用户传入的参数，快捷跳过阶段 | 所有工作流 skill |
| `!`command`` | Skill 加载时自动执行命令，预注入状态 | 所有工作流 skill |
| `user-invocable` | 控制 skill 是否可被用户直接调用 | 知识 skill 设为 false |
| `allowed-tools` | 限制 skill 可使用的工具集 | 所有 skill |

## 设计原则

详见 `PRINCIPLES.md`：

1. **所有项目通用** — 不硬编码，项目差异通过动态探测解决
2. **选项优先于打字** — AskUserQuestion 选项驱动，Other 兜底，每轮一个问题
3. **操作步骤要具体** — 给用户 1-2-3 具体步骤，不泛泛说"请操作"

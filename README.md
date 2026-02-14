# xSkills

Claude Code 自定义工作流 skill 集合。通过 `/x*` 命令调用，引导式完成调试、测试、日志、审查、提交、文档、决策等开发任务。

## Skills 一览

| Skill | 命令 | 参数 | 用途 | 产出物 |
|-------|------|------|------|--------|
| xdebug | `/xdebug` | `[bug描述 \| #issue编号 \| reinit]` | 调试：构建运行 → 加日志 → 引导复现 → 定位修复 | DEBUG_LOG.md, run.sh |
| xtest | `/xtest` | `[自动化 \| 手动 \| reinit]` | 测试：自动化 + 手动逐项验证 | TEST-CHECKLIST.md, ISSUES.md |
| xlog | `/xlog` | `[文件/模块路径 \| reinit]` | 日志补全：建立规范，扫描代码补日志 | LOG-STANDARD.md, LOG-COVERAGE.md |
| xreview | `/xreview` | `[文件/目录路径 \| reinit]` | 代码审查：从 CLAUDE.md 提取规范，三维度审查 | — |
| xcommit | `/xcommit` | `[commit消息 \| reinit]` | 提交：自动预检 + 文档完整性检查 + 规范化 | git commit |
| xdoc | `/xdoc` | `[健康检查 \| 一致性 \| reinit]` | 文档维护：健康检查 + 代码-文档一致性验证 | — |
| xdecide | `/xdecide` | `[决策描述 \| review \| reinit]` | 决策记录：引导式决策 + 快速录入 + 回顾修订 | 决策记录文件 |
| xbase | — | — | 共享基础（不可直接调用） | SKILL-STATE.md |

所有 skill 共享 `reinit` 参数：强制重新初始化（删除状态 + 重新探测项目）。

## 产出物

各 skill 在目标项目中创建和维护的文件（位置根据项目结构动态判断）：

| 产出物 | 说明 | 创建 | 维护 |
|--------|------|------|------|
| `SKILL-STATE.md` | 运行时状态（项目类型、构建命令等探测结果） | 首个运行的 skill | 所有 skill 共同维护 |
| `DEBUG_LOG.md` | Bug 修复日志 | xdebug | xdebug |
| `scripts/run.sh`（或等价物） | 调试运行脚本（构建/启动/停止/日志） | xdebug 或 xtest（谁先需要） | xdebug、xtest |
| `TEST-CHECKLIST.md` | 测试清单（扫描代码生成，记录结果） | xtest | xtest |
| `ISSUES.md` | Bug 队列（状态流转：🔴→🟡→🟢→✅） | xtest | xtest 写入、xdebug 更新状态 |
| `LOG-STANDARD.md` | 日志规范（从代码扫描提取） | xlog | xlog |
| `LOG-COVERAGE.md` | 日志覆盖度跟踪 | xlog | xlog |
| 决策记录文件 | 决策条目（编号递增，含背景/选项/结论） | xdecide | xdecide |
| git commit | 规范化提交 | xcommit | — |
| — | xreview：审查结果通过 AskUserQuestion 逐项交互，不产出文件 | — | — |
| — | xdoc：直接修复文档问题，不产出额外文件 | — | — |

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

## 共享基础（xbase）

### 状态管理（skill-state.py）

各 skill 在阶段 0 探测项目后将结果写入 `SKILL-STATE.md`，后续 session 直接复用，避免重复探测。

```bash
python3 .claude/skills/xbase/skill-state.py check <skill>       # initialized / not_found
python3 .claude/skills/xbase/skill-state.py read                 # 输出完整状态
python3 .claude/skills/xbase/skill-state.py write <skill> <k> <v> [...]  # 写入 skill 段
python3 .claude/skills/xbase/skill-state.py write-info <k> <v> [...]     # 写入项目信息段
python3 .claude/skills/xbase/skill-state.py delete <skill>       # 删除 skill 段（reinit）
```

### ISSUES.md 管理（issues.py）

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
├── SKILL.md                  # 共享规范（项目探测、状态格式、衔接协议）
├── skill-state.py            # 状态管理脚本
├── issues.py                 # ISSUES.md 操作脚本
├── decision-log.py           # 决策记录操作脚本
├── SKILL-STATE.md            # 运行时状态（自动生成，git ignore）
└── references/
    ├── infra-setup.md        # 调试基础设施检查流程（xdebug/xtest 共享）
    ├── issues-format.md      # ISSUES.md 格式规范
    └── decision-format.md    # 决策记录格式规范

xdebug/
├── SKILL.md
└── references/
    └── debug-log-format.md   # DEBUG_LOG.md 格式规范

xtest/
├── SKILL.md
└── references/
    └── checklist-format.md   # TEST-CHECKLIST.md 格式规范

xlog/
├── SKILL.md
└── references/
    ├── log-standard-format.md   # LOG-STANDARD.md 格式规范
    └── log-coverage-format.md   # LOG-COVERAGE.md 格式规范

xreview/SKILL.md
xcommit/SKILL.md
xdoc/SKILL.md
xdecide/SKILL.md
```

## 使用的 Claude Code 官方特性

| 特性 | 说明 | 使用情况 |
|------|------|----------|
| `argument-hint` | `/` 菜单中显示参数提示 | 所有工作流 skill |
| `$ARGUMENTS` | 接收用户传入的参数，快捷跳过阶段 | 所有工作流 skill |
| `!`command`` | Skill 加载时自动执行命令，预注入状态 | xdebug/xtest/xlog |
| `disable-model-invocation` | 禁止模型自动触发，仅限手动调用 | xdebug |
| `allowed-tools` | 限制 skill 可使用的工具集 | 所有 skill |

## 设计原则

详见 `PRINCIPLES.md`：

1. **所有项目通用** — 不硬编码，项目差异通过动态探测解决
2. **选项优先于打字** — AskUserQuestion 选项驱动，Other 兜底，每轮一个问题
3. **操作步骤要具体** — 给用户 1-2-3 具体步骤，不泛泛说"请操作"

# xbase 问题追踪

> 通过模拟 7 个使用场景（全新项目 / 已有文件 / 二次 init / 中断恢复 / status / 间接触发 / 无 CLAUDE.md）发现。

## 修复追踪

| # | 类型 | 问题 | 状态 |
|---|------|------|------|
| P9 | Bug | xtest 全量生成需要 Task 权限，xbase 没有 | ✅ allowed-tools 已包含 Task |
| P1 | 设计矛盾 | 步骤 1B 三态判定与 init-steps 重复 | ✅ 步骤 1 集中探测（extract-section.py 提取探测节），步骤 2 集中创建 |
| P2 | 设计矛盾 | 步骤 3 统一去重与 init-steps 各自去重重复 | ✅ 删除步骤 3，init-steps 各自去重 |
| P8 | 设计矛盾 | description 误导（"自动调用 xbase"） | ✅ 修正 description |
| P4 | 缺失处理 | 迁移后旧文件处理未定义 | ❌ |
| P5 | 缺失处理 | 用户拒绝迁移后的行为未定义 | ❌ |
| P3 | 效率 | xdebug 和 xtest 重复验证调试基础设施 | ❌ |
| P7 | 效率 | status 重复读取状态 | ✅ 改用预加载结果 |
| P10 | 效率 | 顺序处理 7 个 skill 时 context 累积 | ❌ |

---

## Bug

### P9 — xbase 没有 Task 权限，但 xtest init-steps 需要 Task 启动并行子 agent

**场景**：全新项目首次 init

xbase SKILL.md 的 allowed-tools 是 `["Bash", "Read", "Edit", "Write", "Glob", "Grep", "AskUserQuestion"]`，没有 Task。

但 xtest init-steps.md 步骤 3 说"全量生成时用并行子 agent 加速：按语言/模块拆分，每个子 agent（Task 工具）扫描一个区域"。

当 xbase DCI 注入 xtest init-steps.md 并执行时，Claude 想启动 Task 子 agent 但没有权限 → **xtest 全量生成路径会失败**。

---

## 设计矛盾

### P1 — 步骤 1B 三态判定与 init-steps 重复

**场景**：所有 init

步骤 1B（SKILL.md 第 39-72 行）对 7 个 skill 的核心文件做全项目搜索 + 三态判定（✅ 已就绪 / 🔄 可改造 / ❌ 需新建），展示结果等用户确认。

步骤 2 的引言说"三态判定已在步骤 1 确定，直接使用"，但 DCI 注入的 init-steps.md 并不知道步骤 1 已经做过判定 — 它们各自包含完整的三态检测逻辑（"检测文件，判断状态：不存在→创建 / 存在但格式不符→迁移 / 存在且格式正确→跳过"）。

步骤 1B 的判定结果只是展示给用户看的，没有以任何机器可读的方式传递给步骤 2。Claude 实际执行时大概率会按 init-steps.md 的指示再做一遍检测。

**搜索做了两遍，判定做了两遍。**

### P2 — 步骤 3 统一去重与 init-steps 各自去重重复

**场景**：所有 init

**层 1**：每个 init-steps.md 的最后一步都有"去重：按 dedup-steps.md 流程执行"，并指明了各自的去重职责（如 xcommit 负责 CLAUDE.md `## Git 提交规范` → 替换为指向 COMMIT-RULES.md 的指针）。

**层 2**：xbase 步骤 3 `!cat dedup-steps.md`，内容是"读取 CLAUDE.md，读取本 skill 已创建的核心文件，对比识别重复段落"。

去重做了两次。且步骤 3 的 dedup-steps.md 中"本 skill"在 xbase 上下文中语义不清 — xbase 自己没有核心文件（除了 SKILL-STATE.md），Claude 不知道该对比什么。

### P8 — description 误导

**场景**：—

xbase SKILL.md frontmatter 的 description 说"其他 skill 未初始化时自动调用 xbase"。

实际行为：其他 skill 有自己的阶段 0（基于 prep-steps.md 模板），独立执行初始化，不调用 xbase。`/xbase init` 只在用户显式调用时运行。

---

## 缺失处理

### P4 — 迁移后旧文件处理未定义

**场景**：已有部分文件的项目 init

当步骤 1B 判定为 🔄 可改造（如项目有 `docs/debug-notes.md` 内容像 DEBUG-LOG 但格式不同），init-steps 的迁移逻辑是"保留内容，套用新格式"创建新文件（如 `docs/DEBUG-LOG.md`）。

但旧文件 `docs/debug-notes.md` 怎么处理？删不删？没有定义。用户可能困惑为什么有两个文件。

### P5 — 用户拒绝迁移后的行为未定义

**场景**：已有部分文件的项目 init

init-steps 中 🔄 状态会 AskUserQuestion "是否迁移"。如果用户选"否"，没有定义后续行为：
- 是"使用已有文件原样记录路径"？
- 还是"忽略旧文件，从零创建新文件"？

---

## 效率

### P3 — xdebug 和 xtest 重复验证调试基础设施

**场景**：所有 init

xdebug init-steps 第 1 步："验证调试基础设施：按 infra-setup.md 检查四项能力"。xtest init-steps 第 1 步同样。

xbase init 保证 xdebug 在 xtest 之前执行，所以 xtest 执行时基础设施已存在。重复验证无害但浪费 token。

但如果用户独立运行 `/xtest`（不经过 xbase），xtest 需要自己验证。所以 xtest init-steps 不能删掉这一步。

### P7 — status 重复读取状态

**场景**：status 查看

预加载已执行 `skill-state.py read` 输出完整状态。status 命令第 1 步又执行一次 `skill-state.py read`。读了两遍。

### P10 — 顺序处理 7 个 skill 时 context 累积

**场景**：所有 init

步骤 2 顺序处理 7 个 skill，前面 skill 的探测/创建/去重的 context 会累积。到第 7 个 skill（xdecide）时，context 已包含前 6 个 skill 的所有操作历史。可能导致后面 skill 处理质量下降或耗尽 context。

这是顺序执行换取可靠性的代价，可接受。

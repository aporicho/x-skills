---
name: xbase
description: xSkills 初始化与状态管理。一键探测项目、创建所有核心文件、查看状态、重置。其他 skill 未初始化时自动调用 xbase。(xSkills init, status, reset, shared base)
user-invocable: true
allowed-tools: ["Bash", "Read", "Edit", "Write", "Glob", "Grep", "AskUserQuestion", "Task"]
argument-hint: "[init | status | reset | reinit]"
---

## 参数处理

根据 `$ARGUMENTS` 分发：

- **空** 或 **`init`** → 阶段 1：全量初始化
- **`status`** → 阶段 2：状态查看
- **`reset`** → 阶段 3：全量重置
- **`reinit`** → AskUserQuestion 确认（问题：将清空所有 skill 的初始化记录并重新初始化，核心文件不会被删除。确认？选项：确认 / 取消）→ 确认后执行 `python3 .claude/skills/xbase/scripts/skill-state.py reset-all` + 重新执行阶段 1

## 预加载状态

!`python3 .claude/skills/xbase/scripts/skill-state.py read 2>/dev/null`

---

## 阶段 1：全量初始化

### 步骤 1 — 全面探测

> 一次性收集所有 skill 所需的项目信息和核心文件状态，后续步骤不重复探测。

如 `## 项目信息` 的 `output_dir` 已有值 → 跳过 A 区，只做 B 区。

**A. 项目信息**

!`cat .claude/skills/xbase/references/detect-steps.md`

> A 区探测完成后**立即执行 write-info 写入**（不等用户确认），B 区核心文件搜索依赖 `output_dir` 已就绪。

**B. 核心文件状态**（三态判定：✅ 已就绪 / 🔄 可改造 / ❌ 需新建）

对以下各 skill 声明的核心文件，在全项目范围搜索：

!`cat .claude/skills/xdebug/references/core-files.md`

!`cat .claude/skills/xtest/references/core-files.md`

!`cat .claude/skills/xlog/references/core-files.md`

!`cat .claude/skills/xcommit/references/core-files.md`

!`cat .claude/skills/xreview/references/core-files.md`

!`cat .claude/skills/xdoc/references/core-files.md`

!`cat .claude/skills/xdecide/references/core-files.md`

**展示探测结果**，等用户确认后进入步骤 2：

```
项目信息：
| 字段 | 值 |
|------|---|
| 类型 | ... |
| 构建命令 | ... |
| ... | ... |

核心文件状态：
| Skill | 文件 | 状态 |
|-------|------|------|
| xdebug | DEBUG-LOG.md | ✅ / 🔄 ← 旧文件路径 / ❌ |
| ... | ... | ... |
```

### 步骤 2 — 创建核心文件

写入跳过去重标记：
```bash
python3 .claude/skills/xbase/scripts/skill-state.py write-info skip_dedup true
```

对每个核心文件，根据三态判定：

- **❌ 需新建** → 在 `output_dir` 下创建（格式见各 `core-files.md` 中的格式规范引用）
- **🔄 可改造** → AskUserQuestion 询问是否迁移（保留内容，套用新格式）
- **✅ 已就绪** → 跳过创建

各 skill 核心文件互不依赖，为每个 skill 用 Task 工具启动一个子 agent 并行处理，subagent_type 统一为 `general-purpose`。

每个子 agent 的 prompt 模板（替换 `<skill>`、`<三态结果>`、`<output_dir>`）：

```
你是 xbase 初始化的子 agent，负责处理 <skill> 的核心文件。

当前信息：
- 三态判定：<✅ 已就绪 / 🔄 可改造 / ❌ 需新建>
- output_dir：<路径>

执行步骤：
1. 读取 .claude/skills/<skill>/references/init-steps.md，按其指引处理核心文件
2. 三态判定已在上方给出，直接使用，不重复探测
3. 无论三态结果如何，都用 skill-state.py write 写入文件路径：
   python3 .claude/skills/xbase/scripts/skill-state.py write <skill> <key> "<路径>" [<key2> "<路径2>" ...]
4. 不执行去重（由主流程步骤 3 统一处理）
```

等待所有子 agent 完成，展示结果（✅ 创建 / ⏭️ 跳过）。

### 步骤 3 — 去重

!`cat .claude/skills/xbase/references/dedup-steps.md`

### 步骤 4 — 汇总

展示所有核心文件的创建结果和项目信息概览。

---

## 阶段 2：状态查看

1. 运行 `python3 .claude/skills/xbase/scripts/skill-state.py read`
2. 对每个 skill 检查 `initialized` 字段
3. 对每个核心文件路径用 Glob 确认文件存在
4. 展示汇总表：

```
xSkills 状态：

项目信息：
- output_dir：[值 / 未探测]
- 运行脚本：[值 / 未探测]

Skill 状态：
| Skill | 已初始化 | 核心文件 | 路径 | 文件存在 |
|-------|---------|---------|------|---------|
| xdebug | ✅ 2026-02-14 | DEBUG-LOG.md | document/DEBUG-LOG.md | ✅ |
| xtest  | ❌ | TEST-CHECKLIST.md | — | ❌ |
|        |    | TEST-ISSUES.md    | — | ❌ |
| ...    | | | | |
```

> 多核心文件的 skill（如 xtest）每个文件占一行，Skill 和已初始化列在首行填写，后续行留空。路径列展示 SKILL-STATE.md 中记录的实际路径，未记录时显示 `—`。

---

## 阶段 3：全量重置

1. AskUserQuestion 确认：
   - 问题：将清空 SKILL-STATE.md 中所有 skill 的初始化记录，下次使用各 skill 时需要重新初始化。项目中已创建的核心文件（DEBUG-LOG.md、TEST-CHECKLIST.md 等）不会被修改或删除。确认重置？
   - 选项：确认重置 / 取消

2. 确认后运行：`python3 .claude/skills/xbase/scripts/skill-state.py reset-all`

3. 展示重置后状态

---

## 其他 skill 的初始化协议

所有非 xbase 的 skill 采用**双轨初始化**：可独立完成初始化，无需调用 xbase。

**运行时路径**：
```
预加载：check-and-read <skill>
├── initialized → 跳过阶段 0，直接进入阶段 1
└── not_found   → 执行阶段 0（DCI 注入 prep-steps.md + init-steps.md，独立完成初始化）
```

**批量路径**：`/xbase init` 通过 Task 子 agent 并行调用各 skill 的 `init-steps.md`，效果相同。

各 skill 的 SKILL.md 中阶段 0 固定写法：

```markdown
### 阶段 0：探测项目

!`cat .claude/skills/xbase/references/prep-steps.md`

以下为本 skill 的特有探测步骤：

!`cat .claude/skills/<skill>/references/init-steps.md`
```

`prep-steps.md` 步骤 1 负责处理跳过逻辑（`initialized` → 跳过整个阶段 0）。

reinit 参数处理：`skill-state.py delete <skill>` 清空本 skill 状态后，预加载返回 `not_found`，正常触发阶段 0 重新初始化。

---

## SKILL-STATE.md 规范

### 位置与生命周期

`.claude/skills/xbase/SKILL-STATE.md` — 和脚本同目录，**模板预置**（所有段和字段已定义，值留空）。初始化时只需填值，不需要创建文件。

### 读写方式

```bash
# 检查 skill 是否已初始化
python3 .claude/skills/xbase/scripts/skill-state.py check <skill>
# 输出: "initialized" 或 "not_found"

# 检查并读取完整状态（预加载用）
python3 .claude/skills/xbase/scripts/skill-state.py check-and-read <skill>

# 读取完整状态
python3 .claude/skills/xbase/scripts/skill-state.py read

# 写入 skill 状态（自动添加 initialized 日期）
python3 .claude/skills/xbase/scripts/skill-state.py write <skill> <key> <value> [...]

# 写入项目信息
python3 .claude/skills/xbase/scripts/skill-state.py write-info <key> <value> [...]

# 清空 skill 段的值（保留结构）
python3 .claude/skills/xbase/scripts/skill-state.py delete <skill>

# 清空项目信息
python3 .claude/skills/xbase/scripts/skill-state.py delete-info

# 恢复模板（清空所有状态）
python3 .claude/skills/xbase/scripts/skill-state.py reset-all
```

### 关键字段

- **output_dir**（项目信息段）— 所有核心文件的统一存放目录
- **initialized**（各 skill 段）— 初始化日期，`check` 通过此字段判断是否已初始化
- **skip_dedup**（项目信息段）— 批量初始化时跳过去重的标记

### 路径格式

SKILL-STATE.md 中存储的所有文件路径统一使用**相对于项目根目录的相对路径**（如 `document/90-开发/DEBUG-LOG.md`），不使用绝对路径。阶段 2 状态查看时，Glob 以项目根目录为基准执行文件存在检查。

---

## TEST-ISSUES.md 协作协议

### 脚本命令

```bash
python3 .claude/skills/xtest/scripts/issues.py list <path>              # 列出所有问题
python3 .claude/skills/xtest/scripts/issues.py list <path> --status <状态>  # 按状态过滤
python3 .claude/skills/xtest/scripts/issues.py stats <path>             # 状态计数
python3 .claude/skills/xtest/scripts/issues.py status <path> <id> <状态>  # 更新状态
python3 .claude/skills/xtest/scripts/issues.py next-id <path>           # 下一个编号
```

### 职责分工

- **xtest**：创建 TEST-ISSUES.md、写入 🔴 条目、复测后改 ✅
- **xdebug**：选取 🔴 条目修复（改 🟡），修好后改 🟢 并写修复说明

### 文件路径

SKILL-STATE.md `## xtest` 的 `test_issues` 字段。格式见 `../xtest/references/test-issues-format.md`。

---

## 决策记录协作协议

### 脚本命令

```bash
python3 .claude/skills/xdecide/scripts/decision-log.py list <path>           # 列出决策
python3 .claude/skills/xdecide/scripts/decision-log.py next-id <path>        # 下一个编号
python3 .claude/skills/xdecide/scripts/decision-log.py search <path> <keyword>  # 搜索
```

### 职责分工

- **xdecide**：创建决策记录、引导决策过程、写入内容
- **xdebug**：修复涉及技术决策时衔接 `/xdecide`
- **xreview**：审查发现架构问题时衔接 `/xdecide`
- **xcommit**：文档完整性检查时检测未记录的决策

### 文件路径

SKILL-STATE.md `## xdecide` 的 `decision_log` 字段。格式见 `../xdecide/references/decision-format.md`。

---

## 跨 skill 衔接

所有衔接通过 AskUserQuestion 选项实现（用户主动选择），不自动跳转。

- **xdebug → xlog**：子 agent 补日志（Task prompt 传入文件路径和问题描述）
- **xtest → xdebug**：选"立即修复"（传递 TEST-ISSUES.md 条目编号如 `#003`）
- **xtest → xcommit**：选"提交变更"
- **xdebug → xdecide**：选"记录决策"（传递技术决策背景描述）
- **xdebug → xcommit**：选"提交变更"
- **xreview → xdecide**：选"记录决策"（传递架构问题描述）
- **xreview → xcommit**：选"提交变更"
- **xdecide → xcommit**：选"提交变更"
- **xdoc → xcommit**：选"提交变更"

### 上下文传递

| 衔接 | 传递内容 |
|------|----------|
| xdebug → xlog | Task prompt 中传入目标文件路径和问题描述 |
| xtest → xdebug | TEST-ISSUES.md 中 🔴 条目编号（如 `#003`） |
| xdebug → xdecide | 技术决策背景（如"修复时发现 XX 架构问题"） |
| xreview → xdecide | 架构问题描述（如"依赖方向违反：XX → YY"） |
| * → xcommit | 无需传递，xcommit 自行读取 git status/diff |

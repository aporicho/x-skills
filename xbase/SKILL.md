---
name: xbase
description: xSkills 初始化与状态管理。一键初始化所有工作流 skill 的产出物，查看状态，重置。也是共享基础（项目探测、状态规范、衔接协议）。(xSkills init, status, reset, shared base)
user-invocable: true
allowed-tools: ["Bash", "Read", "Edit", "Write", "Glob", "Grep", "AskUserQuestion", "Task"]
argument-hint: "[init | status | reset | reinit]"
---

# xbase — 初始化与状态管理 + 共享基础

> `/xbase` 是可选的便捷入口，不是必须前置步骤。未运行 `/xbase` 时，各 skill 仍可独立初始化。

---

## 参数处理

根据 `$ARGUMENTS` 分发：

- **空** 或 **`init`** → 阶段 1：全量初始化
- **`status`** → 阶段 2：状态查看
- **`reset`** → 阶段 3：全量重置
- **`reinit`** → 删除 xbase 自身状态 + 重新执行阶段 1

## 预加载状态

!`python3 .claude/skills/xbase/skill-state.py read 2>/dev/null`

---

## 阶段 1：全量初始化

### 步骤 1 — 项目探测

如 `## 项目信息` 各字段已有值则跳过此步。

按下方「项目探测标准流程」执行：扫描根目录、读 CLAUDE.md、确定项目类型/构建命令/运行脚本/日志位置。确定 output_dir（搜索 `docs/`/`doc/`/`document/` 等）。

写入项目信息：
```bash
python3 .claude/skills/xbase/skill-state.py write-info 类型 "<类型>" 构建命令 "<命令>" 运行脚本 "<脚本>" 日志位置 "<位置>" output_dir "<目录>"
```

### 步骤 2 — 并行执行各 skill 阶段 0（产出物创建）

各 skill 的产出物创建互不依赖，全部通过 Task 子 agent 并行执行。

**并行组**（同时启动）：xdebug、xtest、xlog、xcommit、xreview、xdoc、xdecide

每个子 agent 的执行方式：
1. 读取该 skill 的 `SKILL.md`
2. 执行其「阶段 0」中的产出物创建步骤（项目探测已在步骤 1 完成，会被自动跳过）
3. **不执行去重子步骤**（由步骤 3 统一处理）

等待所有子 agent 完成，逐个展示结果（✅ / ⏭️ 跳过）。

### 步骤 3 — 串行去重

产出物全部就绪后，依次执行各 skill 的去重逻辑（因为多个 skill 可能修改同一个文件如 CLAUDE.md）。

对每个有去重职责的 skill：
1. 读取该 skill 的 SKILL.md 中定义的去重规则
2. 扫描 CLAUDE.md / MEMORY.md 中对应的重复内容
3. 展示 diff 预览，等用户确认后替换为指针

### 步骤 4 — 汇总展示

展示所有产出物的创建结果和项目信息概览。

---

## 阶段 2：状态查看

1. 运行 `python3 .claude/skills/xbase/skill-state.py read` 获取当前状态
2. 对每个 skill，检查 `initialized` 字段是否有值
3. 对每个产出物路径，用 Glob 检查文件是否实际存在
4. 展示汇总表：

```
xSkills 状态：

项目信息：
- 类型：[值 / 未探测]
- 构建命令：[值 / 未探测]
- output_dir：[值 / 未探测]

Skill 状态：
| Skill | 已初始化 | 产出物 | 文件存在 |
|-------|---------|--------|---------|
| xdebug | ✅ 2026-02-14 | DEBUG-LOG.md | ✅ |
| xtest | ❌ | TEST-CHECKLIST.md | ❌ |
| ... | | | |
```

---

## 阶段 3：全量重置

1. AskUserQuestion 确认：
   - 问题：将重置所有 skill 的初始化状态。产出物文件不会被删除。确认？
   - 选项：确认重置 / 取消

2. 确认后运行：`python3 .claude/skills/xbase/skill-state.py reset-all`

3. 展示重置后状态

---

## 项目探测标准流程

所有 skill 在阶段 0 共享的探测逻辑：

1. **扫描项目根目录**，识别语言、框架、构建系统
   - 识别依据：Cargo.toml、Package.swift、package.json、*.xcodeproj 等
2. **阅读 CLAUDE.md** 了解构建命令、日志系统、调试规范、项目上下文
3. **确定项目关键信息**（后续阶段均引用，不硬编码）：
   - 构建命令
   - 项目类型（GUI 应用 / CLI 工具 / Web 服务 / 库）
   - 启动方式（直接运行二进制 / dev server / 测试命令 / 其他）
   - 日志输出位置（终端 stdout / 日志文件 / 浏览器控制台 等）
   - 停止方式（kill 进程 / Ctrl+C / 停止 dev server 等）

## SKILL-STATE.md 规范

### 位置与生命周期

`.claude/skills/xbase/SKILL-STATE.md` — 和脚本同目录，**模板预置**（所有段和字段已定义，值留空）。skill 初始化时只需填值，不需要创建文件。

### 读写方式

使用 `.claude/skills/xbase/skill-state.py` 脚本操作：

```bash
# 检查 skill 是否已初始化（看 initialized 字段是否有值）
python3 .claude/skills/xbase/skill-state.py check <skill>
# 输出: "initialized" 或 "not_found"

# 读取完整状态
python3 .claude/skills/xbase/skill-state.py read

# 写入/更新 skill 状态（自动添加 initialized 日期）
python3 .claude/skills/xbase/skill-state.py write <skill> <key> <value> [<key2> <value2> ...]

# 写入/更新项目信息
python3 .claude/skills/xbase/skill-state.py write-info <key> <value> [<key2> <value2> ...]

# 清空 skill 段的值（保留结构，用于 reinit）
python3 .claude/skills/xbase/skill-state.py delete <skill>

# 恢复模板（清空所有 skill 状态）
python3 .claude/skills/xbase/skill-state.py reset-all
```

### 模板结构

模板预置所有段，值留空。`check` 通过 `initialized` 字段是否有值来判断是否已初始化。`delete` 清空值但保留段结构。

关键字段：
- **output_dir**（项目信息段）— 所有产出物的统一存放目录，首个 skill 探测写入，后续复用

### 快速跳过逻辑

每个 skill 阶段 0 的入口：
1. 运行 `python3 .claude/skills/xbase/skill-state.py check <skill>`
2. 输出 `initialized` → 运行 `python3 .claude/skills/xbase/skill-state.py read` 获取已有信息 → 跳过探测
3. 输出 `not_found` → 执行完整探测流程 → 完成后用 `write` / `write-info` 写入

## TEST-ISSUES.md 协作协议

### 脚本命令

```bash
# 列出所有问题及状态
python3 .claude/skills/xbase/issues.py list <file_path>

# 按状态过滤列出（可用状态: 待修 / 修复中 / 已修复 / 复测通过）
python3 .claude/skills/xbase/issues.py list <file_path> --status <状态>

# 输出各状态计数统计
python3 .claude/skills/xbase/issues.py stats <file_path>

# 更新问题状态（标题行 emoji 替换）
python3 .claude/skills/xbase/issues.py status <file_path> <id> <new_status>
# new_status: 待修 / 修复中 / 已修复 / 复测通过

# 获取下一个可用编号
python3 .claude/skills/xbase/issues.py next-id <file_path>
```

### 职责分工

- **xtest 职责**：
  - 阶段 0 初始化 TEST-ISSUES.md（三态检测：不存在→创建空模板、格式不符→问迁移、已就绪→跳过）
  - 发现测试失败时写入 🔴 条目（用 `next-id` 获取编号，用 Edit 写入内容）
  - 复测通过后用 `status` 改为 ✅

- **xdebug 职责**：
  - 阶段 1 可从 TEST-ISSUES.md 选取 🔴 条目开始修复（用 `status` 改为 🟡）
  - 修复完成后用 `status` 改为 🟢，用 Edit 写入修复说明

### 文件路径

TEST-ISSUES.md 路径记录在 SKILL-STATE.md `## 项目信息` 中的 `issues_file` 字段，由 xtest 阶段 0 写入。

### 格式规范

详见 `references/test-issues-format.md`。

## 决策记录协作协议

### 脚本命令

```bash
# 列出所有决策
python3 .claude/skills/xbase/decision-log.py list <file_path>

# 获取下一个可用编号
python3 .claude/skills/xbase/decision-log.py next-id <file_path>

# 按关键词搜索决策段落
python3 .claude/skills/xbase/decision-log.py search <file_path> <keyword>
```

### 职责分工

- **xdecide 职责**：
  - 阶段 0 初始化决策记录文件（三态检测：不存在→创建、格式不符→问迁移、已就绪→跳过）
  - 引导决策过程，获取编号（`next-id`），用 Edit 写入决策内容
  - 回顾修订时用 `list` 展示、`search` 搜索

- **xdebug 职责**：
  - 阶段 6 收尾时，如涉及技术决策，可衔接 `/xdecide` 记录

- **xreview 职责**：
  - 阶段 2 审查时发现需要决策的架构问题，可衔接 `/xdecide` 记录

- **xcommit 职责**：
  - 阶段 3 文档完整性检查时，检测是否有未记录的决策

### 文件路径

决策记录路径记录在 SKILL-STATE.md `## xdecide` 中的 `decision_log` 字段，由 xdecide 阶段 0 写入。

### 格式规范

详见 `../xdecide/references/decision-format.md`。

## 跨 skill 衔接

- **xdebug → xlog**：xdebug 阶段 2 判断日志不足时，直接在 Task 工具的 prompt 参数中传入目标文件和问题描述，启动子 agent 执行 `/xlog`
- **xtest → xdebug**：xtest 阶段 4 选择"立即修复"时，从 TEST-ISSUES.md 取 🔴 条目衔接 `/xdebug`
- **xtest → xcommit**：xtest 阶段 4 选择"提交变更"时衔接 `/xcommit`
- **xdebug → xdecide**：xdebug 阶段 6 收尾时，AskUserQuestion 选项"记录决策"衔接 `/xdecide`
- **xdebug → xcommit**：xdebug 阶段 6 收尾时，AskUserQuestion 选项"提交变更"衔接 `/xcommit`
- **xreview → xdecide**：xreview 阶段 2 逐项决策时，选项"记录决策"衔接 `/xdecide`
- **xreview → xcommit**：xreview 阶段 3 收尾时，选项"提交变更"衔接 `/xcommit`
- **xdecide → xcommit**：xdecide 阶段 3 收尾时，选项"提交变更"衔接 `/xcommit`
- **xdoc → xcommit**：xdoc 阶段 4 汇报时，选项"提交变更"衔接 `/xcommit`

所有衔接通过 AskUserQuestion 选项实现（用户主动选择），不自动跳转。

### 上下文传递约定

衔接时，源 skill 应将相关上下文作为 `$ARGUMENTS` 传入目标 skill：

| 衔接 | 传递内容 |
|------|----------|
| xdebug → xlog | Task prompt 中传入目标文件路径和问题描述 |
| xtest → xdebug | TEST-ISSUES.md 中 🔴 条目的编号（如 `#003`） |
| xdebug → xdecide | 技术决策的背景描述（如"修复 Bug 时发现 XX 架构问题"） |
| xreview → xdecide | 审查发现的架构问题描述（如"依赖方向违反：XX 模块依赖了 YY"） |
| * → xcommit | 无需传递，xcommit 自行读取 git status/diff |

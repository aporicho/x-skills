---
name: xbase
description: xdebug/xtest/xlog 的共享基础。项目探测流程、SKILL-STATE.md 规范、衔接协议。不可直接调用。
user-invocable: false
---

# xbase — 共享基础

> 本 skill 不可直接调用。xdebug/xtest/xlog 引用此处的共享逻辑。

## 项目探测标准流程

三个 skill 在阶段 0 共享的探测逻辑：

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

### 位置

`.claude/skills/xbase/SKILL-STATE.md`（和脚本同目录，不依赖项目结构）。

### 读写方式

使用 `.claude/skills/xbase/skill-state.py` 脚本操作：

```bash
# 检查 skill 是否已初始化
python3 .claude/skills/xbase/skill-state.py check <skill>
# 输出: "initialized" 或 "not_found"

# 读取完整状态
python3 .claude/skills/xbase/skill-state.py read

# 写入/更新 skill 状态（自动添加 initialized 日期）
python3 .claude/skills/xbase/skill-state.py write <skill> <key> <value> [<key2> <value2> ...]

# 写入/更新项目信息
python3 .claude/skills/xbase/skill-state.py write-info <key> <value> [<key2> <value2> ...]

# 删除 skill 段（reinit 时使用）
python3 .claude/skills/xbase/skill-state.py delete <skill>
```

### 文件格式

```markdown
# SKILL STATE

> 由 xdebug/xtest/xlog 共同维护

## 项目信息

- 类型: [GUI 应用 / CLI 工具 / Web 服务 / 库]
- 构建命令: [从探测结果填入]
- 运行脚本: [scripts/run.sh 或等价物]
- 日志位置: [日志文件路径]

## xdebug

- debug_log: [DEBUG_LOG.md 路径]
- initialized: YYYY-MM-DD

## xtest

- test_checklist: [TEST-CHECKLIST.md 路径]
- initialized: YYYY-MM-DD

## xlog

- log_standard: [LOG-STANDARD.md 路径]
- log_coverage: [LOG-COVERAGE.md 路径]
- initialized: YYYY-MM-DD
```

### 快速跳过逻辑

每个 skill 阶段 0 的入口：
1. 运行 `python3 .claude/skills/xbase/skill-state.py check <skill>`
2. 输出 `initialized` → 运行 `python3 .claude/skills/xbase/skill-state.py read` 获取已有信息 → 跳过探测
3. 输出 `not_found` → 执行完整探测流程 → 完成后用 `write` / `write-info` 写入

## ISSUES.md 协作协议

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
  - 阶段 0 初始化 ISSUES.md（三态检测：不存在→创建空模板、格式不符→问迁移、已就绪→跳过）
  - 发现测试失败时写入 🔴 条目（用 `next-id` 获取编号，用 Edit 写入内容）
  - 复测通过后用 `status` 改为 ✅

- **xdebug 职责**：
  - 阶段 1 可从 ISSUES.md 选取 🔴 条目开始修复（用 `status` 改为 🟡）
  - 修复完成后用 `status` 改为 🟢，用 Edit 写入修复说明

### 文件路径

ISSUES.md 路径记录在 SKILL-STATE.md `## 项目信息` 中的 `issues_file` 字段，由 xtest 阶段 0 写入。

### 格式规范

详见 `references/issues-format.md`。

### 跨 skill 衔接

- **xdebug → xlog**：xdebug 阶段 2 判断日志不足时，直接在 Task 工具的 prompt 参数中传入目标文件和问题描述，启动子 agent 执行 `/xlog`
- **xtest → xdebug**：xtest 阶段 4 选择"立即修复"时，从 ISSUES.md 取 🔴 条目衔接 `/xdebug`

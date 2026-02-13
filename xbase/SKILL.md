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

# 管理当前任务（跨 skill 衔接用）
python3 .claude/skills/xbase/skill-state.py task set <caller> <target> <description>
python3 .claude/skills/xbase/skill-state.py task clear
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

## 跨 skill 衔接协议

### 当前任务段

skill 间传递上下文时，通过 `## 当前任务` 段通信：

```bash
# xdebug 调 xlog 前，写入目标和描述
python3 .claude/skills/xbase/skill-state.py task set xdebug "macos/Canvas/CanvasView.swift" "拖拽时位置偏移"

# xlog 子 agent 启动后，读取 SKILL-STATE.md 的 ## 当前任务 段
# 如果调用方已指定目标 → 跳过阶段 1（范围选择），直接进入阶段 2

# xtest 衔接 xdebug 时，写入失败描述
python3 .claude/skills/xbase/skill-state.py task set xtest "macos/Canvas/CanvasView.swift" "手动测试失败：拖拽偏移"

# 任务完成后清除
python3 .claude/skills/xbase/skill-state.py task clear
```

### 衔接规则

- **xdebug → xlog**：xdebug 阶段 2 判断日志不足时，用 `task set` 写入目标，启动子 agent 执行 `/xlog`
- **xtest → xdebug**：xtest 阶段 4 选择"修复失败项"时，用 `task set` 写入失败描述和分析结论，衔接 `/xdebug`（跳过阶段 1）
- **xlog 被调用时**：检查 `## 当前任务` 段，若调用方已指定目标则跳过范围选择

---
name: xlog
description: 日志补全。用户输入 /xlog 时激活，或由 /xdebug 子 agent 自动调用。建立日志规范，扫描代码补充诊断日志。
allowed-tools: ["Bash", "Read", "Edit", "Write", "Grep", "Glob", "Task"]
---

# 日志补全

## 目录

- [阶段 0：探测项目日志系统](#阶段-0探测项目日志系统)
- [阶段 1：选择范围](#阶段-1选择范围)
- [阶段 2：扫描 + 补全 + 纠正](#阶段-2扫描--补全--纠正)
- [阶段 3：汇报](#阶段-3汇报)
- [关键原则](#关键原则)

## 启动方式

- 用户输入 `/xlog` 时激活
- `/xlog reinit` — 强制重新初始化（删除 SKILL-STATE.md 中 `## xlog` 段 + 重新执行阶段 0）
- `/xdebug` 阶段 2 加日志时，子 agent 读取本 SKILL.md 执行完整 `/xlog` 流程

## 核心文件

- `LOG-STANDARD.md` — 本项目的日志规范（Logger 列表、级别用法、代码模式、消息风格）
- `LOG-COVERAGE.md` — 日志覆盖度跟踪（哪些模块扫过、状态如何）

两个文件均由 `/xlog` 创建和维护，放在项目文档目录下（根据项目结构判断位置）。

## 流程

### 阶段 0：探测项目日志系统

> **快速跳过**：运行 `python3 .claude/skills/xbase/skill-state.py check xlog`。
> - 输出 `initialized` → 运行 `python3 .claude/skills/xbase/skill-state.py read` 获取已有信息 → **跳过整个阶段 0**
> - `## 项目信息` 段已存在（其他 skill 写入）→ 直接复用，不再重复探测
> - 输出 `not_found` → 执行下方完整探测流程
>
> **衔接检查**：同时检查 `## 当前任务` 段，如果调用方已指定目标 → 记住目标，阶段 1 自动跳过。

1. 阅读 CLAUDE.md 了解日志相关规则和禁忌（如禁止 print）
2. 扫描代码找到日志工具：
   - 日志工具文件（如 `Logger.swift`、`log.rs`、`logger.ts` 等）
   - 已有的日志调用模式（`Log.xxx`、`log::xxx`、`console.xxx`、`logger.xxx` 等）
   - 可用的 Logger 实例 / 分类 / 子系统
   - 消息语言和 metadata 命名风格
3. 检测两个核心文件：
   - **LOG-STANDARD.md**：不存在 → 基于扫描结果生成（格式见 `references/log-standard-format.md`）；存在但格式不符 → 问是否迁移；已就绪 → 跳过
   - **LOG-COVERAGE.md**：同上三态检测（格式见 `references/log-coverage-format.md`）

4. **写入 SKILL-STATE.md**：按 xbase 规范，用脚本写入：
   ```bash
   python3 .claude/skills/xbase/skill-state.py write-info 类型 "<类型>" 构建命令 "<命令>"
   python3 .claude/skills/xbase/skill-state.py write xlog log_standard "<LOG-STANDARD.md 路径>" log_coverage "<LOG-COVERAGE.md 路径>"
   ```

### 阶段 1：选择范围

> 从 `/xdebug` 子 agent 调用时（`## 当前任务` 段已指定目标），跳过此阶段直接进入阶段 2。

读取 LOG-COVERAGE.md 概览，用 AskUserQuestion：

```
问题：给哪里补日志？（✅ X 模块已覆盖 / ⚠️ Y 模块有盲区 / ⏳ Z 模块未扫描）
选项：
- 未扫描的模块（优先补盲区最多的）
- 指定文件/模块（→ Other 输入路径）
- 全项目扫描
- Other → 自由输入
```

### 阶段 2：扫描 + 补全 + 纠正

**不问用户，自动完成：**

1. 读取 LOG-STANDARD.md 获取本项目的日志规则
2. 确定扫描范围：
   - **指定模块/文件** → 扫描指定范围
   - **全项目扫描且 LOG-COVERAGE.md 已有记录** → 只扫描 `git diff` 变更文件（增量），未扫描过的模块仍全量扫
   - **首次全项目扫描** → 全量扫描
3. 读取目标代码，检查两类问题：
   - **盲区**：该有日志但没有的位置 → 补充
   - **不规范**：已有日志但不符合 LOG-STANDARD.md → 纠正
     - 违反项目禁忌（如用 print 代替 Logger）
     - 级别错误（如 guard 失败用了 debug 而非 warning）
     - Logger 实例不匹配（如交互代码用了 `Log.general` 而非 `Log.interaction`）
     - 消息风格不符（如只描述现象不解释原因）
4. 构建确认编译通过
5. 编译失败 → 自己修复
6. 更新 LOG-COVERAGE.md 中对应模块的状态和扫描日期

### 阶段 3：汇报

用 AskUserQuestion：

```
问题：已处理 X 个文件：补充 Y 条 / 纠正 Z 条。[简要列出关键变更]
选项：
- 完成
- 继续下一个模块（→ 回到阶段 1）
- 看详细变更
- 有些不需要，撤回（→ Other 指定）
```

完成后清除衔接任务（如果有）：`python3 .claude/skills/xbase/skill-state.py task clear`

---

## 迁移旧格式

两个核心文件均适用，如果检测到已有文档但格式不同：
1. 用 AskUserQuestion 展示差异，询问是否迁移
2. 用户同意 → 保留原始内容，套用新格式
3. 用户拒绝 → 保持原样，后续更新时仍遵循原格式

---

## 关键原则

- **不硬编码** — 日志工具、调用模式、模块划分均从项目动态发现
- **增量优先** — 已扫描过的模块只检查 git diff 变更文件，未扫描的模块才全量扫
- **规范从代码提取** — LOG-STANDARD.md 基于扫描生成，不是凭空编写
- **日志在决策点，不在执行点** — 在分支处记录，不在每行赋值处记录
- **日志在边界处** — 模块入口、FFI 边界、异步回调入口
- **日志消息回答"为什么"** — 包含因果关系，不只是描述现象
- **遵循项目禁忌** — LOG-STANDARD.md 中的禁忌条目严格遵守
- **编译必须通过** — 加完日志后必须确认编译成功
- **两个文档保持更新** — 规范变化更新 STANDARD，扫描后更新 COVERAGE

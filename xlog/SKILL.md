---
name: xlog
description: 日志补全。用户输入 /xlog 时激活，或由 /xdebug 子 agent 自动调用。建立日志规范，扫描代码补充诊断日志。当用户要补日志、完善日志覆盖时也适用。
user-invocable: true
allowed-tools: ["Bash", "Read", "Edit", "Write", "Grep", "Glob", "AskUserQuestion"]
argument-hint: "[文件/模块路径 | reinit]"
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
- `/xdebug` 阶段 2 加日志时，子 agent 读取本 SKILL.md 执行完整 `/xlog` 流程

### 参数处理（`$ARGUMENTS`）

> **执行顺序**：无论参数如何，阶段 0 的快速跳过检查始终先执行。参数仅影响阶段 1 及之后的跳转。

- **空** → 正常走阶段 1 询问
- **`reinit`** → 删除 SKILL-STATE.md 中 `## xlog` 段（`python3 .claude/skills/xbase/skill-state.py delete xlog`）+ 重新执行阶段 0（忽略预加载的 check 结果，delete 后强制执行完整阶段 0）
- **其他文本** → 作为目标文件/模块路径，跳过阶段 1 直接进入阶段 2

## 核心文件

| 文件 | 说明 | 格式规范 |
|------|------|----------|
| `LOG-RULES.md` | 日志规范（Logger 列表、级别用法、代码模式） | `references/log-rules-format.md` |
| `LOG-COVERAGE.md` | 日志覆盖度跟踪（模块扫描状态） | `references/log-coverage-format.md` |

两个文件均由 `/xlog` 创建和维护，存放在 SKILL-STATE.md 的 `output_dir` 目录下。

## 流程

### 预加载状态
!`python3 .claude/skills/xbase/skill-state.py check-and-read xlog 2>/dev/null`

### 阶段 0：探测项目日志系统

> 按 `../xbase/references/phase0-template.md` 标准流程执行。特有探测步骤：

1. 阅读 CLAUDE.md 了解日志相关规则和禁忌（如禁止 print）
2. 扫描代码找到日志工具：
   - 日志工具文件（如 `Logger.swift`、`log.rs`、`logger.ts` 等）
   - 已有的日志调用模式（`Log.xxx`、`log::xxx`、`console.xxx`、`logger.xxx` 等）
   - 可用的 Logger 实例 / 分类 / 子系统
   - 消息语言和 metadata 命名风格
3. 检测两个核心文件：
   - **LOG-RULES.md**：不存在 → 基于扫描结果生成（格式见 `references/log-rules-format.md`）；存在但格式不符 → 问是否迁移；已就绪 → 跳过
   - **LOG-COVERAGE.md**：同上三态检测（格式见 `references/log-coverage-format.md`）
4. **写入**：`python3 .claude/skills/xbase/skill-state.py write xlog log_rules "<LOG-RULES.md 路径>" log_coverage "<LOG-COVERAGE.md 路径>"`

5. **去重子步骤**：按 `../xbase/references/dedup-protocol.md` 流程执行。xlog 去重职责：MEMORY.md 中日志规则重复部分 → 替换为指针；「禁止 print()」「日志规范详见 /logging」→ **保留**。

### 阶段 1：选择范围

> 从 `/xdebug` 子 agent 调用时，目标信息在 Task prompt 中传入，跳过此阶段直接进入阶段 2。

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

1. 读取 LOG-RULES.md 获取本项目的日志规则
2. 确定扫描范围：
   - **指定模块/文件** → 扫描指定范围
   - **全项目扫描且 LOG-COVERAGE.md 已有记录** → 只扫描 `git diff` 变更文件（增量），未扫描过的模块仍全量扫
   - **首次全项目扫描** → 全量扫描
3. 读取目标代码，检查两类问题：
   - **盲区**：该有日志但没有的位置 → 补充
   - **不规范**：已有日志但不符合 LOG-RULES.md → 纠正
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

完成后返回调用方（如果是子 agent 调用则自动结束）。

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
- **规范从代码提取** — LOG-RULES.md 基于扫描生成，不是凭空编写
- **日志在决策点，不在执行点** — 在分支处记录，不在每行赋值处记录
- **日志在边界处** — 模块入口、FFI 边界、异步回调入口
- **日志消息回答"为什么"** — 包含因果关系，不只是描述现象
- **遵循项目禁忌** — LOG-RULES.md 中的禁忌条目严格遵守
- **编译必须通过** — 加完日志后必须确认编译成功
- **两个文档保持更新** — 规范变化更新 LOG-RULES，扫描后更新 COVERAGE

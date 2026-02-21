---
name: xlog
description: 日志补全：建立日志规范，扫描代码补充诊断日志。也由 /xdebug 子 agent 自动调用。当用户要补日志、完善日志覆盖时使用。
allowed-tools: ["Bash", "Read", "Edit", "Write", "Grep", "Glob", "AskUserQuestion"]
argument-hint: "[文件/模块路径 | reinit]"
---

### 参数处理（`$ARGUMENTS`）

> **执行顺序**：无论参数如何，阶段 0 的快速跳过检查始终先执行。参数仅影响阶段 1 及之后的跳转。

- **空** → 正常走阶段 1 询问
- **`reinit`** → 删除 SKILL-STATE.md 中 `## xlog` 段（`python3 .claude/skills/xbase/scripts/skill-state.py delete xlog`）+ 重新执行阶段 0（忽略预加载的 check 结果，delete 后强制执行完整阶段 0）
- **其他文本** → 作为目标文件/模块路径，跳过阶段 1 直接进入阶段 2

### 启动方式补充

- `/xdebug` 阶段 2 加日志时，子 agent 读取本 SKILL.md 执行完整 `/xlog` 流程

### 核心文件

| 文件 | 说明 | 格式规范 |
|------|------|----------|
| `LOG-RULES.md` | 日志规范（Logger 列表、级别用法、代码模式） | `references/log-rules-format.md` |
| `LOG-COVERAGE.md` | 日志覆盖度跟踪（模块扫描状态） | `references/log-coverage-format.md` |

两个文件均由 `/xlog` 创建和维护，存放在 SKILL-STATE.md 的 `doc_dir` 目录下。

### 预加载状态
!`python3 .claude/skills/xbase/scripts/skill-state.py check-and-read xlog 2>/dev/null`

### 阶段 0：探测项目

!`python3 .claude/skills/xbase/scripts/include.py xlog protocol-prep $ARGUMENTS`

!`python3 .claude/skills/xbase/scripts/include.py xlog protocol-detection $ARGUMENTS`

!`python3 .claude/skills/xbase/scripts/include.py xlog protocol-creation $ARGUMENTS`

!`python3 .claude/skills/xbase/scripts/include.py xlog xlog/artifacts $ARGUMENTS`

!`python3 .claude/skills/xbase/scripts/include.py xlog protocol-cleanup $ARGUMENTS`

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

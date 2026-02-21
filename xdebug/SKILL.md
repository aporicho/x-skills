---
name: xdebug
description: 调试工作流：自动构建运行 App、捕获日志、引导复现、定位修复，全程选项驱动。当用户报告 Bug、请求调试、排查问题时使用。
allowed-tools: ["Bash", "Read", "Edit", "Write", "Grep", "Glob", "AskUserQuestion", "Task"]
argument-hint: "[bug描述 | #issue编号 | reinit]"
---

### 参数处理（`$ARGUMENTS`）

> **执行顺序**：无论参数如何，阶段 0 的快速跳过检查始终先执行。参数仅影响阶段 1 及之后的跳转。

- **空** → 正常走阶段 1 询问
- **`reinit`** → 删除 SKILL-STATE.md 中 `## xdebug` 段（`python3 .claude/skills/xbase/scripts/skill-state.py delete xdebug`）+ 重新执行阶段 0（忽略预加载的 check 结果，delete 后强制执行完整阶段 0）
- **以 `#` 开头**（如 `#003`）→ 从 SKILL-STATE.md `## xtest → test_issues` 读取 TEST-ISSUES.md 路径。如果字段为空（xtest 未初始化），提示用户"TEST-ISSUES.md 尚未创建，请先运行 /xtest"，回退到正常阶段 1 询问。路径有效则取对应条目作为问题描述，用 `issues.py status` 设为 🟡（修复中），跳过阶段 1 直接进入阶段 2
- **其他文本** → 作为 bug 描述，跳过阶段 1 直接进入阶段 2

### 核心文件

| 文件 | 说明 | 格式规范 |
|------|------|----------|
| `DEBUG-LOG.md` | Bug 修复日志（症状→根因→解决） | `references/debug-log-format.md` |
| `scripts/run.sh`（或等价物） | 调试运行脚本（构建/启动/停止/日志） | 阶段 0 artifacts 创建 |

### 预加载状态
!`python3 .claude/skills/xbase/scripts/skill-state.py check-and-read xdebug 2>/dev/null`

### 阶段 0：探测项目

!`cat .claude/skills/xbase/references/protocol-prep.md`

!`cat .claude/skills/xbase/references/protocol-detection.md`

!`cat .claude/skills/xdebug/references/artifacts.md`

!`cat .claude/skills/xbase/references/protocol-cleanup.md`

### 阶段 1：确认问题

用 AskUserQuestion，一步到位。**同时后台启动构建**（用户思考的时间不浪费）：

```
问题：这次调试什么？
选项：
- 从 TEST-ISSUES.md 选取（→ 先检查 SKILL-STATE.md `## xtest → test_issues` 是否有值。无值则不展示此选项。有值则用 issues.py list 展示 🔴 项，用户选一个后 issues.py status 设为 🟡（修复中））
- 探索性测试（先跑起来看日志）
- 继续上次调试（→ 从 TEST-ISSUES.md 找 🟡 条目，如无则提示无进行中的调试）
- Other → 用户直接输入 Bug 描述
```

### 阶段 2：加日志 + 构建 + 运行

**此阶段不问用户，全部自动完成：**

1. 判断现有日志是否足够覆盖问题区域（先查 LOG-COVERAGE.md，再读相关代码确认）
   - 覆盖足够 → 直接构建运行
   - 覆盖不足 → 启动子 agent（Task 工具），在 prompt 参数中直接传入目标文件和问题描述，让它读取 `.claude/skills/xlog/SKILL.md` 并按 `/xlog` 流程给目标区域补日志。子 agent 完成后主流程继续
2. 执行构建命令（从阶段 0 推导）
3. 编译失败 → 自己修复后重试，不问用户
4. 停止旧进程，后台启动项目，日志输出到阶段 0 确定的位置

### 阶段 3：引导用户操作

用 AskUserQuestion，**根据具体 Bug 给出操作步骤**，不要泛泛说"请操作"。

示例：如果 Bug 是"拖拽元素时位置偏移"，则：

```
问题：App 已启动，请按以下步骤操作：
  1. 创建一个元素
  2. 拖动它到右侧
  3. 观察位置是否偏移
  操作完选择：
选项：
- 操作完了，看日志
- 问题没复现
- App 崩溃了 / 没启动
```

### 阶段 4：分析日志

1. 读取日志：通过运行脚本的 `logs` 命令读取，**先用级别/模块过滤缩小范围**，再按需关键词搜索。不要一次读全量日志
2. 用 AskUserQuestion 展示分析结论（**App 保持运行，不要停**）：

```
问题：[简短分析摘要]。下一步？
选项：
- 已定位，修复代码
- 日志不够，加日志再来一轮（→ 回到阶段 2）
- 放弃，记录到 TODO
- Other → 用户补充信息
```

### 阶段 5：修复 + 验证

1. 停止项目（改代码前才停）
2. 修改代码修复 Bug
3. 删除临时诊断日志（保留有长期价值的日志）
4. 重新构建 + 后台启动项目（同阶段 2）
5. 用 AskUserQuestion，**同样给出具体验证步骤**：

```
问题：已修复并重启，请验证：
  [具体验证操作步骤]
选项：
- 修好了
- 没修好，继续调（→ 回到阶段 2）
- Other → 修好了但发现新问题，请描述
```

### 阶段 6：收尾

**仅在确认修好后执行，不问用户：**

1. 停止项目
2. 在 DEBUG-LOG.md 追加本次 Bug 修复记录（格式见 `references/debug-log-format.md`）
3. 如涉及技术决策且项目有决策记录文档，更新记录
4. 如果本次修复来自 TEST-ISSUES.md：
   - 用 `issues.py status` 将状态从 🟡（修复中）改为 🟢（已修复）：`python3 .claude/skills/xtest/scripts/issues.py status <path> <id> 已修复`
   - 用 Edit 工具在对应条目下写入修复说明
5. 用 AskUserQuestion：

```
问题：修复完成。下一步？
选项：
- 继续修下一个（→ 如果 TEST-ISSUES.md 还有 🔴 条目，回阶段 1）
- 提交变更（→ /xcommit，无需参数）
- 记录决策（→ /xdecide，将技术决策背景作为参数）
- Other → 用户描述新问题
```

选择"继续修下一个"且 TEST-ISSUES.md 有 🔴 条目 → 回到阶段 1。
选择"提交变更" → 衔接 `/xcommit`。
选择"记录决策" → 衔接 `/xdecide`。
用户描述了新问题 → 以新问题回到阶段 1。

---

## 关键原则

- **不硬编码** — 构建命令、路径、日志系统均从项目动态推导
- **选项优先于打字** — 能用选项就不让用户打字，Other 兜底自由输入
- **操作步骤要具体** — 根据 Bug 给出 1-2-3 步骤，不要说"请操作复现"
- **每轮只问一个问题** — 不堆叠多个问题
- **先加日志后改代码** — 禁止盲猜
- **加日志委派子 agent** — 子 agent 读 `/xlog` SKILL.md 执行，主流程不中断
- **App 不要提前停** — 分析日志时保持运行，确认要改代码了再停
- **编译问题自己解决** — 编译失败不问用户
- **没修好不更新文档** — 只在确认修复后更新

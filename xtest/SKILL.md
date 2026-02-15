---
name: xtest
description: 测试工作流。用户输入 /xtest 时激活。自动化测试 + 手动逐项验证，维护 TEST-CHECKLIST.md，失败自动衔接 /xdebug。当用户要测试、验证功能、跑测试用例时也适用。
user-invocable: true
allowed-tools: ["Bash", "Read", "Edit", "Write", "Grep", "Glob", "AskUserQuestion", "Task"]
argument-hint: "[自动化 | 手动 | reinit]"
---

# 测试工作流

## 目录

- [阶段 0：初始化](#阶段-0初始化)
- [阶段 1：选择测试类型](#阶段-1选择测试类型)
- [阶段 2a：自动化测试](#阶段-2a自动化测试)
- [阶段 2b：手动测试](#阶段-2b手动测试)
- [阶段 3：失败处理](#阶段-3失败处理)
- [阶段 4：汇总](#阶段-4汇总)
- [关键原则](#关键原则)

## 启动方式

- 用户输入 `/xtest` 时激活

### 参数处理（`$ARGUMENTS`）

> **执行顺序**：无论参数如何，阶段 0 的快速跳过检查始终先执行。参数仅影响阶段 1 及之后的跳转。

- **空** → 正常走阶段 1 询问
- **`reinit`** → 删除 SKILL-STATE.md 中 `## xtest` 段（`python3 .claude/skills/xbase/scripts/skill-state.py delete xtest`）+ 重新执行阶段 0（忽略预加载的 check 结果，delete 后强制执行完整阶段 0）
- **`自动化`** → 跳过阶段 1，直接进入阶段 2a
- **`手动`** → 跳过阶段 1，直接进入阶段 2b

## 核心文件

| 文件 | 说明 | 格式规范 |
|------|------|----------|
| `TEST-CHECKLIST.md` | 测试清单（按模块组织，记录测试结果） | `references/checklist-format.md` |
| `TEST-ISSUES.md` | Bug 队列（状态流转：🔴→🟡→🟢→✅） | `references/test-issues-format.md` |

## 流程

### 预加载状态
!`python3 .claude/skills/xbase/scripts/skill-state.py check-and-read xtest 2>/dev/null`

### 阶段 0：初始化

> 按 `../xbase/references/phase0-template.md` 标准流程执行。特有探测步骤：

1. **验证调试基础设施**（手动测试需要）：按 `../xdebug/references/infra-setup.md` 中的流程检查四项能力（构建、后台启动、日志捕获、停止），缺失的自动创建。

2. **检测 TEST-CHECKLIST.md 和 TEST-ISSUES.md**，判断状态（两个文件独立做三态检测）：
   - **TEST-CHECKLIST.md**：
     - **不存在** → 执行步骤 3-5 **全量生成**
     - **存在但格式不符**（如旧版测试清单）→ 用 AskUserQuestion 询问是否迁移（保留原始测试结果，套用新格式）
     - **存在且格式正确** → **增量更新**：只扫描 `git diff` 变更的文件，新增/删除对应测试项，跳到阶段 1
   - **TEST-ISSUES.md**：
     - **不存在** → 创建空模板（格式见 `references/test-issues-format.md`）
     - **存在但格式不符** → 用 AskUserQuestion 询问是否迁移
     - **存在且格式正确** → 跳过

3. **扫描代码**生成测试功能点（代码是唯一事实来源）：
   - **全量生成时用并行子 agent 加速**：按语言/模块拆分，每个子 agent（Task 工具）扫描一个区域，最后合并结果
     - 子 agent A：扫描自动化测试用例（`#[test]`、XCTest、jest 等）
     - 子 agent B：扫描公开接口、命令、状态管理
     - 子 agent C：扫描交互入口（UI 事件处理、快捷键绑定、手势识别等）
     - 子 agent D：扫描 FFI/API 边界
   - **增量更新时**：只扫描变更文件，不启动子 agent

4. **文档作为补充**：参考项目文档补充业务逻辑、边界条件、用户场景

5. 为每个功能点分类并生成 `TEST-CHECKLIST.md`（格式见 `references/checklist-format.md`）：
   - 🤖 自动化：已有测试代码覆盖，或可通过命令行验证
   - 👤 手动：需要启动 App 操作验证（UI 交互、视觉效果、动画等）
   - 🤝 结合：机器准备场景，人验证结果

6. **写入**：`python3 .claude/skills/xbase/scripts/skill-state.py write xtest test_checklist "<TEST-CHECKLIST.md 路径>" test_issues "<TEST-ISSUES.md 路径>"`

7. **去重子步骤**：按 `../xbase/references/dedup-protocol.md` 流程执行。xtest 当前无对应重复内容 → **跳过**。

### 阶段 1：选择测试类型

读取概览表，用 AskUserQuestion：

```
问题：测试什么？（🤖 X 项待测 / 👤 Y 项待测 / 🤝 Z 项待测）
选项：
- 自动化测试
- 手动测试（选模块逐项验证）
- Other → 指定测试编号
```

### 阶段 2a：自动化测试（🤖）

**不问用户，全自动完成：**

1. 根据项目构建系统运行测试（从 CLAUDE.md 或项目配置推导命令）
2. 解析输出，映射到 TEST-CHECKLIST.md 对应项
3. 更新状态和概览表
4. 用 AskUserQuestion 汇报：

```
问题：自动化测试完成：X 通过 / Y 失败。下一步？
选项：
- 查看失败详情
- 继续手动测试
- 进入 /xdebug 修复
- 结束
```

### 阶段 2b：手动测试（👤/🤝）

**选模块**：从 TEST-CHECKLIST.md grep ⏳ 行按 ID 前缀统计，展示选项（最多 4 个取待测最多的模块）。

**构建 + 运行**（不问用户）：
- 如果阶段 0 生成测试清单时已后台预构建 → 直接用构建结果
- 否则根据项目构建系统执行构建命令
- 后台启动项目，日志输出到阶段 0 确定的位置
- 构建失败自行修复，不问用户

**逐项测试**：grep 选定模块的 ⏳ 项，每项用 AskUserQuestion：

```
问题：[ID] 测试项名称
  验证：验证要点
  步骤：（根据具体功能给出 1-2-3 操作步骤）
选项：
- 通过
- 失败
- 跳过
- Other → 备注
```

结果在内存中暂存，**一轮结束后批量写入** TEST-CHECKLIST.md（避免逐项写文件的开销）。

### 阶段 3：失败处理

用户选"失败"时：

1. 启动后台子 agent（Task 工具，run_in_background），让它读取日志做初步分析，输出分析结论
2. **不打断测试流程**，在 TEST-CHECKLIST.md 该项标注 ❌ 并记录问题描述
3. 写入 TEST-ISSUES.md 一条 🔴 条目：
   ```bash
   # 获取下一个编号
   python3 .claude/skills/xtest/scripts/issues.py next-id <TEST-ISSUES.md 路径>
   ```
   然后用 Edit 工具在 TEST-ISSUES.md 末尾追加问题记录（格式见 `references/test-issues-format.md`），包含复现步骤、实际/预期表现
4. 继续下一个测试项

### 阶段 4：汇总

模块测试完成后：

1. 停止项目
2. 收集所有后台子 agent 的分析结论（如果有失败项）
3. 更新概览表
4. 用 AskUserQuestion：

```
问题：本轮完成：X 通过 / Y 失败 / Z 跳过。下一步？
选项：
- 立即修复（→ 从 TEST-ISSUES.md 取优先级最高的 🔴，衔接 /xdebug，传递 TEST-ISSUES.md 条目编号如 #003）
- 复测已修复项（→ 扫描 🟢 条目逐项验证，通过→✅，未通过→补充描述回 🔴）
- 提交变更（→ /xcommit）
- 继续下一个模块（→ 回阶段 1）
- Other → 稍后修复 / 结束
```

选择"立即修复"时：从 TEST-ISSUES.md 取优先级最高的 🔴 条目，衔接 `/xdebug`。

选择"复测已修复项"时：用 `issues.py list` 找到所有 🟢 条目，逐项引导用户验证。通过则用 `issues.py status` 改为 ✅，未通过则补充描述后用 `issues.py status` 改回 🔴。

选择"提交变更"时：衔接 `/xcommit`。

---

## 关键原则

- **代码是事实来源** — 扫描代码生成测试点，文档只做补充
- **增量优先** — 清单已存在时只扫描 git diff 变更文件，首次生成用并行子 agent 加速
- **批量写入** — 手动测试结果暂存内存，一轮结束后一次性更新文件
- **不硬编码** — 路径、构建命令、编号体系均从项目动态推导
- **TEST-CHECKLIST.md 是唯一状态** — 所有结果写入此文件
- **选项优先于打字** — Other 兜底自由输入
- **每次一个用例** — 不堆叠
- **操作步骤要具体** — 根据功能给出 1-2-3 步骤，不泛泛说"测试 XX 功能"
- **失败不打断测试** — 后台子 agent 分析日志，主流程继续下一项
- **失败同步写入 TEST-ISSUES.md** — 每个失败项同时写入 TEST-CHECKLIST.md（❌）和 TEST-ISSUES.md（🔴），保持双向一致
- **概览表保持更新** — 每次测试后刷新统计

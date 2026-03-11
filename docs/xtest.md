# xTest

> 测试执行 + 问题跟踪：运行自动化测试验证代码正确性，手动逐项验证使用体验，发现的问题跟踪至关闭

**制品文件**

- **TEST_CHECKLIST.md**（记录）
  按模块组织的测试清单，记录每项的验证状态。自动化测试无法覆盖的使用体验层（交互、视觉、流程）在这里逐项跟踪。
  - **创建**：xBase→xTest 阶段 0，按 template 创建空文件
  - **写入**：xTest 执行测试时按 standard 更新状态
  - **读取**：xTest
  - **更新时机**：每次手动测试执行后
- **TEST_ISSUES.md**（记录，跨 skill 共享）
  测试中发现的问题队列，状态流转 🔴→🟡→🟢→✅。
  - **创建**：xBase→xTest 阶段 0，按 template 创建空文件
  - **写入**：xTest 发现问题时按 standard 写入（🔴）；xDebug 接手时更新为🟡，修复后更新为🟢
  - **读取**：xDebug 从条目获取问题描述；xTest 回归验证后关闭（✅）
  - **更新时机**：测试发现问题 / xDebug 接手修复 / 回归验证通过
- **RUN.sh**（工具，来自 xBase）
  通过 SKILL-STATE.md 获取路径。
  - **创建**：xBase 初始化时
  - **读取**：xTest 用于构建和启动 App

**参考文件**

- **test-checklist-template.md**（模板）
  TEST_CHECKLIST.md 的结构骨架——概览表、分类表格占位。
  - **消费场景**：xBase→xTest 阶段 0 创建 TEST_CHECKLIST.md 时
- **test-checklist-standard.md**（书写标准）
  TEST_CHECKLIST.md 的书写标准——编号规则、分类判断、测试项质量标准。
  - **消费场景**：xTest 更新测试清单时
- **test-issues-template.md**（模板）
  TEST_ISSUES.md 的结构骨架——状态说明表、问题条目占位。
  - **消费场景**：xBase→xTest 阶段 0 创建 TEST_ISSUES.md 时
- **test-issues-standard.md**（书写标准）
  TEST_ISSUES.md 的书写标准——条目字段、编号规则、状态流转。
  - **消费场景**：xTest 写入问题条目时

**入口**

| 入口 | 触发方式 | 起始点 |
|------|----------|--------|
| 用户直接调用 | 用户请求测试 | D1 |
| xDebug 衔接 | Bug 修复后回归验证 | D6 |

### D1. 测试类型
- **自动化测试** → D2
- **手动测试** → D3

### D2. 自动化测试执行
探测并运行项目测试命令（代码逻辑层——函数、API、边界条件）。解析结果映射到 TEST_CHECKLIST.md 对应项，更新状态。两者互补不替代：自动化全过 ≠ 功能正常。
- **衔接手动测试** → D3
- **直接汇总** → D5

### D3. 模块选择与构建
从 TEST_CHECKLIST.md 统计各模块待测项（⏳），用户选择模块。增量优先：清单已存在时只扫描 git diff 变更文件更新测试项，避免每次全量扫描。自动构建并后台启动 App；构建失败自行修复，不打断用户。
→ D4

### D4. 逐项引导
每项给出具体操作步骤（使用体验层——交互、视觉、流程），用户逐项判定：
- **通过** → TEST_CHECKLIST.md 更新为 ✅，继续下一项
- **失败** → 同步写入 TEST_CHECKLIST.md（❌）和 TEST_ISSUES.md（🔴），后台子 agent 提取日志摘要，主流程继续下一项
- **跳过** → 继续下一项

进度持久化：通过状态标记（⏳/✅/❌）跟踪进度，跨 session 从未完成项继续。模块测试完成 → D5

### D5. 汇总与衔接
汇总模块测试结果（通过/失败/跳过）。
- **立即修复** → 衔接 xDebug D1
- **复测已修复项** → D6
- **继续下一个模块** → 回到 D3
- **提交变更** → 衔接 xCommit D1

### D6. 回归验证
两步验证：① Retest — 按原始复现步骤验证 Bug 是否修复；② Regression — 运行受影响模块的测试确认无副作用。
- **通过** → TEST_ISSUES.md 状态更新为 ✅
- **未通过** → 状态回退，衔接回 xDebug D1

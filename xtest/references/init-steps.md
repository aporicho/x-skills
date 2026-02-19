1. **验证调试基础设施**（手动测试需要）：按 `../xbase/references/infra-setup.md` 中的流程检查四项能力（构建、后台启动、日志捕获、停止），缺失的自动创建。

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

7. **去重**：按 `../xbase/references/dedup-steps.md` 流程执行。xtest 当前无对应重复内容 → **跳过**。

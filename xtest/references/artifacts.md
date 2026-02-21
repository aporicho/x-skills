## 探测

1. **运行脚本检查**（手动测试需要）：
   - 从 SKILL-STATE.md `## xbase → run_script` 读取路径
   - 有值 → 验证文件存在且可用，记录路径
   - 无值 → 标记"需先运行 /xbase 初始化"（运行脚本由 xbase 负责创建）
2. **构建命令**：从 CLAUDE.md 或构建配置推导，验证可执行。已有 → 记录；缺失 → 标记"待创建"
3. **TEST-CHECKLIST.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/TEST-CHECKLIST.md"`
   - 指纹 Grep：`"^\\| [A-Z]+-[A-Z]+-\\d{2}"`, glob=`"*.md"`（匹配 `| R-M-01` 等测试 ID）
   - 模糊名 Glob：`"**/*{test,checklist,测试清单,测试列表}*.md"`
   - 内容指纹：`^\| [A-Z]+-[A-Z]+-\d{2}`
   - 更新触发：`git diff` 有变更文件时判定为"需更新"
4. **TEST-ISSUES.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/TEST-ISSUES.md"`
   - 指纹 Grep：`"^### #\\d{3} "`, glob=`"*.md"`（匹配 `### #001 ✅` 等问题条目）
   - 模糊名 Glob：`"**/*{issues,待修复,缺陷}*.md"`
   - 内容指纹：`^### #\d{3} `

## 创建

1. **构建命令补齐**：构建命令缺失 → 根据项目类型推导
2. **TEST-CHECKLIST.md 处理**：
   - 需创建 → 执行步骤 3-5 全量生成
   - 迁移候选 → 先全量扫描生成完整测试项（同"需创建"的步骤 3-5），再将旧文件中的已通过/已失败状态映射到新测试项：展示旧项→新项的映射关系表，AskUserQuestion 确认后标记对应状态（旧文件在清理步骤处理）
   - 需更新 → 只扫描 `git diff` 变更的文件，新增/删除对应测试项
3. **扫描代码**生成测试功能点（代码是唯一事实来源）：
   - **全量生成时用并行子 agent 加速**：按语言/模块拆分，每个子 agent（Task 工具）扫描一个区域，最后合并结果
     - 子 agent A：扫描自动化测试用例（`#[test]`、XCTest、jest 等）
     - 子 agent B：扫描公开接口、命令、状态管理
     - 子 agent C：扫描交互入口（UI 事件处理、快捷键绑定、手势识别等）
     - 子 agent D：扫描 FFI/API 边界
   - **需更新时**：只扫描变更文件，不启动子 agent
4. **文档作为补充**：参考项目文档补充业务逻辑、边界条件、用户场景
5. 为每个功能点分类并生成 `TEST-CHECKLIST.md`（格式见 `.claude/skills/xtest/references/test-checklist-format.md`）：
   - 🤖 自动化：已有测试代码覆盖，或可通过命令行验证
   - 👤 手动：需要启动 App 操作验证（UI 交互、视觉效果、动画等）
   - 🤝 结合：机器准备场景，人验证结果
6. **TEST-ISSUES.md 处理**：
   - 需创建 → 创建空模板（格式见 `.claude/skills/xtest/references/test-issues-format.md`）
7. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xtest test_checklist "<TEST-CHECKLIST.md 路径>" test_issues "<TEST-ISSUES.md 路径>"`


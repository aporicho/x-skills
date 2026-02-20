## 探测

1. **调试基础设施检查**（手动测试需要）：
   - **构建命令**：从 CLAUDE.md 或构建配置推导，验证可执行。已有 → 记录；缺失 → 标记"待创建"
   - **调试运行脚本**（如 `scripts/run.sh`）：检查是否存在且支持后台启动、日志捕获、停止
     - 已有且功能完备 → 记录路径
     - 缺失或不完备 → 标记"待创建"
2. **TEST-CHECKLIST.md 三态检测**（文件名含 test、checklist、测试清单）：
   - **不存在** → 标记"需全量生成"
   - **存在但格式不符**（如旧版测试清单）→ 标记"迁移候选"
   - **存在且格式正确** → 标记"增量更新"（只扫描 `git diff` 变更文件）
3. **TEST-ISSUES.md 三态检测**（文件名含 issues、待修复、bug）：
   - **不存在** → 标记"需创建"
   - **存在但格式不符** → 标记"迁移候选"
   - **存在且格式正确** → 标记"已就绪"

## 创建

1. **补齐调试基础设施**（对探测中标记"待创建"的项）：
   - 构建命令缺失 → 根据项目类型推导
   - 运行脚本缺失 → 在 `scripts/` 下创建，需支持：`build`（构建）、`start`（后台启动 + 日志捕获到文件）、`stop`（停止进程）、`logs [filter]`（读取/过滤日志）、`status`（检查运行状态）
   - 创建后验证：运行 `build` 和 `status` 确认可用，失败则修复重试
   - 更新状态：`python3 .claude/skills/xbase/scripts/skill-state.py write-info 运行脚本 "<脚本路径>"`
2. **TEST-CHECKLIST.md 处理**：
   - 需全量生成 → 执行步骤 3-5 生成
   - 迁移候选 → 保留原始测试结果套用新格式，删除旧文件
   - 增量更新 → 只扫描 `git diff` 变更的文件，新增/删除对应测试项，跳到阶段 1
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
6. **TEST-ISSUES.md 处理**：
   - 需创建 → 创建空模板（格式见 `references/test-issues-format.md`）
   - 迁移候选 → 保留原始内容套用新格式，删除旧文件
   - 已就绪 → 跳过
7. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xtest test_checklist "<TEST-CHECKLIST.md 路径>" test_issues "<TEST-ISSUES.md 路径>"`

## 去重

读取 CLAUDE.md/MEMORY.md，对比本 skill 核心文件（路径从 SKILL-STATE.md 获取），将已被覆盖的具体规范替换为一句话指针（方法论/禁令保留原文）。有重复时逐条展示 diff，AskUserQuestion 确认后 Edit 替换。

xtest 当前无对应重复内容 → **跳过**。

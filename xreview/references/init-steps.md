1. **REVIEW-RULES.md 三态检测**：
   - **不存在** → 在 `output_dir` 下生成（执行步骤 2）
   - **存在但格式不符**（缺少 A/B/C 三维度章节）→ 用 AskUserQuestion 问是否重新生成（保留旧文件为 `.bak`）
   - **已就绪** → 跳过生成，直接步骤 3

2. **生成 REVIEW-RULES.md**（按 `references/review-rules-format.md` 格式）：

   规则来源两层：

   **a) CLAUDE.md 提取**（如存在）：
   - **禁忌类**：搜索"禁止"/"NEVER"/"不要"/"绝对不"等关键词，提取禁止事项
   - **必须类**：搜索"必须"/"MUST"/"IMPORTANT"/"CRITICAL"等关键词，提取必须遵守的规则
   - **规范类**：搜索"规范"/"风格"/"命名"/"格式"等关键词，提取编码规范
   - **架构类**：搜索"架构"/"依赖"/"层"/"模块"/"耦合"等关键词，提取架构约束

   **b) 代码扫描推导**（始终执行，不依赖 CLAUDE.md 存在）：
   - **缩进风格**：扫描源文件判断 tab/空格、缩进宽度
   - **命名风格**：扫描函数/变量名判断 camelCase/snake_case 等
   - **注释语言**：扫描注释判断中文/英文
   - **目录结构**：扫描项目目录推导架构分层
   - **错误处理模式**：扫描 guard/try-catch/Result 等模式
   - **项目特有安全检查点**：根据技术栈推导（如 FFI 项目检查内存安全、Web 项目检查 XSS 等）

   来源标记：每条规则标注来源为 `CLAUDE.md` 或 `代码扫描`，便于维护。

3. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xreview review_rules <REVIEW-RULES.md路径>`

4. **去重**：按 `../xbase/references/dedup-steps.md` 流程执行。xreview 去重职责：CLAUDE.md `## 代码规范` 段 → 替换为指向 REVIEW-RULES.md 的指针；「禁止 print()」→ **保留**（禁令）。

## 探测

1. **REVIEW_RULES.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/REVIEW_RULES.md"`
   - 指纹 Grep：`"^> 由 /xreview"`, glob=`"*.md"`
   - 模糊名 Glob：`"**/*{review,审查,代码规范}*.md"`
   - 内容指纹：`^> 由 /xreview`
2. **代码扫描**（始终执行，为生成规则收集信息）：
   - **命名风格**：扫描函数/变量名判断 camelCase/snake_case 等
   - **缩进风格**：扫描源文件判断 tab/空格、缩进宽度
   - **注释语言**：扫描注释判断中文/英文
   - **目录结构**：扫描项目目录推导架构分层和模块职责
   - **设计模式**：扫描代码识别使用的设计模式（命令、注册、委托等）
   - **错误处理模式**：扫描 guard/try-catch/Result 等模式
   - **项目特有健壮性检查点**：根据技术栈推导（如 FFI 项目检查内存安全、Web 项目检查 XSS）
   - **测试框架**：扫描测试目录识别测试框架和组织方式
   - **文档同步规则**：从 CLAUDE.md 提取变更时应同步更新哪些文档
3. **CLAUDE.md 提取**（如存在）：
   - 搜索"禁止"/"NEVER"/"不要"/"绝对不"等关键词，提取禁止事项
   - 搜索"必须"/"MUST"/"IMPORTANT"/"CRITICAL"等关键词，提取必须遵守的规则
   - 搜索"规范"/"风格"/"命名"/"格式"等关键词，提取编码规范
   - 搜索"架构"/"依赖"/"层"/"模块"/"耦合"等关键词，提取架构约束
   - 搜索"文档"/"更新"/"记录"等关键词，提取文档同步要求

## 创建

1. **REVIEW_RULES.md 处理**：
   - 需创建 → 基于探测结果生成（格式见 `.claude/skills/xreview/references/review-rules-guideline.md`），每条规则标注来源（`CLAUDE.md` 或 `代码扫描`）
2. **写入状态**：`python3 .claude/skills/xbase/scripts/state.py write xreview review_rules "<REVIEW_RULES.md 路径>"`

## 探测

1. **DOC-RULES.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/DOC-RULES.md"`
   - 指纹 Grep：`"^## 文档目录结构"`, glob=`"*.md"`
   - 模糊名 Glob：`"**/*{doc-rules,文档规范}*.md"`
   - 内容指纹：`^## 文档目录结构`
2. **项目扫描**（始终执行，为生成规则收集信息）：
   - **文档目录**：搜索 `docs/`/`doc/`/`document/`/`documentation/` 等候选，确认主文档目录及子目录结构
   - **检查脚本**：在 `scripts/` 目录下搜索 `link`/`check_link`/`structure`/`check_structure`/`index`/`generate_index`/`doc`/`verify` 等关键词的脚本，逐个确认功能
   - **编辑验证脚本**：搜索 `verify_edits` 等批量编辑验证脚本
   - **格式规范**：扫描 markdown 文件推导标题风格、代码块标注、注释语言等
   - **代码-文档映射**：扫描项目中的 DEBUG-LOG.md、DECIDE-LOG.md 等文件，推导变更类型→文档映射
3. **CLAUDE.md 提取**（如存在）：
   - 搜索"文档"/"document"/"优先"等关键词，提取文档权威性规则
   - 搜索"必须"/"更新"/"同步"等关键词，提取文档维护要求
   - 搜索"批量"/"verify"/"验证"等关键词，提取批量编辑验证要求

## 创建

1. **DOC-RULES.md 处理**：
   - 需创建 → 基于探测结果生成（格式见 `.claude/skills/xdoc/references/doc-rules-format.md`），每条规则标注来源（`CLAUDE.md` 或 `项目扫描`）
   - 迁移候选 → 基于探测结果重新生成（旧文件在清理步骤处理）
   - 已就绪 → 跳过
2. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xdoc doc_rules "<DOC-RULES.md 路径>"`

## 清理

**文件清理**：删除探测阶段标记的"废弃候选"文件（已被规范文件取代的旧文件）。有待删除文件时逐个展示，AskUserQuestion 确认后用 `rm -f` 删除（所有废弃文件合并到一条命令）。

**引用清理**：读取 CLAUDE.md，对比本 skill 核心文件（路径从 SKILL-STATE.md 获取），将已被覆盖的具体规范替换为一句话指针（方法论/禁令保留原文）。有重复时逐条展示 diff，AskUserQuestion 确认后 Edit 替换。修复过时引用（指向已不存在的 skill 或旧文件名的引用）。

xdoc 当前无对应重复内容 → 仅执行文件清理。

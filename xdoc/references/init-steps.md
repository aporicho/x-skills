## 探测

1. **DOC-RULES.md 三态检测**（文件名含 doc-rules、文档规范）：
   - **不存在** → 标记"需创建"
   - **存在但格式不符**（缺少「文档目录结构」「检查脚本」「代码-文档映射」等章节）→ 标记"迁移候选"
   - **存在且格式正确** → 标记"已就绪"
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
   - 需创建 → 基于探测结果生成（格式见 `references/doc-rules-format.md`），每条规则标注来源（`CLAUDE.md` 或 `项目扫描`）
   - 迁移候选 → 用 AskUserQuestion 问是否重新生成（保留旧文件为 `.bak`）
   - 已就绪 → 跳过
2. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xdoc doc_rules "<DOC-RULES.md 路径>"`

## 去重

按 `../xbase/references/dedup-steps.md` 流程执行。xdoc 当前无对应重复内容 → **跳过**。

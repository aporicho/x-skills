## 探测

1. **COMMIT-RULES.md 探测**（三路并行，不短路）：
   - 精确名 Glob：`"**/COMMIT-RULES.md"`
   - 指纹 Grep：`"^## 提交消息风格"`, glob=`"*.md"`
   - 模糊名 Glob：`"**/*{commit,提交规范}*.md"`
   - 内容指纹：`^## 提交消息风格`
2. **项目扫描**（始终执行，为生成规则收集信息）：
   - **Git 规范**：读取最近 10 条 commit 消息，分析消息语言、前缀格式、长度风格
   - **预检脚本**：在 `scripts/` 目录下搜索 `preflight`/`precommit`/`lint`/`check`/`verify` 等关键词的脚本
   - **文档映射**：扫描项目中的 DEBUG-LOG.md、DECIDE-LOG.md 等文件，推导变更类型→文档映射
3. **CLAUDE.md 提取**（如存在）：
   - 搜索"提交"/"commit"/"暂存"/"push"等关键词，提取暂存和提交约束
   - 搜索"DEBUG-LOG"/"决策记录"/"文档"/"必须"等关键词，提取文档完整性规则
   - 搜索"禁止"/"NEVER"/"不要"等关键词，提取提交相关禁忌

## 创建

1. **COMMIT-RULES.md 处理**：
   - 需创建 → 基于探测结果生成（格式见 `.claude/skills/xcommit/references/commit-rules-format.md`），每条规则标注来源（`CLAUDE.md` 或 `项目扫描`）
   - 迁移候选 → 基于探测结果重新生成（旧文件在清理步骤处理）
   - 已就绪 → 跳过
2. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xcommit commit_rules "<COMMIT-RULES.md 路径>"`

## 清理

**文件清理**：删除探测阶段标记的"废弃候选"文件（已被规范文件取代的旧文件）。有待删除文件时逐个展示，AskUserQuestion 确认后用 `rm -f` 删除（所有废弃文件合并到一条命令）。

**引用清理**：读取 CLAUDE.md，对比本 skill 核心文件（路径从 SKILL-STATE.md 获取），将已被覆盖的具体规范替换为一句话指针（方法论/禁令保留原文）。有重复时逐条展示 diff，AskUserQuestion 确认后 Edit 替换。修复过时引用（指向已不存在的 skill 或旧文件名的引用）。

xcommit 职责：CLAUDE.md `## Git 提交规范` 段 → 替换为指向 COMMIT-RULES.md 的指针。

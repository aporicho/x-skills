1. **COMMIT-RULES.md 三态检测**：
   - **不存在** → 在 `output_dir` 下生成（执行步骤 2）
   - **存在但格式不符**（缺少「提交消息风格」「文档完整性检查」等章节）→ 用 AskUserQuestion 问是否重新生成（保留旧文件为 `.bak`）
   - **已就绪** → 跳过生成，直接步骤 3

2. **生成 COMMIT-RULES.md**（按 `references/commit-rules-format.md` 格式）：

   规则来源两层：

   **a) CLAUDE.md 提取**（如存在）：
   - **提交规则**：搜索"提交"/"commit"/"暂存"/"push"等关键词，提取暂存和提交约束
   - **文档要求**：搜索"DEBUG-LOG"/"决策记录"/"文档"/"必须"等关键词，提取文档完整性规则
   - **禁忌类**：搜索"禁止"/"NEVER"/"不要"等关键词，提取提交相关禁忌

   **b) 项目扫描**（始终执行，不依赖 CLAUDE.md 存在）：
   - **Git 规范**：读取最近 10 条 commit 消息，分析消息语言、前缀格式、长度风格
   - **预检脚本**：在 `scripts/` 目录下搜索 `preflight`/`precommit`/`lint`/`check`/`verify` 等关键词的脚本
   - **文档映射**：扫描项目中的 DEBUG-LOG.md、DECIDE-LOG.md 等文件，推导变更类型→文档映射

   来源标记：每条规则标注来源为 `CLAUDE.md` 或 `项目扫描`，便于维护。

3. **写入状态**：`python3 .claude/skills/xbase/scripts/skill-state.py write xcommit commit_rules <COMMIT-RULES.md路径>`

4. **去重**：按 `../xbase/references/dedup-steps.md` 流程执行。xcommit 去重职责：CLAUDE.md `## Git 提交规范` 段 → 替换为指向 COMMIT-RULES.md 的指针。

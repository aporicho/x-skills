# 去重流程模板

> 各 skill 阶段 0 末尾的去重子步骤共享此模板。各 SKILL.md 引用此文件 + 补充 skill 特有的去重职责。

## 前置检查

先检查 SKILL-STATE.md `## 项目信息 → skip_dedup` 字段，值为 `true` 则跳过去重（由 `/xbase init` 统一处理）。

## 去重流程

1. **扫描**：使用 `dedup-scan.py` 扫描 CLAUDE.md 和 MEMORY.md：
   ```bash
   python3 .claude/skills/xbase/dedup-scan.py scan --skill <skill名> --claude-md <CLAUDE.md路径> [--memory-md <MEMORY.md路径>]
   ```

2. **判断**：解析 JSON 输出中的 `matches` 数组：
   - 无匹配 → 跳过，无需去重
   - 有匹配 → 继续步骤 3

3. **预览**：对每个匹配项，展示 diff 预览（当前内容 → 替换为指针文本）

4. **确认**：用 AskUserQuestion 等用户确认后执行替换（用 Edit 工具）

## 原则

- 每次对话都需要的**方法论/禁令/哲学** → 保留原文
- 已被产出物详细覆盖的**具体规范** → 替换为一句话 + 文件路径
- 修改前展示 diff 预览，等用户确认

## 各 skill 去重职责速查

| Skill | 可替换内容 | 保留内容 |
|-------|-----------|---------|
| xcommit | CLAUDE.md `## Git 提交规范` → 指向 COMMIT-RULES.md | — |
| xreview | CLAUDE.md `## 代码规范` → 指向 REVIEW-RULES.md | 「禁止 print()」（禁令） |
| xdebug | MEMORY.md 中 DEBUG_LOG 格式说明 → 指向 DEBUG-LOG.md | 「修复 Bug 必须更新」（禁令） |
| xdecide | MEMORY.md 中决策记录格式说明 → 指向 DECIDE-LOG.md | 「任何决策必须记录」（禁令） |
| xlog | MEMORY.md 中日志规则重复部分 → 指向 LOG-RULES.md | 「禁止 print()」「日志规范详见 /logging」 |
| xtest | 当前无对应重复内容 → **跳过** | — |
| xdoc | 当前无对应重复内容 → **跳过** | — |

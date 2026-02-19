检查预加载输出中 `skip_dedup` 字段，值为 `true` 则跳过去重。否则：

1. 读取 CLAUDE.md（以及 MEMORY.md，如果存在）
2. 读取本 skill 已创建的核心文件（路径从 SKILL-STATE.md 获取）
3. 对比两者内容，识别 CLAUDE.md/MEMORY.md 中已被核心文件覆盖的重复段落
4. 无重复内容 → 告知用户"未发现重复内容，无需处理"，结束去重
5. 有重复内容 → 对每处展示 diff（当前内容 → 替换为一句话指针），用 AskUserQuestion 逐条确认后用 Edit 替换

**判断标准**：方法论/禁令/哲学 → 保留原文；已被核心文件覆盖的具体规范 → 替换为一句话指针。

**批量模式**（xbase 统一初始化完成后）额外执行：

```bash
python3 .claude/skills/xbase/scripts/skill-state.py write-info skip_dedup ""
```

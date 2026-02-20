## 位置与生命周期

`.claude/skills/xbase/SKILL-STATE.md` — 和脚本同目录，**模板预置**（所有段和字段已定义，值留空）。初始化时只需填值，不需要创建文件。

## 读写方式

```bash
# 检查 skill 是否已初始化
python3 .claude/skills/xbase/scripts/skill-state.py check <skill>
# 输出: "initialized" 或 "not_found"

# 检查并读取完整状态（预加载用）
python3 .claude/skills/xbase/scripts/skill-state.py check-and-read <skill>

# 读取完整状态
python3 .claude/skills/xbase/scripts/skill-state.py read

# 写入 skill 状态（自动添加 initialized 日期）
python3 .claude/skills/xbase/scripts/skill-state.py write <skill> <key> <value> [...]

# 写入项目信息
python3 .claude/skills/xbase/scripts/skill-state.py write-info <key> <value> [...]

# 清空 skill 段的值（保留结构）
python3 .claude/skills/xbase/scripts/skill-state.py delete <skill>

# 清空项目信息
python3 .claude/skills/xbase/scripts/skill-state.py delete-info

# 恢复模板（清空所有状态）
python3 .claude/skills/xbase/scripts/skill-state.py reset-all
```

## 关键字段

- **output_dir**（项目信息段）— 所有核心文件的统一存放目录
- **initialized**（各 skill 段）— 初始化日期，`check` 通过此字段判断是否已初始化

## 路径格式

所有文件路径统一使用**相对于项目根目录的相对路径**（如 `document/90-开发/DEBUG-LOG.md`），不使用绝对路径。

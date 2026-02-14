# 决策记录格式规范

## 文件头

```markdown
# 决策记录

> 记录产品和技术决策，避免重复讨论。每条决策包含背景、选项、结论和理由。

---
```

## 条目格式

每条决策用 `## D-NNN 标题` 作为标题，后跟详细内容和分隔线：

```markdown
## D-001 决策简短标题

**背景**：为什么需要做这个决策，上下文是什么。

**选项**：
1. 方案 A — 描述及利弊
2. 方案 B — 描述及利弊
3. 方案 C — 描述及利弊

**结论**：方案 X — 选择理由。

---
```

## 字段说明

| 字段 | 必填 | 谁写 | 说明 |
|------|------|------|------|
| 编号 | ✅ | xdecide | 三位数字（D-001），通过 `decision-log.py next-id` 获取 |
| 标题 | ✅ | xdecide | 决策简短描述 |
| 背景 | ✅ | xdecide/用户 | 决策上下文、为什么需要做这个决策 |
| 选项 | 推荐 | xdecide | 编号列表，每项含描述和利弊（简单决策可省略） |
| 结论 | ✅ | 用户确认 | 最终选择及理由 |

## 快速录入格式

简单决策可省略选项，直接给出背景和结论：

```markdown
## D-002 默认 Archive 名称

**背景**：创建新 Archive 时默认名称为"我的 Archive"，"我的"多余。

**结论**：改为 `Archive`

---
```

## 修订格式

修订在原条目末尾追加，不删除原始内容：

```markdown
## D-003 某决策标题

**背景**：...

**结论**：方案 A — ...

**修订（YYYY-MM-DD）**：基于 [新发现/新需求]，调整为方案 B。理由：...

---
```

## 三态检测流程

xdecide 阶段 0 对决策记录文件做三态检测：

1. **不存在** → 使用上方文件头模板创建
2. **存在但格式不符**（无 `## D-NNN` 标题行）→ AskUserQuestion 询问是否迁移（保留原始内容，套用新格式）
3. **已就绪**（能解析出 `## D-NNN` 条目）→ 跳过

## 脚本操作

决策记录的元数据管理通过 `decision-log.py` 脚本完成，富文本内容由 skill 用 Read/Edit 工具直接操作。

```bash
# 列出所有决策
python3 .claude/skills/xbase/decision-log.py list <file_path>

# 获取下一个编号
python3 .claude/skills/xbase/decision-log.py next-id <file_path>

# 按关键词搜索
python3 .claude/skills/xbase/decision-log.py search <file_path> <keyword>
```

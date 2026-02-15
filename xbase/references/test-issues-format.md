# TEST-ISSUES.md 格式规范

## 文件头

```markdown
# 待修复问题

## 状态说明

| 状态 | 含义 | 谁负责 |
|------|------|--------|
| 🔴 待修 | 测试发现问题，等待修复 | → xdebug |
| 🟡 修复中 | xdebug 正在处理 | xdebug |
| 🟢 已修复 | 代码已改，等待复测 | → xtest |
| ✅ 复测通过 | 问题已关闭 | xtest |

---

## 问题列表
```

## 问题记录格式

每个问题用 `### #NNN <emoji> <标题>` 作为标题，后跟详细内容和分隔线：

```markdown
### #001 🔴 问题简短描述

**检查清单**：§N 章节名 — 测试项

**复现步骤**：（1-2-3 操作步骤）

**实际表现**：（观察到的行为）

**预期表现**：（正确行为）

**修复说明**：（xdebug 修复后填入，描述根因和修复方式）

---
```

## 字段说明

| 字段 | 必填 | 谁写 | 说明 |
|------|------|------|------|
| 编号 | ✅ | xtest | 三位数字，通过 `issues.py next-id` 获取 |
| 状态 emoji | ✅ | 两方 | 标题行中的 🔴🟡🟢✅，通过 `issues.py status` 更新 |
| 标题 | ✅ | xtest | 问题简短描述 |
| 检查清单 | 可选 | xtest | TEST-CHECKLIST.md 中对应的章节和测试项 |
| 复现步骤 | ✅ | xtest | 具体操作步骤 |
| 实际表现 | ✅ | xtest | 观察到的行为 |
| 预期表现 | ✅ | xtest | 正确行为 |
| 修复说明 | 修复后 | xdebug | 根因分析和修复方式 |

## 脚本操作

TEST-ISSUES.md 的状态管理通过 `issues.py` 脚本完成，富文本内容（复现步骤、修复说明等）由 skill 用 Read/Edit 工具直接操作。

```bash
# 列出所有问题
python3 .claude/skills/xtest/scripts/issues.py list <file_path>

# 更新状态
python3 .claude/skills/xtest/scripts/issues.py status <file_path> <id> <new_status>

# 获取下一个编号
python3 .claude/skills/xtest/scripts/issues.py next-id <file_path>
```

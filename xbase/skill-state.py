#!/usr/bin/env python3
"""SKILL-STATE.md 读写工具。

供 xdebug/xtest/xlog/xcommit/xreview/xdoc/xdecide skill 使用，替代多次 Read/Edit tool call。

SKILL-STATE.md 作为模板预置在同目录下，所有段和字段已定义好，skill 初始化时只需填值。

用法:
    python3 .claude/skills/xbase/skill-state.py check <skill>
    python3 .claude/skills/xbase/skill-state.py read
    python3 .claude/skills/xbase/skill-state.py write <skill> <key> <value> [<key2> <value2> ...]
    python3 .claude/skills/xbase/skill-state.py write-info <key> <value> [<key2> <value2> ...]
    python3 .claude/skills/xbase/skill-state.py delete <skill>
    python3 .claude/skills/xbase/skill-state.py reset-all
"""

import sys
import re
from datetime import date
from pathlib import Path

# 和脚本同目录，不依赖项目结构
STATE_FILE = Path(__file__).resolve().parent / "SKILL-STATE.md"

TEMPLATE = """\
# SKILL STATE

> 由 xdebug/xtest/xlog/xcommit/xreview/xdoc/xdecide 共同维护

## 项目信息

- 类型:
- 构建命令:
- 运行脚本:
- 日志位置:
- output_dir:

## xdebug

- debug_log:
- initialized:

## xtest

- test_checklist:
- initialized:

## xlog

- log_rules:
- log_coverage:
- initialized:

## xcommit

- commit_rules:
- initialized:

## xreview

- review_rules:
- initialized:

## xdoc

- doc_rules:
- initialized:

## xdecide

- decision_log:
- initialized:
"""


def read_file() -> str:
    """读取状态文件，不存在则从模板恢复。"""
    if STATE_FILE.exists():
        return STATE_FILE.read_text(encoding="utf-8")
    # 模板文件被意外删除时自动恢复
    write_file(TEMPLATE)
    return TEMPLATE


def write_file(content: str) -> None:
    """写入状态文件。"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(content, encoding="utf-8")


def find_section(content: str, heading: str) -> tuple[int, int] | None:
    """查找 ## heading 段的起止位置（不含下一个 ## 段）。

    返回 (start, end) 或 None。
    """
    pattern = rf"^## {re.escape(heading)}\s*$"
    lines = content.split("\n")
    start = None
    for i, line in enumerate(lines):
        if re.match(pattern, line):
            start = i
            continue
        if start is not None and re.match(r"^## ", line):
            return (start, i)
    if start is not None:
        return (start, len(lines))
    return None


def get_section_content(content: str, heading: str) -> str | None:
    """获取指定段的内容（不含标题行）。"""
    rng = find_section(content, heading)
    if rng is None:
        return None
    lines = content.split("\n")
    return "\n".join(lines[rng[0] + 1 : rng[1]])


def update_section_kv(content: str, heading: str, kvs: dict[str, str]) -> str:
    """更新指定段的键值对。段必须已存在（模板预置）。"""
    rng = find_section(content, heading)
    lines = content.split("\n")

    if rng is None:
        # 段不存在（异常情况，模板应预置所有段），追加新段
        new_lines = [f"\n## {heading}\n"]
        for k, v in kvs.items():
            new_lines.append(f"- {k}: {v}")
        new_lines.append("")
        return content.rstrip("\n") + "\n" + "\n".join(new_lines)

    # 更新已有段
    start, end = rng
    section_lines = lines[start + 1 : end]
    remaining_kvs = dict(kvs)

    new_section = []
    for line in section_lines:
        m = re.match(r"^- (.+?):\s*(.*)$", line)
        if m and m.group(1) in remaining_kvs:
            key = m.group(1)
            new_section.append(f"- {key}: {remaining_kvs.pop(key)}")
        else:
            new_section.append(line)

    # 追加新 key（在段末空行前）
    for k, v in remaining_kvs.items():
        insert_pos = len(new_section)
        while insert_pos > 0 and not new_section[insert_pos - 1].strip():
            insert_pos -= 1
        new_section.insert(insert_pos, f"- {k}: {v}")

    result_lines = lines[: start + 1] + new_section + lines[end:]
    return "\n".join(result_lines)


def clear_section_values(content: str, heading: str) -> str:
    """清空指定段的所有值，保留键名和段结构。"""
    rng = find_section(content, heading)
    if rng is None:
        return content

    lines = content.split("\n")
    start, end = rng
    new_section = []
    for line in lines[start + 1 : end]:
        m = re.match(r"^- (.+?):\s*(.*)$", line)
        if m:
            new_section.append(f"- {m.group(1)}:")
        else:
            new_section.append(line)

    result_lines = lines[: start + 1] + new_section + lines[end:]
    return "\n".join(result_lines)


def cmd_check(args: list[str]) -> None:
    """check <skill> — 检查 skill 是否已初始化（initialized 字段是否有值）。"""
    if len(args) != 1:
        print("用法: skill-state.py check <skill>", file=sys.stderr)
        sys.exit(1)

    skill = args[0]
    content = read_file()
    section = get_section_content(content, skill)
    if section:
        for line in section.split("\n"):
            m = re.match(r"^- initialized:\s*(.+)$", line)
            if m and m.group(1).strip():
                print("initialized")
                return
    print("not_found")


def cmd_read(_args: list[str]) -> None:
    """read — 输出完整状态文件内容。"""
    content = read_file()
    print(content)


def cmd_write(args: list[str]) -> None:
    """write <skill> <key> <value> [<key2> <value2> ...] — 写入 skill 状态。"""
    if len(args) < 3 or (len(args) - 1) % 2 != 0:
        print("用法: skill-state.py write <skill> <key> <value> [<key2> <value2> ...]", file=sys.stderr)
        sys.exit(1)

    skill = args[0]
    kvs = {}
    for i in range(1, len(args), 2):
        kvs[args[i]] = args[i + 1]

    # 自动添加 initialized
    if "initialized" not in kvs:
        kvs["initialized"] = date.today().isoformat()

    content = read_file()
    content = update_section_kv(content, skill, kvs)
    write_file(content)
    print(f"已更新 ## {skill}")


def cmd_write_info(args: list[str]) -> None:
    """write-info <key> <value> [<key2> <value2> ...] — 写入项目信息。"""
    if len(args) < 2 or len(args) % 2 != 0:
        print("用法: skill-state.py write-info <key> <value> [<key2> <value2> ...]", file=sys.stderr)
        sys.exit(1)

    kvs = {}
    for i in range(0, len(args), 2):
        kvs[args[i]] = args[i + 1]

    content = read_file()
    content = update_section_kv(content, "项目信息", kvs)
    write_file(content)
    print("已更新 ## 项目信息")


def cmd_delete(args: list[str]) -> None:
    """delete <skill> — 清空指定 skill 段的值（保留结构，用于 reinit）。"""
    if len(args) != 1:
        print("用法: skill-state.py delete <skill>", file=sys.stderr)
        sys.exit(1)

    skill = args[0]
    content = read_file()

    rng = find_section(content, skill)
    if rng is None:
        print(f"未找到 ## {skill} 段")
        return

    content = clear_section_values(content, skill)
    write_file(content)
    print(f"已重置 ## {skill}")


def cmd_reset_all(_args: list[str]) -> None:
    """reset-all — 恢复模板，清空所有 skill 状态。"""
    write_file(TEMPLATE)
    print("已恢复模板，所有 skill 状态已重置")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "check": cmd_check,
        "read": cmd_read,
        "write": cmd_write,
        "write-info": cmd_write_info,
        "delete": cmd_delete,
        "reset-all": cmd_reset_all,
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}", file=sys.stderr)
        print(f"可用命令: {', '.join(commands)}", file=sys.stderr)
        sys.exit(1)

    commands[cmd](args)


if __name__ == "__main__":
    main()

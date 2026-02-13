#!/usr/bin/env python3
"""SKILL-STATE.md 读写工具。

供 xdebug/xtest/xlog skill 使用，替代多次 Read/Edit tool call。

用法:
    python3 .claude/skills/xbase/skill-state.py check <skill>
    python3 .claude/skills/xbase/skill-state.py read
    python3 .claude/skills/xbase/skill-state.py write <skill> <key> <value> [<key2> <value2> ...]
    python3 .claude/skills/xbase/skill-state.py write-info <key> <value> [<key2> <value2> ...]
    python3 .claude/skills/xbase/skill-state.py delete <skill>
"""

import sys
import re
from datetime import date
from pathlib import Path

# 和脚本同目录，不依赖项目结构
STATE_FILE = Path(__file__).resolve().parent / "SKILL-STATE.md"

HEADER = """# SKILL STATE

> 由 xdebug/xtest/xlog 共同维护
"""


def read_file() -> str:
    """读取状态文件，不存在返回空字符串。"""
    if STATE_FILE.exists():
        return STATE_FILE.read_text(encoding="utf-8")
    return ""


def write_file(content: str) -> None:
    """写入状态文件，自动创建目录。"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(content, encoding="utf-8")


def ensure_file() -> str:
    """确保文件存在并返回内容。"""
    content = read_file()
    if not content.strip():
        content = HEADER + "\n"
        write_file(content)
    return content


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
    """更新或创建指定段的键值对。"""
    rng = find_section(content, heading)
    lines = content.split("\n")

    if rng is None:
        # 追加新段
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
        # 找到最后一个非空行的位置
        insert_pos = len(new_section)
        while insert_pos > 0 and not new_section[insert_pos - 1].strip():
            insert_pos -= 1
        new_section.insert(insert_pos, f"- {k}: {v}")

    result_lines = lines[: start + 1] + new_section + lines[end:]
    return "\n".join(result_lines)


def cmd_check(args: list[str]) -> None:
    """check <skill> — 检查 skill 是否已初始化。"""
    if len(args) != 1:
        print("用法: skill-state.py check <skill>", file=sys.stderr)
        sys.exit(1)
    skill = args[0]
    content = read_file()
    if content and find_section(content, skill) is not None:
        print("initialized")
    else:
        print("not_found")


def cmd_read(_args: list[str]) -> None:
    """read — 输出完整状态文件内容。"""
    content = read_file()
    if content:
        print(content)
    else:
        print("(文件不存在)")


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

    content = ensure_file()
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

    content = ensure_file()
    content = update_section_kv(content, "项目信息", kvs)
    write_file(content)
    print("已更新 ## 项目信息")


def cmd_delete(args: list[str]) -> None:
    """delete <skill> — 删除指定 skill 段。"""
    if len(args) != 1:
        print("用法: skill-state.py delete <skill>", file=sys.stderr)
        sys.exit(1)

    skill = args[0]
    content = read_file()
    if not content:
        print(f"文件不存在，无需删除")
        return

    rng = find_section(content, skill)
    if rng is None:
        print(f"未找到 ## {skill} 段")
        return

    lines = content.split("\n")
    # 移除整个段（包括标题和段后空行）
    end = rng[1]
    while end < len(lines) and not lines[end].strip():
        end += 1
    content = "\n".join(lines[: rng[0]] + lines[end:])
    # 清理多余空行
    content = re.sub(r"\n{3,}", "\n\n", content)
    write_file(content)
    print(f"已删除 ## {skill}")


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
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}", file=sys.stderr)
        print(f"可用命令: {', '.join(commands)}", file=sys.stderr)
        sys.exit(1)

    commands[cmd](args)


if __name__ == "__main__":
    main()

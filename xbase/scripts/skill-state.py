#!/usr/bin/env python3
"""SKILL-STATE.md 读写工具。

SKILL-STATE.md 作为模板预置在同目录下，所有段和字段已定义好，skill 初始化时只需填值。

用法:
    python3 .claude/skills/xbase/scripts/skill-state.py check <skill>
    python3 .claude/skills/xbase/scripts/skill-state.py read
    python3 .claude/skills/xbase/scripts/skill-state.py check-and-read <skill>
    python3 .claude/skills/xbase/scripts/skill-state.py write <skill> <key> <value> [<key2> <value2> ...]
    python3 .claude/skills/xbase/scripts/skill-state.py write-info <key> <value> [<key2> <value2> ...]
    python3 .claude/skills/xbase/scripts/skill-state.py delete <skill>
    python3 .claude/skills/xbase/scripts/skill-state.py delete-info
    python3 .claude/skills/xbase/scripts/skill-state.py reset-all
"""

import sys
import re
import fcntl
from datetime import date
from pathlib import Path

# xbase 根目录下的状态文件（脚本在 scripts/ 子目录，需上溯一级）
STATE_FILE = Path(__file__).resolve().parent.parent / "SKILL-STATE.md"

TEMPLATE = """\
# SKILL STATE

> 由 xbase/xdebug/xtest/xlog/xcommit/xreview/xdoc/xdecide 共同维护

## 项目信息

- doc_dir:

## xbase

- run_script:
- initialized:

## xdebug

- debug_log:
- initialized:

## xtest

- test_checklist:
- test_issues:
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
    """读取状态文件（共享锁保护），不存在则从模板恢复。"""
    if not STATE_FILE.exists():
        _write_file_raw(TEMPLATE)
        return TEMPLATE

    with open(STATE_FILE, "rb") as fd:
        fcntl.flock(fd, fcntl.LOCK_SH)
        try:
            content = fd.read().decode("utf-8")
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)

    if not content.strip():
        _write_file_raw(TEMPLATE)
        return TEMPLATE
    return content


def _write_file_raw(content: str) -> None:
    """无锁写入（仅供 read_file 恢复模板时使用）。"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(content, encoding="utf-8")


def atomic_read_modify_write(modify_fn) -> str:
    """在文件锁保护下执行 read → modify → write，返回修改后的内容。

    modify_fn: 接收当前文件内容(str)，返回修改后的内容(str)。
    """
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    # 使用 r+b 打开已有文件，或 w+b 创建新文件
    if STATE_FILE.exists():
        fd = open(STATE_FILE, "r+b")
    else:
        fd = open(STATE_FILE, "w+b")
        fd.write(TEMPLATE.encode("utf-8"))
        fd.flush()
        fd.seek(0)

    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        content = fd.read().decode("utf-8")
        if not content.strip():
            content = TEMPLATE
        new_content = modify_fn(content)
        fd.seek(0)
        fd.truncate()
        fd.write(new_content.encode("utf-8"))
        fd.flush()
        return new_content
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


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


def cmd_check_and_read(args: list[str]) -> None:
    """check-and-read <skill> — 一次调用完成 check + read，减少进程启动开销。

    输出格式：第一行为 check 结果（initialized / not_found），第二行为 ---，后续为完整状态。
    """
    if len(args) != 1:
        print("用法: skill-state.py check-and-read <skill>", file=sys.stderr)
        sys.exit(1)

    skill = args[0]
    content = read_file()

    # check 逻辑
    check_result = "not_found"
    section = get_section_content(content, skill)
    if section:
        for line in section.split("\n"):
            m = re.match(r"^- initialized:\s*(.+)$", line)
            if m and m.group(1).strip():
                check_result = "initialized"
                break

    print(check_result)
    print("---")
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

    atomic_read_modify_write(lambda c: update_section_kv(c, skill, kvs))
    print(f"已更新 ## {skill}")


def cmd_write_info(args: list[str]) -> None:
    """write-info <key> <value> [<key2> <value2> ...] — 写入项目信息。"""
    if len(args) < 2 or len(args) % 2 != 0:
        print("用法: skill-state.py write-info <key> <value> [<key2> <value2> ...]", file=sys.stderr)
        sys.exit(1)

    kvs = {}
    for i in range(0, len(args), 2):
        kvs[args[i]] = args[i + 1]

    atomic_read_modify_write(lambda c: update_section_kv(c, "项目信息", kvs))
    print("已更新 ## 项目信息")


def cmd_delete(args: list[str]) -> None:
    """delete <skill> — 清空指定 skill 段的值（保留结构，用于 reinit）。"""
    if len(args) != 1:
        print("用法: skill-state.py delete <skill>", file=sys.stderr)
        sys.exit(1)

    skill = args[0]
    # 先检查段是否存在
    content = read_file()
    rng = find_section(content, skill)
    if rng is None:
        print(f"未找到 ## {skill} 段")
        return

    atomic_read_modify_write(lambda c: clear_section_values(c, skill))
    print(f"已重置 ## {skill}")


def cmd_delete_info(_args: list[str]) -> None:
    """delete-info — 清空项目信息段的值（保留结构）。"""
    atomic_read_modify_write(lambda c: clear_section_values(c, "项目信息"))
    print("已重置 ## 项目信息")


def cmd_reset_all(_args: list[str]) -> None:
    """reset-all — 恢复模板，清空所有 skill 状态。"""
    atomic_read_modify_write(lambda _: TEMPLATE)
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
        "check-and-read": cmd_check_and_read,
        "write": cmd_write,
        "write-info": cmd_write_info,
        "delete": cmd_delete,
        "delete-info": cmd_delete_info,
        "reset-all": cmd_reset_all,
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}", file=sys.stderr)
        print(f"可用命令: {', '.join(commands)}", file=sys.stderr)
        sys.exit(1)

    commands[cmd](args)


if __name__ == "__main__":
    main()

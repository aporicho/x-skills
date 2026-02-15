#!/usr/bin/env python3
"""决策记录操作工具。

供 xdecide/xreview/xcommit skill 使用，管理决策记录文件。

用法:
    python3 .claude/skills/xbase/decision-log.py list <file_path>
    python3 .claude/skills/xbase/decision-log.py next-id <file_path>
    python3 .claude/skills/xbase/decision-log.py search <file_path> <keyword>
"""

import sys
import re
import fcntl
from pathlib import Path

# 标题行正则：## D-NNN 标题文字
TITLE_RE = re.compile(r"^## D-(\d+)\s+(.+)$")


def read_file(path: str) -> str:
    """读取文件内容。"""
    p = Path(path)
    if not p.exists():
        print(f"文件不存在: {path}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def atomic_read_modify_write(path: str, modify_fn):
    """在文件锁保护下执行 read → modify → write，返回修改后的内容。

    modify_fn: 接收当前文件内容(str)，返回修改后的内容(str)。
    """
    p = Path(path)
    if not p.exists():
        print(f"文件不存在: {path}", file=sys.stderr)
        sys.exit(1)

    with open(p, "r+b") as fd:
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            content = fd.read().decode("utf-8")
            new_content = modify_fn(content)
            fd.seek(0)
            fd.truncate()
            fd.write(new_content.encode("utf-8"))
            fd.flush()
            return new_content
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)


def parse_decisions(content: str) -> list[tuple[str, str]]:
    """解析所有决策条目，返回 [(id, title), ...]。"""
    results = []
    for line in content.split("\n"):
        m = TITLE_RE.match(line)
        if m:
            results.append((m.group(1), m.group(2)))
    return results


def get_decision_block(content: str, decision_id: str) -> str | None:
    """获取指定决策的完整段落（从 ## D-NNN 到下一个 ## 或文件末尾）。"""
    lines = content.split("\n")
    start = None
    for i, line in enumerate(lines):
        m = TITLE_RE.match(line)
        if m:
            if m.group(1) == decision_id:
                start = i
                continue
            if start is not None:
                return "\n".join(lines[start:i])
    if start is not None:
        return "\n".join(lines[start:])
    return None


def cmd_list(args: list[str]) -> None:
    """list <file_path> — 列出所有决策。"""
    if len(args) != 1:
        print("用法: decision-log.py list <file_path>", file=sys.stderr)
        sys.exit(1)

    content = read_file(args[0])
    decisions = parse_decisions(content)

    if not decisions:
        print("(无决策记录)")
        return

    for d_id, title in decisions:
        print(f"D-{d_id} {title}")


def cmd_next_id(args: list[str]) -> None:
    """next-id <file_path> — 原子获取下一个编号并写入占位行。"""
    if len(args) != 1:
        print("用法: decision-log.py next-id <file_path>", file=sys.stderr)
        sys.exit(1)

    next_id_holder = {"value": 0}

    def do_reserve(content: str) -> str:
        max_id = 0
        last_placeholder_id = 0
        for line in content.split("\n"):
            m = TITLE_RE.match(line)
            if m:
                d_id = int(m.group(1))
                max_id = max(max_id, d_id)
                if "[待填入]" in line:
                    last_placeholder_id = d_id
        if last_placeholder_id > 0:
            next_id_holder["value"] = last_placeholder_id
            return content  # 不修改，复用已有占位
        next_id = max_id + 1
        next_id_holder["value"] = next_id
        # 追加占位行
        placeholder = f"\n## D-{next_id:03d} [待填入]\n"
        return content.rstrip("\n") + placeholder

    atomic_read_modify_write(args[0], do_reserve)
    print(f"{next_id_holder['value']:03d}")


def cmd_search(args: list[str]) -> None:
    """search <file_path> <keyword> — 按关键词搜索决策段落。"""
    if len(args) != 2:
        print("用法: decision-log.py search <file_path> <keyword>", file=sys.stderr)
        sys.exit(1)

    file_path, keyword = args
    content = read_file(file_path)
    decisions = parse_decisions(content)
    keyword_lower = keyword.lower()

    found = False
    for d_id, title in decisions:
        block = get_decision_block(content, d_id)
        if block and keyword_lower in block.lower():
            print(f"D-{d_id} {title}")
            found = True

    if not found:
        print(f"(未找到包含 '{keyword}' 的决策)")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "list": cmd_list,
        "next-id": cmd_next_id,
        "search": cmd_search,
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}", file=sys.stderr)
        print(f"可用命令: {', '.join(commands)}", file=sys.stderr)
        sys.exit(1)

    commands[cmd](args)


if __name__ == "__main__":
    main()

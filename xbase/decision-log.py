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
    """next-id <file_path> — 获取下一个可用编号。"""
    if len(args) != 1:
        print("用法: decision-log.py next-id <file_path>", file=sys.stderr)
        sys.exit(1)

    content = read_file(args[0])
    max_id = 0
    for line in content.split("\n"):
        m = TITLE_RE.match(line)
        if m:
            max_id = max(max_id, int(m.group(1)))

    print(f"{max_id + 1:03d}")


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

#!/usr/bin/env python3
"""TEST-ISSUES.md 操作工具。

供 xtest/xdebug skill 使用，管理跨 session Bug 队列。

用法:
    python3 .claude/skills/xbase/issues.py list <file_path> [--status <状态>]
    python3 .claude/skills/xbase/issues.py status <file_path> <id> <new_status>
    python3 .claude/skills/xbase/issues.py next-id <file_path>
    python3 .claude/skills/xbase/issues.py stats <file_path>
"""

import sys
import re
from pathlib import Path

# 状态映射
STATUS_MAP = {
    "待修": "🔴",
    "修复中": "🟡",
    "已修复": "🟢",
    "复测通过": "✅",
}

EMOJI_TO_LABEL = {v: k for k, v in STATUS_MAP.items()}

# 标题行正则：### #001 🔴 标题文字
TITLE_RE = re.compile(r"^### #(\d+) (🔴|🟡|🟢|✅) (.+)$")


def read_file(path: str) -> str:
    """读取文件内容。"""
    p = Path(path)
    if not p.exists():
        print(f"文件不存在: {path}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def write_file(path: str, content: str) -> None:
    """写入文件内容。"""
    Path(path).write_text(content, encoding="utf-8")


def parse_issues(content: str) -> list[tuple[str, str, str]]:
    """解析所有问题条目，返回 [(id, emoji, title), ...]。"""
    results = []
    for line in content.split("\n"):
        m = TITLE_RE.match(line)
        if m:
            results.append((m.group(1), m.group(2), m.group(3)))
    return results


def cmd_list(args: list[str]) -> None:
    """list <file_path> [--status <状态>] — 列出问题及状态。"""
    if len(args) < 1:
        print("用法: issues.py list <file_path> [--status <状态>]", file=sys.stderr)
        sys.exit(1)

    file_path = args[0]
    status_filter = None

    # 解析 --status 参数
    i = 1
    while i < len(args):
        if args[i] == "--status" and i + 1 < len(args):
            status_filter = args[i + 1]
            if status_filter not in STATUS_MAP:
                print(f"未知状态: {status_filter}", file=sys.stderr)
                print(f"可用状态: {', '.join(STATUS_MAP.keys())}", file=sys.stderr)
                sys.exit(1)
            i += 2
        else:
            print(f"未知参数: {args[i]}", file=sys.stderr)
            sys.exit(1)

    content = read_file(file_path)
    issues = parse_issues(content)
    filter_emoji = STATUS_MAP.get(status_filter) if status_filter else None

    found = False
    for issue_id, emoji, title in issues:
        if filter_emoji and emoji != filter_emoji:
            continue
        label = EMOJI_TO_LABEL.get(emoji, "?")
        print(f"#{issue_id} {emoji} {label} — {title}")
        found = True

    if not found:
        print("(无匹配记录)")


def cmd_status(args: list[str]) -> None:
    """status <file_path> <id> <new_status> — 更新问题状态。"""
    if len(args) != 3:
        print("用法: issues.py status <file_path> <id> <new_status>", file=sys.stderr)
        print(f"可用状态: {', '.join(STATUS_MAP.keys())}", file=sys.stderr)
        sys.exit(1)

    file_path, issue_id, new_status = args
    issue_id = issue_id.lstrip("#").zfill(3)

    if new_status not in STATUS_MAP:
        print(f"未知状态: {new_status}", file=sys.stderr)
        print(f"可用状态: {', '.join(STATUS_MAP.keys())}", file=sys.stderr)
        sys.exit(1)

    new_emoji = STATUS_MAP[new_status]
    content = read_file(file_path)
    lines = content.split("\n")
    updated = False

    for i, line in enumerate(lines):
        m = TITLE_RE.match(line)
        if m and m.group(1) == issue_id:
            old_emoji = m.group(2)
            title = m.group(3)
            lines[i] = f"### #{issue_id} {new_emoji} {title}"
            old_label = EMOJI_TO_LABEL.get(old_emoji, "?")
            print(f"#{issue_id}: {old_emoji} {old_label} → {new_emoji} {new_status}")
            updated = True
            break

    if not updated:
        print(f"未找到问题 #{issue_id}", file=sys.stderr)
        sys.exit(1)

    write_file(file_path, "\n".join(lines))


def cmd_next_id(args: list[str]) -> None:
    """next-id <file_path> — 获取下一个可用编号。"""
    if len(args) != 1:
        print("用法: issues.py next-id <file_path>", file=sys.stderr)
        sys.exit(1)

    content = read_file(args[0])
    max_id = 0
    for line in content.split("\n"):
        m = TITLE_RE.match(line)
        if m:
            max_id = max(max_id, int(m.group(1)))

    print(f"{max_id + 1:03d}")


def cmd_stats(args: list[str]) -> None:
    """stats <file_path> — 输出各状态计数统计。"""
    if len(args) != 1:
        print("用法: issues.py stats <file_path>", file=sys.stderr)
        sys.exit(1)

    content = read_file(args[0])
    issues = parse_issues(content)

    counts = {"🔴": 0, "🟡": 0, "🟢": 0, "✅": 0}
    for _, emoji, _ in issues:
        if emoji in counts:
            counts[emoji] += 1

    total = sum(counts.values())
    print(f"🔴 {counts['🔴']} / 🟡 {counts['🟡']} / 🟢 {counts['🟢']} / ✅ {counts['✅']} / 总计 {total}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "list": cmd_list,
        "status": cmd_status,
        "next-id": cmd_next_id,
        "stats": cmd_stats,
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}", file=sys.stderr)
        print(f"可用命令: {', '.join(commands)}", file=sys.stderr)
        sys.exit(1)

    commands[cmd](args)


if __name__ == "__main__":
    main()

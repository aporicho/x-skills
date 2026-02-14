#!/usr/bin/env python3
"""去重扫描工具。

扫描 CLAUDE.md / MEMORY.md 中与各 skill 产出物重复的内容，输出 JSON 格式结果。

用法:
    python3 .claude/skills/xbase/dedup-scan.py scan --skill <name> --claude-md <path> [--memory-md <path>]
    python3 .claude/skills/xbase/dedup-scan.py scan-all --claude-md <path> [--memory-md <path>]
"""

import sys
import re
import json
from pathlib import Path

# 每个 skill 的去重规则：搜索关键词 + 保留/替换判断 + 替换指针文本
DEDUP_RULES = {
    "xcommit": {
        "targets": [
            {
                "file_key": "claude_md",
                "section_pattern": r"^## Git 提交规范",
                "keywords": ["禁止部分提交", "提交前展示", "每次提交必须包含"],
                "action": "replace",
                "pointer": "Git 提交规范详见 COMMIT-RULES.md（路径见 SKILL-STATE.md）",
            }
        ],
    },
    "xreview": {
        "targets": [
            {
                "file_key": "claude_md",
                "section_pattern": r"^## 代码规范",
                "keywords": ["4 空格缩进", "中文注释", "guard.*退出", "MARK.*组织", "避免强制解包"],
                "action": "replace",
                "pointer": "代码规范详见 REVIEW-RULES.md（路径见 SKILL-STATE.md）",
            }
        ],
    },
    "xdebug": {
        "targets": [
            {
                "file_key": "memory_md",
                "keywords": ["DEBUG_LOG", "debug-log-format", "Bug 修复日志"],
                "action": "replace",
                "pointer": "DEBUG-LOG.md 格式详见文件顶部说明",
            }
        ],
    },
    "xdecide": {
        "targets": [
            {
                "file_key": "memory_md",
                "keywords": ["决策记录格式", "DECIDE-LOG", "decision-format"],
                "action": "replace",
                "pointer": "决策记录格式详见 DECIDE-LOG.md 文件顶部",
            }
        ],
    },
    "xlog": {
        "targets": [
            {
                "file_key": "memory_md",
                "keywords": ["日志规则", "LOG-RULES", "log-rules-format"],
                "action": "replace",
                "pointer": "日志规范详见 LOG-RULES.md（路径见 SKILL-STATE.md）",
            }
        ],
    },
    "xtest": {
        "targets": [],  # 当前无对应重复内容
    },
    "xdoc": {
        "targets": [],  # 当前无对应重复内容
    },
}

# 保留列表：匹配到这些关键词的行不替换（禁令/方法论）
KEEP_PATTERNS = [
    r"禁止.*print",
    r"修复 Bug.*必须.*更新",
    r"任何.*决策.*必须.*记录",
    r"日志规范详见.*skill",
    r"先加日志.*不要盲猜",
    r"绝对不修改.*pbxproj",
    r"禁止部分提交",
    r"文档优先",
    r"先规划后执行",
]


def find_section_range(content: str, section_pattern: str) -> tuple[int, int] | None:
    """找到 ## 段的行范围 (start, end)。"""
    lines = content.split("\n")
    start = None
    for i, line in enumerate(lines):
        if re.match(section_pattern, line):
            start = i
            continue
        if start is not None and re.match(r"^## ", line):
            return (start, i)
    if start is not None:
        return (start, len(lines))
    return None


def is_keep_line(line: str) -> bool:
    """检查行是否匹配保留模式（禁令/方法论）。"""
    for pattern in KEEP_PATTERNS:
        if re.search(pattern, line):
            return True
    return False


def scan_file(content: str, targets: list, file_key: str) -> list:
    """扫描文件内容，返回匹配结果。"""
    matches = []
    lines = content.split("\n")

    for target in targets:
        if target["file_key"] != file_key:
            continue

        # 确定扫描范围
        if "section_pattern" in target:
            rng = find_section_range(content, target["section_pattern"])
            if rng is None:
                continue
            scan_start, scan_end = rng
        else:
            scan_start, scan_end = 0, len(lines)

        matched_lines = []
        for i in range(scan_start, scan_end):
            line = lines[i]
            for keyword in target["keywords"]:
                if re.search(keyword, line, re.IGNORECASE):
                    if not is_keep_line(line):
                        matched_lines.append(i + 1)  # 1-based
                    break

        if matched_lines:
            matches.append({
                "lines": matched_lines,
                "action": target["action"],
                "pointer": target.get("pointer", ""),
                "section": target.get("section_pattern", "全文"),
            })

    return matches


def cmd_scan(args: list[str]) -> None:
    """scan --skill <name> --claude-md <path> [--memory-md <path>]"""
    skill = None
    claude_md_path = None
    memory_md_path = None

    i = 0
    while i < len(args):
        if args[i] == "--skill" and i + 1 < len(args):
            skill = args[i + 1]
            i += 2
        elif args[i] == "--claude-md" and i + 1 < len(args):
            claude_md_path = args[i + 1]
            i += 2
        elif args[i] == "--memory-md" and i + 1 < len(args):
            memory_md_path = args[i + 1]
            i += 2
        else:
            print(f"未知参数: {args[i]}", file=sys.stderr)
            sys.exit(1)

    if not skill or not claude_md_path:
        print("用法: dedup-scan.py scan --skill <name> --claude-md <path> [--memory-md <path>]", file=sys.stderr)
        sys.exit(1)

    rules = DEDUP_RULES.get(skill)
    if not rules:
        print(json.dumps({"matches": []}, ensure_ascii=False))
        return

    all_matches = []

    # 扫描 CLAUDE.md
    claude_path = Path(claude_md_path)
    if claude_path.exists():
        content = claude_path.read_text(encoding="utf-8")
        for m in scan_file(content, rules["targets"], "claude_md"):
            all_matches.append({"skill": skill, "file": str(claude_path), **m})

    # 扫描 MEMORY.md
    if memory_md_path:
        memory_path = Path(memory_md_path)
        if memory_path.exists():
            content = memory_path.read_text(encoding="utf-8")
            for m in scan_file(content, rules["targets"], "memory_md"):
                all_matches.append({"skill": skill, "file": str(memory_path), **m})

    print(json.dumps({"matches": all_matches}, ensure_ascii=False, indent=2))


def cmd_scan_all(args: list[str]) -> None:
    """scan-all --claude-md <path> [--memory-md <path>]"""
    claude_md_path = None
    memory_md_path = None

    i = 0
    while i < len(args):
        if args[i] == "--claude-md" and i + 1 < len(args):
            claude_md_path = args[i + 1]
            i += 2
        elif args[i] == "--memory-md" and i + 1 < len(args):
            memory_md_path = args[i + 1]
            i += 2
        else:
            print(f"未知参数: {args[i]}", file=sys.stderr)
            sys.exit(1)

    if not claude_md_path:
        print("用法: dedup-scan.py scan-all --claude-md <path> [--memory-md <path>]", file=sys.stderr)
        sys.exit(1)

    all_matches = []

    # 读取文件内容（只读一次）
    claude_content = ""
    memory_content = ""
    claude_path = Path(claude_md_path)
    if claude_path.exists():
        claude_content = claude_path.read_text(encoding="utf-8")
    if memory_md_path:
        memory_path = Path(memory_md_path)
        if memory_path.exists():
            memory_content = memory_path.read_text(encoding="utf-8")

    for skill, rules in DEDUP_RULES.items():
        if not rules["targets"]:
            continue

        if claude_content:
            for m in scan_file(claude_content, rules["targets"], "claude_md"):
                all_matches.append({"skill": skill, "file": str(claude_path), **m})
        if memory_content:
            for m in scan_file(memory_content, rules["targets"], "memory_md"):
                all_matches.append({"skill": skill, "file": str(memory_md_path), **m})

    print(json.dumps({"matches": all_matches}, ensure_ascii=False, indent=2))


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "scan": cmd_scan,
        "scan-all": cmd_scan_all,
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}", file=sys.stderr)
        print(f"可用命令: {', '.join(commands)}", file=sys.stderr)
        sys.exit(1)

    commands[cmd](args)


if __name__ == "__main__":
    main()

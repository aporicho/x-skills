#!/usr/bin/env python3
"""Git 上下文收集工具。

一次调用收集多个 git 命令的输出，替代多次 Bash 调用。

用法:
    python3 .claude/skills/xbase/git-context.py commit-context
    python3 .claude/skills/xbase/git-context.py diff-context [--scope staged|unstaged|both]
    python3 .claude/skills/xbase/git-context.py changed-files [--scope staged|recent]
"""

import sys
import re
import json
import subprocess


def run_git(args: list[str], check: bool = False) -> str:
    """运行 git 命令，返回输出。"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=30
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""
    if check and result.returncode != 0:
        return ""
    return result.stdout.strip()


def analyze_commit_style(log_lines: list[str]) -> dict:
    """从 git log 分析提交消息风格。"""
    if not log_lines:
        return {"language": "unknown", "prefix_pattern": "none", "avg_length": 0}

    # 提取消息部分（去掉 hash）
    messages = []
    for line in log_lines:
        parts = line.split(" ", 1)
        if len(parts) == 2:
            messages.append(parts[1])

    if not messages:
        return {"language": "unknown", "prefix_pattern": "none", "avg_length": 0}

    # 检测语言
    cjk_count = sum(1 for msg in messages if re.search(r"[\u4e00-\u9fff]", msg))
    language = "zh" if cjk_count > len(messages) / 2 else "en"

    # 检测前缀模式
    prefix_patterns = {
        "conventional": re.compile(r"^(feat|fix|docs|style|refactor|test|chore|build|ci|perf)(\(.+\))?[!]?:\s"),
        "gitmoji": re.compile(r"^:[a-z_]+:\s"),
        "tag": re.compile(r"^\[.+\]\s"),
        "hash_prefix": re.compile(r"^#\d+\s"),
    }

    prefix_counts = {k: 0 for k in prefix_patterns}
    for msg in messages:
        for name, pattern in prefix_patterns.items():
            if pattern.match(msg):
                prefix_counts[name] += 1

    max_prefix = max(prefix_counts, key=prefix_counts.get)
    prefix_pattern = max_prefix if prefix_counts[max_prefix] > len(messages) / 3 else "none"

    # 平均长度
    avg_length = sum(len(msg) for msg in messages) // len(messages) if messages else 0

    return {
        "language": language,
        "prefix_pattern": prefix_pattern,
        "avg_length": avg_length,
    }


def cmd_commit_context(args: list[str]) -> None:
    """commit-context — xcommit 全流程所需上下文。"""
    # 并行收集所有 git 信息
    status = run_git(["status", "--short"])
    diff_stat = run_git(["diff", "--stat"])
    cached_diff = run_git(["diff", "--cached"])
    cached_stat = run_git(["diff", "--cached", "--stat"])
    recent_log_raw = run_git(["log", "--oneline", "-10"])
    recent_log = recent_log_raw.split("\n") if recent_log_raw else []

    # 分析提交风格
    commit_style = analyze_commit_style(recent_log)

    result = {
        "status": status,
        "diff_stat": diff_stat,
        "cached_diff": cached_diff,
        "cached_stat": cached_stat,
        "recent_log": recent_log,
        "commit_style": commit_style,
        "has_staged": bool(cached_diff),
        "has_unstaged": bool(diff_stat),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_diff_context(args: list[str]) -> None:
    """diff-context — xreview 所需差异上下文。"""
    scope = "both"
    i = 0
    while i < len(args):
        if args[i] == "--scope" and i + 1 < len(args):
            scope = args[i + 1]
            i += 2
        else:
            i += 1

    result = {}

    if scope in ("staged", "both"):
        result["staged_diff"] = run_git(["diff", "--cached"])
        result["staged_stat"] = run_git(["diff", "--cached", "--stat"])

    if scope in ("unstaged", "both"):
        result["unstaged_diff"] = run_git(["diff"])
        result["unstaged_stat"] = run_git(["diff", "--stat"])

    result["status"] = run_git(["status", "--short"])

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_changed_files(args: list[str]) -> None:
    """changed-files — xtest 增量测试所需变更文件列表。"""
    scope = "staged"
    i = 0
    while i < len(args):
        if args[i] == "--scope" and i + 1 < len(args):
            scope = args[i + 1]
            i += 2
        else:
            i += 1

    if scope == "staged":
        files_raw = run_git(["diff", "--cached", "--name-only"])
    elif scope == "recent":
        files_raw = run_git(["diff", "HEAD~5..HEAD", "--name-only"])
    else:
        files_raw = run_git(["diff", "--name-only"])

    files = [f for f in files_raw.split("\n") if f.strip()] if files_raw else []

    print(json.dumps({"scope": scope, "files": files}, ensure_ascii=False, indent=2))


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "commit-context": cmd_commit_context,
        "diff-context": cmd_diff_context,
        "changed-files": cmd_changed_files,
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}", file=sys.stderr)
        print(f"可用命令: {', '.join(commands)}", file=sys.stderr)
        sys.exit(1)

    commands[cmd](args)


if __name__ == "__main__":
    main()

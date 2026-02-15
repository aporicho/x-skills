#!/usr/bin/env python3
"""产出物三态检测 + 骨架创建工具。

动态读取 references/*-format.md 提取格式标记，新增 skill 只需放格式文件即可自动适配。

用法:
    python3 .claude/skills/xbase/artifact-check.py check <artifact_name> <expected_path>
    python3 .claude/skills/xbase/artifact-check.py create <artifact_name> <target_path>
    python3 .claude/skills/xbase/artifact-check.py batch-check <output_dir>
"""

import sys
import re
import json
from pathlib import Path
from datetime import date

SKILLS_DIR = Path(__file__).resolve().parent.parent


def discover_formats() -> dict:
    """扫描所有 references/*-format.md，建立 artifact → format 映射。

    返回 {artifact_name: {filename, markers: [str], format_path: str}}
    """
    formats = {}
    for format_file in SKILLS_DIR.rglob("references/*-format.md"):
        content = format_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        # 提取 H1 标题作为 artifact name
        h1 = None
        for line in lines:
            m = re.match(r"^# (.+)$", line)
            if m:
                h1 = m.group(1).strip()
                break
        if not h1:
            continue

        # 从 H1 提取产出物文件名（如 "COMMIT-RULES.md 规范" → "COMMIT-RULES.md"）
        filename_match = re.match(r"^([A-Z][-A-Z0-9]+\.md)", h1)
        if not filename_match:
            # fallback: 从 format 文件名推导（如 commit-rules-format.md → COMMIT-RULES.md）
            basename = format_file.name
            name_part = basename.replace("-format.md", "")
            filename = name_part.upper().replace("_", "-") + ".md"
        else:
            filename = filename_match.group(1)

        # 提取必需段落标题（## 级别）作为格式标记
        markers = []
        for line in lines:
            m = re.match(r"^## (.+)$", line)
            if m:
                markers.append(m.group(1).strip())

        # artifact_name 用小写无后缀形式（如 commit-rules）
        artifact_name = filename.replace(".md", "").lower()

        formats[artifact_name] = {
            "filename": filename,
            "markers": markers,
            "format_path": str(format_file),
        }

    return formats


def cmd_check(args: list[str]) -> None:
    """check <artifact_name> <expected_path> → ready / format_mismatch / not_found"""
    if len(args) != 2:
        print("用法: artifact-check.py check <artifact_name> <expected_path>", file=sys.stderr)
        sys.exit(1)

    artifact_name, expected_path = args
    p = Path(expected_path)

    if not p.exists():
        print("not_found")
        return

    formats = discover_formats()
    fmt = formats.get(artifact_name.lower())
    if not fmt:
        # 无格式定义，文件存在即视为就绪
        print("ready")
        return

    content = p.read_text(encoding="utf-8")
    # 检查必需段落标题是否存在
    missing = []
    for marker in fmt["markers"]:
        pattern = rf"^##\s+{re.escape(marker)}"
        if not re.search(pattern, content, re.MULTILINE):
            missing.append(marker)

    if missing:
        print("format_mismatch")
        # 在 stderr 输出缺失细节
        print(f"缺失段落: {', '.join(missing)}", file=sys.stderr)
    else:
        print("ready")


def cmd_create(args: list[str]) -> None:
    """create <artifact_name> <target_path> → 从格式文件提取骨架并创建"""
    if len(args) != 2:
        print("用法: artifact-check.py create <artifact_name> <target_path>", file=sys.stderr)
        sys.exit(1)

    artifact_name, target_path = args
    p = Path(target_path)

    formats = discover_formats()
    fmt = formats.get(artifact_name.lower())
    if not fmt:
        print(f"未找到 {artifact_name} 的格式定义", file=sys.stderr)
        sys.exit(1)

    # 读取格式文件，提取骨架
    format_content = Path(fmt["format_path"]).read_text(encoding="utf-8")

    # 提取标题和段落标题构建骨架
    skeleton_lines = [
        f"# {fmt['filename'].replace('.md', '')}",
        "",
        f"> 由 xSkills 创建于 {date.today().isoformat()}",
        "",
    ]

    for marker in fmt["markers"]:
        skeleton_lines.append(f"## {marker}")
        skeleton_lines.append("")
        skeleton_lines.append("<!-- 待填入 -->")
        skeleton_lines.append("")

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(skeleton_lines), encoding="utf-8")
    print(f"已创建: {target_path}")


def cmd_batch_check(args: list[str]) -> None:
    """batch-check <output_dir> → JSON 汇总所有已知产出物状态"""
    if len(args) != 1:
        print("用法: artifact-check.py batch-check <output_dir>", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args[0])
    formats = discover_formats()
    results = {}

    for artifact_name, fmt in formats.items():
        expected_path = output_dir / fmt["filename"]
        if not expected_path.exists():
            results[artifact_name] = {
                "status": "not_found",
                "path": str(expected_path),
                "filename": fmt["filename"],
            }
            continue

        content = expected_path.read_text(encoding="utf-8")
        missing = []
        for marker in fmt["markers"]:
            pattern = rf"^##\s+{re.escape(marker)}"
            if not re.search(pattern, content, re.MULTILINE):
                missing.append(marker)

        results[artifact_name] = {
            "status": "ready" if not missing else "format_mismatch",
            "path": str(expected_path),
            "filename": fmt["filename"],
            "missing_markers": missing if missing else None,
        }

    print(json.dumps(results, ensure_ascii=False, indent=2))


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "check": cmd_check,
        "create": cmd_create,
        "batch-check": cmd_batch_check,
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}", file=sys.stderr)
        print(f"可用命令: {', '.join(commands)}", file=sys.stderr)
        sys.exit(1)

    commands[cmd](args)


if __name__ == "__main__":
    main()

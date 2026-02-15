#!/usr/bin/env python3
"""产出物骨架创建工具。

动态读取 references/*-format.md 提取格式结构，从模板生成骨架文件。
新增 skill 只需放格式文件即可自动适配。

用法:
    python3 .claude/skills/xbase/scripts/artifact-create.py <artifact_name> <target_path>
    python3 .claude/skills/xbase/scripts/artifact-create.py --list
"""

import sys
import re
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


def cmd_create(artifact_name: str, target_path: str) -> None:
    """从格式文件提取骨架并创建产出物文件。"""
    p = Path(target_path)

    formats = discover_formats()
    fmt = formats.get(artifact_name.lower())
    if not fmt:
        print(f"未找到 {artifact_name} 的格式定义", file=sys.stderr)
        print(f"可用: {', '.join(sorted(formats))}", file=sys.stderr)
        sys.exit(1)

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


def cmd_list() -> None:
    """列出所有可创建的产出物。"""
    formats = discover_formats()
    for name, fmt in sorted(formats.items()):
        print(f"  {name:20s} → {fmt['filename']}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    if sys.argv[1] == "--list":
        cmd_list()
    elif len(sys.argv) == 3:
        cmd_create(sys.argv[1], sys.argv[2])
    else:
        print(__doc__.strip())
        sys.exit(1)


if __name__ == "__main__":
    main()

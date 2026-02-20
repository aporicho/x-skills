#!/usr/bin/env python3
"""从 init-steps.md 按节名提取内容。

用法: python3 extract-section.py <skill> <section> [<section2> ...]
示例: python3 extract-section.py xdebug 探测
      python3 extract-section.py xdebug 创建 去重

通过 `## 标题` 行定位节边界，不输出标题行本身。
多节时按参数顺序输出，节间空行分隔。
文件/节不存在时 stderr 报错，exit 1。
"""

import sys
from pathlib import Path


def extract_sections(filepath: Path, section_names: list[str]) -> str:
    """从文件中提取指定节的内容。"""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    # 解析所有 ## 节：{节名: 内容}
    sections: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            # 保存上一节
            if current_name is not None:
                sections[current_name] = "\n".join(current_lines).strip()
            current_name = line[3:].strip()
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)

    # 保存最后一节
    if current_name is not None:
        sections[current_name] = "\n".join(current_lines).strip()

    # 按参数顺序提取
    results: list[str] = []
    for name in section_names:
        if name not in sections:
            print(f"错误：节 '## {name}' 在 {filepath} 中不存在", file=sys.stderr)
            sys.exit(1)
        results.append(sections[name])

    return "\n\n".join(results)


def main() -> None:
    if len(sys.argv) < 3:
        print("用法: python3 extract-section.py <skill> <section> [<section2> ...]", file=sys.stderr)
        sys.exit(1)

    skill = sys.argv[1]
    section_names = sys.argv[2:]

    # 定位 init-steps.md
    script_dir = Path(__file__).resolve().parent
    skills_dir = script_dir.parent.parent  # .claude/skills/
    filepath = skills_dir / skill / "references" / "init-steps.md"

    if not filepath.exists():
        print(f"错误：文件不存在 {filepath}", file=sys.stderr)
        sys.exit(1)

    output = extract_sections(filepath, section_names)
    print(output)


if __name__ == "__main__":
    main()

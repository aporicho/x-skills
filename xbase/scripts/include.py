#!/usr/bin/env python3
"""条件性内容注入工具（替代 !cat + extract-section.py）。

根据 SKILL-STATE.md 状态和用户参数决定是否输出内容。
已初始化且非 reinit 时输出空，减少 prompt 膨胀。

用法:
    python3 include.py <gate_skill> <ref> [user_args...]

ref 解析规则（skills_dir = 脚本上两级目录）：

| ref 格式           | 解析                                    | 示例              |
|-------------------|-----------------------------------------|-------------------|
| 名称（无 / 无 :）   | xbase/references/{名称}.md              | protocol-prep     |
| skill/文件         | {skill}/references/{文件}.md            | xdebug/artifacts  |
| skill:段名         | {skill}/references/artifacts.md → ## 段名 | xdebug:探测        |

示例:
    python3 include.py xdebug protocol-prep
    python3 include.py xdebug protocol-prep reinit
    python3 include.py xbase xdebug:探测
    python3 include.py xbase xdebug:探测 status
"""

import sys
import re
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent.parent  # .claude/skills/
STATE_FILE = SKILLS_DIR / "xbase" / "SKILL-STATE.md"


def is_initialized(skill: str) -> bool:
    """检查 skill 是否已初始化。"""
    if not STATE_FILE.exists():
        return False
    content = STATE_FILE.read_text(encoding="utf-8")
    in_section = False
    for line in content.split("\n"):
        if re.match(rf"^## {re.escape(skill)}\s*$", line):
            in_section = True
            continue
        if in_section and re.match(r"^## ", line):
            break
        if in_section:
            m = re.match(r"^- initialized:\s*(.+)$", line)
            if m and m.group(1).strip():
                return True
    return False


def should_skip(skill: str, user_args: list[str]) -> bool:
    """判断是否跳过注入。"""
    if skill == "xbase":
        return bool(user_args) and user_args[0] == "status"
    return is_initialized(skill) and "reinit" not in user_args


def extract_section(filepath: Path, section_name: str) -> str:
    """从文件中提取指定 ## 节的内容（不含标题行）。"""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    current_name: str | None = None
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_name == section_name:
                return "\n".join(current_lines).strip()
            current_name = line[3:].strip()
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)

    # 最后一节
    if current_name == section_name:
        return "\n".join(current_lines).strip()

    print(f"错误：段 '## {section_name}' 在 {filepath} 中不存在", file=sys.stderr)
    sys.exit(1)


def resolve_ref(ref: str) -> tuple[Path, str | None]:
    """解析 ref 为 (文件路径, 段名或None)。"""
    if ":" in ref:
        # skill:段名 → {skill}/references/artifacts.md + 段名
        skill, section = ref.split(":", 1)
        return SKILLS_DIR / skill / "references" / "artifacts.md", section
    elif "/" in ref:
        # skill/文件 → {skill}/references/{文件}.md
        skill, filename = ref.split("/", 1)
        if not filename.endswith(".md"):
            filename += ".md"
        return SKILLS_DIR / skill / "references" / filename, None
    else:
        # 名称 → xbase/references/{名称}.md
        return SKILLS_DIR / "xbase" / "references" / f"{ref}.md", None


def main() -> None:
    if len(sys.argv) < 3:
        print("用法: include.py <gate_skill> <ref> [user_args...]", file=sys.stderr)
        sys.exit(1)

    gate_skill = sys.argv[1]
    ref = sys.argv[2]
    user_args = sys.argv[3:]

    if should_skip(gate_skill, user_args):
        return

    filepath, section = resolve_ref(ref)

    if not filepath.exists():
        print(f"文件不存在: {filepath}", file=sys.stderr)
        sys.exit(1)

    if section:
        print(extract_section(filepath, section))
    else:
        print(filepath.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()

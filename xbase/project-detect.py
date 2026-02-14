#!/usr/bin/env python3
"""项目探测工具。

扫描项目根目录，识别项目类型、构建命令、文档目录等关键信息。

用法:
    python3 .claude/skills/xbase/project-detect.py detect [--project-root <path>]
    python3 .claude/skills/xbase/project-detect.py detect-and-write [--project-root <path>]
"""

import sys
import re
import json
import subprocess
from pathlib import Path

# 项目标志文件 → 类型/语言/构建命令映射
MARKERS = {
    "Cargo.toml": {"lang": "Rust", "build": "cargo build", "test": "cargo test"},
    "package.json": {"lang": "JavaScript/TypeScript", "build": "npm run build", "test": "npm test"},
    "Package.swift": {"lang": "Swift", "build": "swift build", "test": "swift test"},
    "go.mod": {"lang": "Go", "build": "go build ./...", "test": "go test ./..."},
    "pyproject.toml": {"lang": "Python", "build": None, "test": "pytest"},
    "setup.py": {"lang": "Python", "build": None, "test": "pytest"},
    "CMakeLists.txt": {"lang": "C/C++", "build": "cmake --build build", "test": "ctest"},
    "Makefile": {"lang": "unknown", "build": "make", "test": "make test"},
}

# 文档目录候选
DOC_DIRS = ["docs", "doc", "document", "documentation", "wiki"]


def detect_project(root: Path) -> dict:
    """探测项目信息。"""
    info = {
        "languages": [],
        "build_commands": [],
        "test_commands": [],
        "project_type": "unknown",
        "output_dir": None,
        "run_script": None,
        "log_location": None,
        "xcodeproj": None,
    }

    # 扫描标志文件
    for marker, meta in MARKERS.items():
        if (root / marker).exists():
            if meta["lang"] != "unknown":
                info["languages"].append(meta["lang"])
            if meta["build"]:
                info["build_commands"].append(meta["build"])
            if meta["test"]:
                info["test_commands"].append(meta["test"])

    # 检查 Xcode 项目
    xcodeprojs = list(root.glob("*.xcodeproj")) + list(root.glob("*/*.xcodeproj"))
    if xcodeprojs:
        info["xcodeproj"] = str(xcodeprojs[0].relative_to(root))
        if "Swift" not in info["languages"]:
            info["languages"].append("Swift")

    # 推导项目类型
    if info["xcodeproj"]:
        info["project_type"] = "GUI 应用"
    elif (root / "src" / "main.rs").exists() or (root / "main.go").exists():
        info["project_type"] = "CLI 工具"
    elif any((root / "src" / f"lib.{ext}").exists() for ext in ["rs", "ts", "js"]):
        info["project_type"] = "库"
    elif (root / "package.json").exists():
        # 检查是否有 dev server
        pkg = (root / "package.json").read_text(encoding="utf-8")
        if '"dev"' in pkg or '"start"' in pkg:
            info["project_type"] = "Web 服务"

    # 探测文档目录
    for doc_dir in DOC_DIRS:
        doc_path = root / doc_dir
        if doc_path.is_dir():
            info["output_dir"] = str(doc_path.relative_to(root))
            break

    # 探测运行脚本
    scripts_dir = root / "scripts"
    if scripts_dir.is_dir():
        for script in scripts_dir.iterdir():
            if script.name in ("run.sh", "dev.sh", "start.sh"):
                info["run_script"] = str(script.relative_to(root))
                break

    # 读取 CLAUDE.md 提取额外信息
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")
        info["has_claude_md"] = True

        # 提取构建命令
        build_section = re.search(
            r"(?:^##.*构建|^##.*[Bb]uild).*?\n(.*?)(?=^##|\Z)",
            content, re.MULTILINE | re.DOTALL
        )
        if build_section:
            info["claude_md_build_section"] = build_section.group(0).strip()[:500]

        # 提取日志系统信息
        log_match = re.search(r"日志.*?[：:]\s*`?([^`\n]+)", content)
        if log_match:
            info["log_location"] = log_match.group(1).strip()
    else:
        info["has_claude_md"] = False

    return info


def format_build_command(info: dict) -> str:
    """从探测结果推导主构建命令。"""
    if info.get("claude_md_build_section"):
        # 优先从 CLAUDE.md 提取
        return "(见 CLAUDE.md)"
    if info["build_commands"]:
        return " && ".join(info["build_commands"])
    return "unknown"


def cmd_detect(args: list[str]) -> None:
    """detect [--project-root <path>] → JSON 格式项目信息"""
    root = Path.cwd()
    i = 0
    while i < len(args):
        if args[i] == "--project-root" and i + 1 < len(args):
            root = Path(args[i + 1]).resolve()
            i += 2
        else:
            i += 1

    info = detect_project(root)
    print(json.dumps(info, ensure_ascii=False, indent=2))


def cmd_detect_and_write(args: list[str]) -> None:
    """detect-and-write [--project-root <path>] → 检测并写入 SKILL-STATE.md"""
    root = Path.cwd()
    i = 0
    while i < len(args):
        if args[i] == "--project-root" and i + 1 < len(args):
            root = Path(args[i + 1]).resolve()
            i += 2
        else:
            i += 1

    info = detect_project(root)

    # 确定 output_dir，fallback 为 docs/
    output_dir = info.get("output_dir")
    if not output_dir:
        output_dir = "docs"
        (root / output_dir).mkdir(exist_ok=True)
        print(f"未找到文档目录，已创建 {output_dir}/", file=sys.stderr)

    # 构建 skill-state.py write-info 参数
    write_args = [
        "python3", ".claude/skills/xbase/skill-state.py", "write-info",
        "类型", info.get("project_type", "unknown"),
        "构建命令", format_build_command(info),
        "output_dir", output_dir,
    ]

    if info.get("run_script"):
        write_args.extend(["运行脚本", info["run_script"]])
    if info.get("log_location"):
        write_args.extend(["日志位置", info["log_location"]])

    result = subprocess.run(write_args, capture_output=True, text=True, cwd=str(root))
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    # 同时输出 JSON 供调用方参考
    print(json.dumps(info, ensure_ascii=False, indent=2))


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "detect": cmd_detect,
        "detect-and-write": cmd_detect_and_write,
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}", file=sys.stderr)
        print(f"可用命令: {', '.join(commands)}", file=sys.stderr)
        sys.exit(1)

    commands[cmd](args)


if __name__ == "__main__":
    main()

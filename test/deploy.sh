#!/usr/bin/env bash
# 部署（或重新部署）x-skills 到测试项目
# 用法：./deploy.sh [项目名...]（不指定则全部）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECTS_DIR="$SCRIPT_DIR/projects"

SKILLS=(xbase xdebug xlog xtest xreview xcommit xdoc xdecide)

# 确定目标项目
targets=()
if [ $# -gt 0 ]; then
  targets=("$@")
else
  for d in "$PROJECTS_DIR"/*/; do
    [ -d "$d" ] && targets+=("$(basename "$d")")
  done
fi

if [ ${#targets[@]} -eq 0 ]; then
  echo "无项目可部署。先运行 setup.sh"
  exit 0
fi

for name in "${targets[@]}"; do
  dir="$PROJECTS_DIR/$name"
  if [ ! -d "$dir" ]; then
    echo "跳过 $name (不存在，先运行 setup.sh)"
    continue
  fi

  target="$dir/.claude/skills"
  rm -rf "$target"
  mkdir -p "$target"

  for skill in "${SKILLS[@]}"; do
    src="$SKILLS_DIR/$skill"
    [ -d "$src" ] && cp -r "$src" "$target/$skill"
  done

  echo "已部署到 $name (${#SKILLS[@]} skills)"
done

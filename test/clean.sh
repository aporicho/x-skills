#!/usr/bin/env bash
# 删除克隆的测试项目
# 用法：./clean.sh [项目名...]（不指定则全部，全部时需确认）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECTS_DIR="$SCRIPT_DIR/projects"

if [ $# -gt 0 ]; then
  # 删除指定项目
  for name in "$@"; do
    dir="$PROJECTS_DIR/$name"
    if [ -d "$dir" ]; then
      rm -rf "$dir"
      echo "已删除 $name"
    else
      echo "跳过 $name (不存在)"
    fi
  done
else
  # 删除全部，需确认
  read -p "确认删除 $PROJECTS_DIR 下所有项目？(y/N) " confirm
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "取消。"
    exit 0
  fi
  for project in "$PROJECTS_DIR"/*/; do
    [ -d "$project" ] || continue
    name="$(basename "$project")"
    rm -rf "$project"
    echo "已删除 $name"
  done
fi

echo ""
echo "清理完成。"

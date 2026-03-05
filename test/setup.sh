#!/usr/bin/env bash
# 首次设置：克隆测试项目 + 部署 skills
# 用法：./setup.sh [项目名...]（不指定则全部）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECTS_DIR="$SCRIPT_DIR/projects"
CONF="$SCRIPT_DIR/projects.conf"

# 从 conf 读取项目列表，过滤指定项目
list_projects() {
  grep -v '^\s*#' "$CONF" | grep -v '^\s*$'
}

# 克隆项目
if [ $# -gt 0 ]; then
  for arg in "$@"; do
    repo=$(list_projects | awk -v name="$arg" '$1 == name { print $2 }')
    if [ -z "$repo" ]; then
      echo "错误：$arg 不在 projects.conf 中"
      continue
    fi
    dir="$PROJECTS_DIR/$arg"
    if [ -d "$dir" ]; then
      echo "跳过 $arg (已存在)"
    else
      echo "克隆 $arg ..."
      git clone --depth 50 "https://github.com/${repo}.git" "$dir"
    fi
  done
else
  list_projects | while read -r name repo; do
    dir="$PROJECTS_DIR/$name"
    if [ -d "$dir" ]; then
      echo "跳过 $name (已存在)"
    else
      echo "克隆 $name ..."
      git clone --depth 50 "https://github.com/${repo}.git" "$dir"
    fi
  done
fi

# 部署 skills
"$SCRIPT_DIR/deploy.sh" "$@"

echo ""
echo "设置完成。"

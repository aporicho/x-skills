#!/usr/bin/env bash
# 重置测试项目到干净状态 + 重新部署 skills
# 用法：./reset.sh [项目名...]（不指定则全部）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECTS_DIR="$SCRIPT_DIR/projects"

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
  echo "无项目可重置。先运行 setup.sh"
  exit 0
fi

for name in "${targets[@]}"; do
  dir="$PROJECTS_DIR/$name"
  if [ ! -d "$dir" ]; then
    echo "跳过 $name (不存在)"
    continue
  fi

  echo "重置 $name ..."
  (
    cd "$dir"
    git checkout -- . 2>/dev/null || true
    git clean -fd 2>/dev/null || true
    rm -f SKILL-STATE.md
  )
  echo "  已重置"
done

# 重新部署
"$SCRIPT_DIR/deploy.sh" "${targets[@]}"

echo ""
echo "重置完成。"

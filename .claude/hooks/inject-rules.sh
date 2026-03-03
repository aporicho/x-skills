#!/bin/bash
# 从 CLAUDE.md 的 ## 守则 段提取规则，注入到每次用户输入前
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_MD="$CLAUDE_PROJECT_DIR/CLAUDE.md"

if [ ! -f "$CLAUDE_MD" ]; then
  exit 0
fi

# 提取 ## 守则 到下一个 ## 之间的内容
RULES=$(sed -n '/^## 守则$/,/^## /{/^## 守则$/d;/^## /d;p;}' "$CLAUDE_MD" | sed '/^$/d')

if [ -z "$RULES" ]; then
  exit 0
fi

echo "$RULES"
exit 0

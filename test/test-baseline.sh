#!/usr/bin/env bash
# 跑 baseline（无 skill）对比测试
# 用法同 test.sh，但禁用所有 skill，结果存到 baseline/ 子目录
set -euo pipefail

# 允许从 Claude Code session 内部调用（绕过嵌套检测）
unset CLAUDECODE 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECTS_DIR="$SCRIPT_DIR/projects"
RESULTS_DIR="$SCRIPT_DIR/results"

TIMEOUT="${XSKILLS_TEST_TIMEOUT:-600}"
MAX_BUDGET="${XSKILLS_TEST_BUDGET:-5.00}"

# baseline 用自然语言提示词（不触发 skill）
declare_baselines() {
  cat <<'EOF'
xbase|请分析这个项目的结构，创建开发所需的配置文件和规则文档
xdoc|请检查这个项目的文档健康状况，找出断链、格式问题、结构问题、过时内容
xreview|请审查这个项目最近的代码提交，找出潜在问题
xtest|请分析这个项目的测试状况，列出测试覆盖情况
xcommit|请帮我提交当前的代码变更
EOF
}

usage() {
  echo "用法："
  echo "  $0 <项目名> [skill名]"
  echo "  $0 --all"
  echo ""
  echo "与 test.sh 相同的参数，但禁用 skill，用自然语言提示词。"
  echo "结果存在同一时间戳目录的 baseline/ 子目录。"
  exit 1
}

if ! command -v claude &>/dev/null; then
  echo "错误：未找到 claude CLI。"
  exit 1
fi

[ $# -eq 0 ] && usage

RUN_TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

run_baseline() {
  local project="$1"
  local prompt="$2"
  local label="$3"
  local project_dir="$PROJECTS_DIR/$project"
  local result_dir="$RESULTS_DIR/$RUN_TIMESTAMP/$project/baseline-$label"

  mkdir -p "$result_dir"

  echo "--- baseline: $project / $label ---"
  echo "提示词: $prompt"

  local start_time
  start_time=$(date +%s)

  local full_prompt="[测试模式] 这是自动化测试，无人值守。遇到需要用户确认的步骤时，直接选择第一个选项继续执行，不要等待用户输入。

$prompt"
  (
    cd "$project_dir"
    claude -p "$full_prompt" \
      --disable-slash-commands \
      --allowedTools "Bash Read Edit Write Grep Glob AskUserQuestion" \
      --output-format stream-json \
      --verbose \
      --max-budget-usd "$MAX_BUDGET" \
      > "$result_dir/stream.jsonl" 2>"$result_dir/stderr.txt" \
      &
    local pid=$!
    ( sleep "$TIMEOUT" && kill "$pid" 2>/dev/null ) &
    local watchdog=$!
    wait "$pid" 2>/dev/null || true
    kill "$watchdog" 2>/dev/null || true
    wait "$watchdog" 2>/dev/null || true
  )

  local end_time
  end_time=$(date +%s)
  local duration=$((end_time - start_time))

  if [ -f "$result_dir/stream.jsonl" ] && command -v jq &>/dev/null; then
    jq -r 'select(.type == "assistant") | .message.content[]? | select(.type == "text") | .text' \
      "$result_dir/stream.jsonl" \
      > "$result_dir/output.txt" 2>/dev/null || true
  fi

  cat > "$result_dir/meta.json" <<METAEOF
{
  "project": "$project",
  "skill": "baseline-$label",
  "prompt": "$prompt",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "run_id": "$RUN_TIMESTAMP",
  "duration_seconds": $duration,
  "configuration": "without_skill"
}
METAEOF

  local output_lines=0
  [ -f "$result_dir/output.txt" ] && output_lines=$(wc -l < "$result_dir/output.txt" | tr -d ' ')
  echo "  完成 (${duration}s, ${output_lines} 行输出)"
  echo ""
}

run_all_baselines() {
  local project="$1"
  declare_baselines | while IFS='|' read -r skill prompt; do
    run_baseline "$project" "$prompt" "$skill"
  done
}

if [ "$1" = "--all" ]; then
  for d in "$PROJECTS_DIR"/*/; do
    [ -d "$d" ] || continue
    run_all_baselines "$(basename "$d")"
  done
  echo "全部 baseline 完成。结果在 $RESULTS_DIR/$RUN_TIMESTAMP/"
  exit 0
fi

project="$1"
shift

if [ ! -d "$PROJECTS_DIR/$project" ]; then
  echo "错误：项目 $project 不存在。"
  exit 1
fi

if [ $# -eq 0 ]; then
  run_all_baselines "$project"
else
  label="$1"
  prompt=$(declare_baselines | grep "^${label}|" | cut -d'|' -f2)
  if [ -z "$prompt" ]; then
    echo "错误：未知 skill $label"
    exit 1
  fi
  run_baseline "$project" "$prompt" "$label"
fi

echo "baseline 完成。结果在 $RESULTS_DIR/$RUN_TIMESTAMP/"

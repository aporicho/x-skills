#!/usr/bin/env bash
# 对测试项目运行 skill 测试
# 用法：
#   ./test.sh clay xdoc 巡检    # 对 clay 运行 xdoc 巡检
#   ./test.sh clay              # 对 clay 按依赖顺序运行所有 skill
#   ./test.sh --all             # 对所有项目运行所有 skill
#
# 输出：
#   results/<时间戳>/<项目>/<skill>/
#     output.txt     - 文本输出
#     stream.jsonl   - 完整工具调用记录
#     meta.json      - 元数据
#     grade.txt      - 自动评判结果（如果有 eval 定义）
set -euo pipefail

# 允许从 Claude Code session 内部调用（绕过嵌套检测）
unset CLAUDECODE 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECTS_DIR="$SCRIPT_DIR/projects"
RESULTS_DIR="$SCRIPT_DIR/results"
EVALS_DIR="$SCRIPT_DIR/evals"

# 超时（秒），可通过环境变量覆盖
TIMEOUT="${XSKILLS_TEST_TIMEOUT:-600}"
# 预算上限（美元）
MAX_BUDGET="${XSKILLS_TEST_BUDGET:-5.00}"

# skill 默认测试命令（按依赖顺序：xbase 必须在前）
declare_skills() {
  cat <<'EOF'
xbase|/xbase
xdoc|/xdoc 巡检
xreview|/xreview
xtest|/xtest
xcommit|/xcommit
EOF
}

usage() {
  echo "用法："
  echo "  $0 <项目名> [skill名] [参数...]"
  echo "  $0 --all"
  echo ""
  echo "示例："
  echo "  $0 clay                  # 对 clay 按顺序跑全部 skill"
  echo "  $0 clay xdoc 巡检        # 对 clay 跑 xdoc 巡检"
  echo "  $0 pinia xbase           # 对 pinia 跑 xbase 初始化"
  echo "  $0 --all                 # 全部项目 x 全部 skill"
  echo ""
  echo "环境变量："
  echo "  XSKILLS_TEST_TIMEOUT=300   超时秒数（默认 300）"
  echo "  XSKILLS_TEST_BUDGET=1.00   单次预算上限（默认 \$1.00）"
  echo ""
  echo "可用项目："
  ls "$PROJECTS_DIR" 2>/dev/null || echo "  (无，先运行 setup.sh)"
  echo ""
  echo "可用 skill：xbase xdoc xreview xtest xcommit"
  exit 1
}

# 检查 claude CLI
if ! command -v claude &>/dev/null; then
  echo "错误：未找到 claude CLI。请先安装 Claude Code。"
  exit 1
fi

[ $# -eq 0 ] && usage

# 本次运行的统一时间戳
RUN_TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

# 运行单个测试
run_test() {
  local project="$1"
  local prompt="$2"
  local label="$3"
  local project_dir="$PROJECTS_DIR/$project"
  local result_dir="$RESULTS_DIR/$RUN_TIMESTAMP/$project/$label"

  mkdir -p "$result_dir"

  echo "--- 运行: $project / $label ---"
  echo "提示词: $prompt"
  echo "超时: ${TIMEOUT}s | 预算: \$${MAX_BUDGET}"

  local start_time
  start_time=$(date +%s)

  # 注意：
  # - -p 模式无交互，通过 system prompt 指示自动确认
  # - stream-json 捕获完整工具调用链，同时提取 text 输出
  # 后台运行 claude，用 kill 实现超时（macOS 没有 timeout 命令）
  local full_prompt="[测试模式] 这是自动化测试，无人值守。遇到需要用户确认的步骤时，直接选择第一个选项继续执行，不要等待用户输入。

$prompt"
  (
    cd "$project_dir"
    claude -p "$full_prompt" \
      --allowedTools "Bash Read Edit Write Grep Glob Skill AskUserQuestion" \
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

  # 从 stream-json 提取文本输出（用 jq 正确处理转义）
  if [ -f "$result_dir/stream.jsonl" ] && command -v jq &>/dev/null; then
    jq -r 'select(.type == "assistant") | .message.content[]? | select(.type == "text") | .text' \
      "$result_dir/stream.jsonl" \
      > "$result_dir/output.txt" 2>/dev/null || true
  fi

  # 元数据
  cat > "$result_dir/meta.json" <<METAEOF
{
  "project": "$project",
  "skill": "$label",
  "prompt": "$prompt",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "run_id": "$RUN_TIMESTAMP",
  "duration_seconds": $duration,
  "timeout_limit": $TIMEOUT,
  "budget_limit": $MAX_BUDGET
}
METAEOF

  local output_lines=0
  [ -f "$result_dir/output.txt" ] && output_lines=$(wc -l < "$result_dir/output.txt" | tr -d ' ')

  echo "  完成 (${duration}s, ${output_lines} 行输出)"
  echo "  结果: $result_dir/"

  # 自动评判（如果有 eval 定义）
  run_grading "$project" "$label" "$result_dir"

  echo ""
}

# LLM-as-a-judge 自动评判
run_grading() {
  local project="$1"
  local label="$2"
  local result_dir="$3"
  local eval_file="$EVALS_DIR/${label}.yaml"

  # 没有 eval 定义就跳过
  if [ ! -f "$eval_file" ]; then
    echo "  评判: 跳过 (无 $eval_file)"
    return
  fi

  local output_file="$result_dir/output.txt"
  if [ ! -s "$output_file" ]; then
    echo "  评判: 跳过 (无输出)"
    return
  fi

  echo "  评判中..."

  local expected
  expected=$(grep -A100 'expected_behavior:' "$eval_file" | grep '^\s*-' | sed 's/^\s*-\s*//' || true)

  if [ -z "$expected" ]; then
    echo "  评判: 跳过 (无 expected_behavior)"
    return
  fi

  local output
  output=$(head -200 "$output_file")

  local grade_prompt
  grade_prompt=$(cat <<GRADEEOF
你是一个评判员。判断以下 AI 输出是否满足各项预期行为。

## AI 输出（截取前 200 行）
$output

## 预期行为
$expected

## 输出格式
对每条预期行为，输出一行：
PASS/FAIL | 预期行为描述 | 简短理由

最后一行输出总结：X/Y passed
GRADEEOF
)

  # 用 claude -p 做评判（haiku 模型，便宜快速）
  claude -p "$grade_prompt" \
    --model haiku \
    --output-format text \
    --max-budget-usd 0.05 \
    > "$result_dir/grade.txt" 2>/dev/null \
    &
  local grade_pid=$!
  ( sleep 60 && kill "$grade_pid" 2>/dev/null ) &
  local grade_watchdog=$!
  wait "$grade_pid" 2>/dev/null || echo "评判失败" > "$result_dir/grade.txt"
  kill "$grade_watchdog" 2>/dev/null || true
  wait "$grade_watchdog" 2>/dev/null || true

  # 输出评判结果摘要
  local summary
  summary=$(tail -1 "$result_dir/grade.txt")
  echo "  评判: $summary"
}

# 对一个项目跑全部 skill
run_all_skills() {
  local project="$1"
  declare_skills | while IFS='|' read -r skill prompt; do
    run_test "$project" "$prompt" "$skill"
  done
}

# --all 模式
if [ "$1" = "--all" ]; then
  for d in "$PROJECTS_DIR"/*/; do
    [ -d "$d" ] || continue
    run_all_skills "$(basename "$d")"
  done
  echo "全部测试完成。结果在 $RESULTS_DIR/$RUN_TIMESTAMP/"
  exit 0
fi

# 指定项目
project="$1"
shift

if [ ! -d "$PROJECTS_DIR/$project" ]; then
  echo "错误：项目 $project 不存在。可用项目："
  ls "$PROJECTS_DIR" 2>/dev/null
  exit 1
fi

if [ $# -eq 0 ]; then
  run_all_skills "$project"
else
  skill="$1"
  shift
  if [ $# -gt 0 ]; then
    prompt="/$skill $*"
  else
    prompt=$(declare_skills | grep "^${skill}|" | cut -d'|' -f2)
    if [ -z "$prompt" ]; then
      prompt="/$skill"
    fi
  fi
  run_test "$project" "$prompt" "$skill"
fi

echo "测试完成。结果在 $RESULTS_DIR/$RUN_TIMESTAMP/"

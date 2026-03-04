# x-skills 测试

用真实 GitHub 项目端到端验证 x-skills 的行为。

## 测试项目

项目列表在 `projects.conf` 中维护，可自行增删。当前包含 4 个不同技术栈的项目（C、Swift、Rust、Vue+TS）。

## 快速开始

```bash
cd test/

# 1. 首次：克隆项目 + 部署 skills
./setup.sh

# 2. 重置到干净状态 + 初始化
./reset.sh clay
./test.sh clay xbase

# 3. 跑目标 skill
./test.sh clay xdoc 巡检

# 4. 查看结果
cat results/最新目录/clay/xdoc/output.txt    # 文本输出
cat results/最新目录/clay/xdoc/grade.txt     # 自动评判
```

## 脚本

| 脚本 | 用途 | 示例 |
|------|------|------|
| `setup.sh` | 克隆项目 + 部署 skills | `./setup.sh` 或 `./setup.sh clay` |
| `deploy.sh` | skill 更新后重新部署 | `./deploy.sh` 或 `./deploy.sh pinia` |
| `reset.sh` | 清除 xbase 产物 + 重新部署 | `./reset.sh` 或 `./reset.sh clay` |
| `clean.sh` | 删除克隆的项目 | `./clean.sh` 或 `./clean.sh clay` |
| `test.sh` | 运行 skill 测试 + 自动评判 | `./test.sh clay xdoc 巡检` |
| `test-baseline.sh` | 运行无 skill 的 baseline 对比 | `./test-baseline.sh clay xdoc` |

所有脚本都支持指定项目名，不指定则操作全部项目。

## 测试场景

### 单 skill 测试

每个 skill 独立测试。xbase 是前置依赖，其他 skill 需要先跑 xbase。

```bash
./reset.sh clay
./test.sh clay xbase
./test.sh clay xdoc 巡检
```

对照 `xdoc/SKILL.md` 的对应章节检查输出。其他 skill 同理。

可用的 skill 命令参考各 SKILL.md 的参数处理段：

| skill | 典型测试命令 | 参考 |
|-------|-------------|------|
| xbase | `./test.sh <项目> xbase` | `xbase/SKILL.md` |
| xdoc | `./test.sh <项目> xdoc 巡检` | `xdoc/SKILL.md` → 参数处理 |
| xdoc | `./test.sh <项目> xdoc 同步` | 同上 |
| xdoc | `./test.sh <项目> xdoc docs/` | 同上（路径参数） |
| xreview | `./test.sh <项目> xreview` | `xreview/SKILL.md` |
| xtest | `./test.sh <项目> xtest` | `xtest/SKILL.md` |
| xcommit | `./test.sh <项目> xcommit` | `xcommit/SKILL.md` |

### 全链路测试

验证 skill 间的衔接。

```bash
./reset.sh clay
./test.sh clay xbase
./test.sh clay xdoc 巡检
./test.sh clay xreview
./test.sh clay xcommit
```

核心检查点：后续 skill 是否从 SKILL-STATE.md 正确读取到前置 skill 的产物路径。

### baseline 对比

验证 skill 是否比 claude 裸跑更好。

```bash
# with skill
./reset.sh clay
./test.sh clay xbase
./test.sh clay xdoc 巡检

# without skill（自然语言提示词，禁用 slash commands）
./test-baseline.sh clay xdoc
```

对比 `results/` 下的 with_skill 和 baseline 输出及评判结果。

### 跨项目对比

同一 skill 在不同技术栈上是否产出合理的差异化结果。

```bash
./reset.sh
./test.sh --all
```

### 迭代测试

修改 skill 后快速验证：

```bash
./deploy.sh                        # 重新部署（保留 xbase 产物）
./test.sh clay xdoc 巡检           # 直接跑，不用重新初始化

# 如果需要从头测试
./reset.sh clay
./test.sh clay xbase
./test.sh clay xdoc 巡检
```

## 自动评判

`test.sh` 运行完后会自动用 LLM (Haiku) 评判输出是否满足预期行为。

评判标准定义在 `evals/<skill>.yaml`：

```yaml
expected_behavior:
  - 输出了结构化的健康报告，有明确的维度分类
  - 发现的问题有具体文件路径和描述
```

评判结果写入 `grade.txt`，格式：`PASS/FAIL | 预期行为 | 理由`。

要自定义评判标准，编辑 `evals/` 下对应的 YAML 文件即可。

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `XSKILLS_TEST_TIMEOUT` | 600 | 单次测试超时（秒） |
| `XSKILLS_TEST_BUDGET` | 5.00 | 单次测试预算上限（美元） |

## 结果目录

```
results/
└── 20260304-153200/            # 时间戳（同批次共用）
    └── clay/
        ├── xbase/
        │   ├── output.txt      # 文本输出
        │   ├── stream.jsonl    # 完整工具调用记录
        │   ├── stderr.txt      # 错误输出
        │   ├── meta.json       # 元数据（时长、预算等）
        │   └── grade.txt       # 自动评判结果
        ├── xdoc/
        │   └── ...
        └── baseline-xdoc/      # baseline 对比（test-baseline.sh）
            └── ...
```

## 自动确认机制

`-p` 模式下无法交互。test.sh 在提示词前注入 `[测试模式]` 指令，让 AI 遇到确认步骤时自动选择第一个选项继续执行。

对于可通过参数跳过交互的 skill（如 `/xdoc 巡检`），优先使用参数方式。

## 已知限制

- **自动确认不是 100% 可靠**：AI 可能仍然用文本提问而非 AskUserQuestion 工具，导致流程提前终止。遇到此情况，检查 output.txt 末尾是否有疑问句。
- **stream-json 需要 --verbose**：`-p` 模式下 `--output-format stream-json` 必须搭配 `--verbose`，否则报错且无输出。
- **评判精度**：LLM-as-a-judge 不是 100% 准确，grade.txt 作为参考，最终判断看 output.txt 原文。
- **stream-json 解析**：output.txt 从 stream-json 提取，可能有格式损失，完整内容看 stream.jsonl。
- **嵌套 session**：脚本已处理（unset CLAUDECODE），可从 Claude Code session 内部调用。

## 评估方式

输出是否符合预期，对照对应的 SKILL.md 判断。自动评判 (grade.txt) 提供快速筛选，但不替代人工审阅。

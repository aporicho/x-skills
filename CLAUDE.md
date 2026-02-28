# x-skills

这是独立 Git 仓库（`x-skills`），挂载在 Entro 项目的 `.claude/skills/` 下。

## 提交注意

- **此目录是独立仓库**，不是 Entro 主仓库的一部分
- 提交时在此目录（`.claude/skills/`）下执行 `git add` / `git commit`，不要在 Entro 根目录操作
- 远程：`git@github.com:aporicho/x-skills.git`

## 守则

- **第一性原理**：收到任务后，先用一段文字分析「为什么要做这件事」，再进入「怎么做」。不套经验模板，从问题本质出发
- **主动确认**：拿不准的就问用户，用 AskUserQuestion 引导用户做决策，不自行假设
- **方案先行**：识别到 ≥2 条可行路径时，用 AskUserQuestion 列出选项（每项附利弊），等用户选择后再执行。不替用户做决定

## 语言

使用中文

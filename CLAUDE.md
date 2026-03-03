# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

x-skills 是一套 Claude Code Skills 体系，用于保证 AI 辅助开发时的**过程质量和知识不丢失**。部署到目标项目的 `.claude/skills/` 目录下使用。

架构设计、文件体系、术语表、衔接矩阵见 `docs/system.md`（核心架构文档）。编写或修改 SKILL.md 及 references/ 时，对照 `docs/SKILL-EVALUATION.md` 检查质量。各 skill 的设计文档在 `docs/x{name}.md`。

## 当前阶段：Docs-First 设计

- 目标：产出高质量设计文档，用文档驱动后续重构
- 现有代码仅作**参考**，不作为设计起点
- **隔离现有实现**：分析时先从需求/目标独立推导，不被现有结构/思路带偏；现有实现只在对照验证环节引入
- 产出的文档将作为后续重构的唯一规范

## 守则

- **第一性原理**：收到任务后，先用一段文字分析「为什么要做这件事」，再进入「怎么做」。不套经验模板，从问题本质出发
- **主动确认**：拿不准的就问用户，用 AskUserQuestion 引导用户做决策，不自行假设
- **方案先行**：识别到 ≥2 条可行路径时，用 AskUserQuestion 列出选项（每项附利弊），等用户选择后再执行。不替用户做决定

## 语言

使用中文

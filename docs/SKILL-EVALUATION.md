# Skill 评判框架

> x-skills 项目内部标准。用于审查本项目 SKILL.md 及其 references/ 文件的质量，排查 skill 不生效或行为异常的问题。
> 来源：[Claude Code Skills 文档](https://code.claude.com/docs/en/skills)、[Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)、[Agent Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)、[Claude 4 Prompt Best Practices](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) + 项目自身经验。

---

## 总则

1. **所有项目通用** — 好的 skill 能直接复制到任何项目使用，不硬编码项目特定的路径、命令、目录结构或工作流假设。项目差异通过动态探测和 SKILL-STATE.md 解决。
2. **选项优先于打字** — 能用 AskUserQuestion 选项就不让用户打字，Other 兜底自由输入。每轮只问一个问题，不堆叠。
3. **操作步骤要具体** — 给用户的操作指引必须是 1-2-3 具体步骤，不泛泛说"请操作"或"请测试"。

以下所有维度的检查均以总则为前提。

---

## A. 结构完整性

| 检查项 | 通过标准 | 常见问题 |
|--------|---------|---------|
| frontmatter 关键字段 | `description` 有值（`name` 可选，省略时用目录名） | description 缺失导致 Claude 不知何时触发 |
| description 触发词 | 包含用户自然会说的关键词和使用场景 | 太泛（"处理代码"）或太窄（只匹配一种说法） |
| argument-hint | 有参数的 skill 给出提示 | 用户不知道传什么参数 |
| allowed-tools | 只列出实际需要的工具，最小化 | 列出所有工具 → 安全表面过大 |
| 调用控制 | 有副作用的 skill 设 `disable-model-invocation: true` | Claude 自动触发了不该自动触发的操作（如部署、提交） |
| 执行上下文 | 需要隔离执行的 skill 设 `context: fork`，并指定 `agent` 类型 | skill 在主对话上下文中执行，副作用影响当前会话 |
| 可见性控制 | 背景知识型 skill 设 `user-invocable: false`；注意它不阻止 Skill tool 调用 | 用户看到无意义的 `/slash-command`，或误以为 `user-invocable: false` 等于禁止 Claude 触发 |
| 参数传递 | 接收参数的 skill 使用 `$ARGUMENTS` / `$N` 占位符，SKILL.md 内容中显式引用 | 参数被追加到末尾而非插入预期位置，agent 不知道参数的语义 |
| 无硬编码路径 | 所有路径通过动态探测或 SKILL-STATE.md 获取 | 换项目就坏 |
| 无硬编码命令 | 构建、测试等命令从 CLAUDE.md 或项目配置读取 | 只在特定项目能用 |
| 状态持久化 | 跨会话需要的数据写入 SKILL-STATE.md | 每次重新探测，浪费时间 |

## B. 内容组织与引用

> 核心原则：只展示 agent 当前步骤需要的信息，后续细节按需加载。
> 来源：[Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)、[Claude Code Skills](https://code.claude.com/docs/en/skills)

### 三层加载机制

| 层级 | 加载时机 | 内容 | token 开销 |
|------|---------|------|-----------|
| 1. frontmatter | 启动时预加载 | 所有 skill 的 `name` + `description` | 极小（~100 tokens/skill） |
| 2. SKILL.md | Claude 判断 skill 相关时加载 | 主体指令和导航 | 中（< 500 行） |
| 3. 引用文件 | Claude 执行到需要时按需读取 | references/ 下的详细规范、示例等 | 按需（不读则零开销） |

### 引用方式决策

> 标准方式是 SKILL.md 中用 markdown 链接指向 references/ 文件，Claude 按需 Read。本项目额外支持 DCI 预注入（`!`include.py\`\`），用于 agent 不读就做不对的执行前提。

| 方式 | 机制 | 适用场景 | 判断标准 |
|------|------|---------|---------|
| 标准引用 | SKILL.md 中 markdown 链接，Claude 自行 Read | 创建/生成任务的参考材料 | agent 的任务就是"按 X 文件生成"，读取是任务的直接依赖 |
| DCI 预注入 | `!`include.py\`` 在展开前注入上下文 | 当前步骤的执行前提——缺了就做不对 | agent 不读这个内容就无法正确完成任务 |
| 不引用 | 不提及 | 与当前步骤无关的内容 | 提了反而分散注意力 |

**典型分配**：
- **标准引用**：生成 LOG-RULES.md 时的 log-rules-guideline.md（创建任务的直接依赖，Claude 会主动读）
- **DCI 预注入**：扫描代码时的 LOG-RULES.md（是判断标准，不读就无法判断）
- **不引用**：阶段 2 不提质量原则（那是阶段 0 的事，和阶段 2 无关）

### 标准引用的写法

> 链接文本要告诉 Claude **文件里有什么**和**什么时候该去读**，而不只是给一个文件名。

✅ 好——Claude 能判断何时需要读：

```markdown
## 日志扫描

1. 用 Glob 搜索项目中所有 `.swift` 文件
2. 逐文件检查日志调用是否符合规范

**日志规范**: 判断标准见 [references/log-rules.md](references/log-rules.md)
**生成指南**: 生成 LOG-RULES.md 时的结构和质量原则见 [references/log-rules-guideline.md](references/log-rules-guideline.md)
```

❌ 坏——文件堆在一起，没说各自用途，Claude 可能全读或全不读：

```markdown
参考资料:
- [references/log-rules.md](references/log-rules.md)
- [references/log-rules-guideline.md](references/log-rules-guideline.md)
```

### 引用规则

| 规则 | 说明 |
|------|------|
| **引用只深一层** | 所有 references/ 文件直接从 SKILL.md 链接，不要 A → B → C 嵌套——Claude 遇到嵌套引用可能只 `head -100` 预览而非完整读取 |
| **长文件加目录** | 超过 100 行的 references/ 文件在顶部加目录（Contents），确保 Claude 即使部分读取也能看到完整范围 |
| **文件名自描述** | 用 `form_validation_rules.md` 而非 `doc2.md`——Claude 靠文件名判断是否需要读取 |
| **执行 vs 阅读** | 对脚本文件明确区分："运行 `analyze.py` 提取字段"（执行）vs "参见 `analyze.py` 了解算法"（阅读） |
| **多领域按文件拆分** | 每个领域一个 references/ 文件，SKILL.md 只做路由——不把所有领域内联在 SKILL.md 中 |
| **基础内联高级外链** | 简单操作写在 SKILL.md，高级/分支操作链接到 references/——Claude 按用户实际需求决定是否读取 |

### DCI 预注入（本项目扩展）

> DCI = Dynamic Context Injection，通过 `!`include.py\`\` 在 SKILL.md 展开前将内容注入上下文。

#### 注入方式

| 方式 | 语法 | 门控 | 适用场景 |
|------|------|------|---------|
| 静态注入 | `!`include.py skill ref\`` | 已初始化则跳过 | 阶段 0 的探测/创建协议、质量标准 |
| 动态注入 | `!`include.py skill $key\`` | 始终注入 | 运行时依赖的产出物（如 LOG-RULES.md） |

#### 拼接质量

> 多个 `!include` 展开后顺序拼接为一段连续文本，agent 看到的是拼接结果，不知道原始来源。

| 检查项 | 通过标准 | 常见问题 |
|--------|---------|---------|
| 块间有边界 | 每个被注入文件以标题行或分隔符开头 | 多块内容融为一体，agent 混淆来源和用途 |
| 拼接顺序有逻辑 | 依赖关系靠前，执行顺序与注入顺序一致 | agent 先看到具体步骤，后看到前置条件 |
| 无指令冲突 | 多个注入块不包含矛盾指令 | agent 在矛盾指令间随机选择 |
| 无重复内容 | 不同注入块不重复相同段落 | token 浪费 + agent 困惑是否有细微差异 |
| 拼接后可读 | 手动把所有 include 输出拼在一起审读 | 单独看每块没问题，拼在一起语义断裂 |

#### 被注入内容的编写原则

| 原则 | 说明 |
|------|------|
| 自包含 | 不依赖 SKILL.md 的上下文才能理解——注入内容可能被不同 skill 复用 |
| 有明确受众 | 开头说明"此内容用于 X 时参照"——agent 知道在什么场景下应用 |
| 不重复 SKILL.md | 不复述 SKILL.md 已有的步骤——注入的是补充信息，不是重复指令 |
| 粒度匹配 | 格式规范给结构骨架，质量标准给判断准则——不把两者混在一个文件里 |

### 检查表

| 检查项 | 通过标准 | 常见问题 |
|--------|---------|---------|
| SKILL.md 长度 | < 500 行（官方建议） | 过长 → 关键指令被稀释，agent 遗漏步骤 |
| 详细规范外置 | 格式规范、质量标准等放 references/，SKILL.md 用 markdown 链接导航 | 全部内联 → prompt 膨胀，token 浪费 |
| 引用深度 | references/ 文件直接从 SKILL.md 链接，不嵌套 | 嵌套引用 → Claude 部分读取，信息丢失 |
| 长文件有目录 | 超 100 行的 references/ 文件顶部有 Contents | Claude 预览时看不到完整范围 |
| description 长度 | 简洁有效——所有 skill 的 description 共享 context window 2% 的字符预算（fallback 16,000 chars） | description 过长挤占其他 skill 空间，或超预算后被截断 |
| 引用方式匹配 | 执行前提用 DCI 预注入，生成参考用标准引用，无关内容不提 | 该注入的只是引用 → agent 跳过；该引用的却注入 → 上下文膨胀 |
| 注入位置正确 | 内容注入在使用它的步骤之前 | agent 执行步骤时注入内容已滚出上下文窗口 |
| 每阶段各取所需 | 阶段 0 注入生成标准，阶段 2 注入产出物，不混注 | 上下文污染，agent 混淆用途 |
| 门控逻辑匹配 | 静态内容用门控跳过；动态内容绕过门控 | 运行时需要的内容被门控跳过，或探测内容每次重复注入 |
| 注入结果可验证 | 能用 `python3 include.py <args> 2>&1` 手动验证输出 | 注入为空但无错误提示，静默失败 |

## C. 编写规范

### 术语与语义

> 同一个概念用不同的词，agent 会当成不同的东西。

| 检查项 | 通过标准 | 常见问题 |
|--------|---------|---------|
| 术语一致 | 同一概念全文只用一个词（如"产出物"不混用"核心文件""输出文件"） | agent 不确定是否指同一事物，行为分裂 |
| 术语无歧义 | 每个术语只有一个含义（"规范"到底指格式规范还是质量标准？） | agent 猜错含义，执行偏离 |
| 层级关系清晰 | 区分"标准 → 产出物 → 代码"的把控链（如质量原则把控 LOG-RULES.md，LOG-RULES.md 把控日志代码） | 层级混淆导致在错误阶段注入错误内容 |
| 指代明确 | 不用"它""该文件""上述内容"等模糊指代，直接写名称 | agent 回溯上下文失败，指代错误 |
| 角色区分 | 区分"给 agent 的指令"和"给用户看的产出物"——两者措辞和详略不同 | agent 把内部指令当用户内容输出，或反过来 |

### 句式风格

> agent 对不同句式的遵从度不同。祈使句 > 陈述句 > 建议句。

| 句式 | 遵从度 | 用法 | 示例 |
|------|--------|------|------|
| 祈使句 | 最高 | 必须执行的步骤，每步以动词开头 | "用 Glob 搜索 `**/LOG-RULES.md`" |
| 条件祈使句 | 高 | 分支逻辑，`X → A，Y → B`，不用"如果觉得需要" | "文件存在 → 读取内容；不存在 → 创建" |
| 禁止句 | 高 | 红线规则，`不要 X`、`禁止 Y`，不用"尽量避免" | "不要修改 .pbxproj 文件" |
| 陈述句 | 中 | 仅提供背景信息，不期望 agent 对此采取行动 | "LOG-RULES.md 存放在 doc_dir 目录下" |
| 建议句 | 低 | 避免使用——要做就用祈使句，不做就不写 | ~~"可以考虑检查一下格式"~~ |

### 指令质量

| 检查项 | 通过标准 | 常见问题 |
|--------|---------|---------|
| 步骤具体可执行 | 每步是明确动作（"用 Glob 搜索 X"），不是模糊意图（"了解项目"） | agent 自由发挥，行为不可预测 |
| 判断标准明确 | 分支条件有具体判据（"文件存在 → A，不存在 → B"） | "如果需要" → agent 自行判断，行为不一致 |
| 输出格式定义 | 产出物有格式规范（references/*-guideline.md 或 *-template.md） | agent 每次生成不同格式 |
| 错误处理路径 | 失败场景有明确应对（重试、回退、报告） | 失败时 agent 卡住或静默跳过 |
| 正反例配对 | references/ 中的质量标准和原则文件应有正反例对比 | 只有抽象原则，agent 理解偏差 |
| 执行流程无断点 | 阶段间的数据传递显式声明（"从步骤 1 获取 X，传入步骤 2"） | agent 不知道用上一步的什么结果 |
| 入口出口明确 | 每个阶段写清前置条件和产出 | agent 跳过阶段或重复执行 |
| 不鼓励过度工程化 | 指令不含"尽可能全面""考虑所有情况"等措辞——Claude 4 模型已倾向过度扩展 | agent 自行添加未要求的功能、抽象层或防御代码 |

## D. 交互设计

| 检查项 | 通过标准 | 常见问题 |
|--------|---------|---------|
| 选项优先于打字 | AskUserQuestion 有具体选项，Other 兜底 | 让用户打字描述选择 |
| 每轮一个问题 | 不堆叠多个问题 | 用户认知负担重 |
| 先展示后执行 | 有副作用的操作先展示计划，确认后执行 | 直接改代码，用户失去控制 |
| 汇报简明 | 完成后一句话摘要 + 可选详细展开 | 大段输出淹没关键信息 |

## E. 排查流程

skill 不生效时，按此顺序排查：

| 步骤 | 排查内容 | 对应维度 |
|------|---------|---------|
| 1 | **触发** — description 是否包含用户会说的词？`disable-model-invocation` 是否误设？ | A |
| 2 | **参数** — `$ARGUMENTS` 是否在正确位置？skill 是否收到了预期参数？ | A |
| 3 | **注入** — `!include` 输出是否为空？门控是否错误跳过？用 `python3 include.py ... 2>&1` 验证 | B |
| 4 | **状态** — SKILL-STATE.md 中路径是否正确？`initialized` 是否有值？ | A |
| 5 | **上下文** — SKILL.md 是否超 500 行？关键指令是否被淹没？ | B |
| 6 | **指令** — 步骤是否具体？分支条件是否明确？术语是否一致？ | C |
| 7 | **路径** — references/ 文件路径是否正确？动态路径在 SKILL-STATE.md 中有值？ | A, B |

## F. 验证与迭代

> 官方推荐 evaluation-first approach：先在代表性任务上跑 skill，再增量改进。

| 检查项 | 通过标准 | 常见问题 |
|--------|---------|---------|
| 触发测试 | 用自然语言测试 description 触发率——换 3 种说法都能激活 | 只测了 `/skill-name` 直接调用，没测自动触发 |
| 端到端执行 | 在真实项目上完整跑一遍，验证每个阶段的产出 | 只读了 SKILL.md 觉得"应该没问题" |
| 边界场景 | 测试空项目（无 SKILL-STATE.md）、已初始化项目、异常输入 | 只在 happy path 上测试 |
| 迭代记录 | 修复的问题记录在 commit message 或 changelog 中，避免回退 | 反复调同一个问题 |

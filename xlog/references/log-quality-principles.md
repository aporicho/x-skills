# 日志质量原则

> 供 agent 生成/审查 LOG-RULES.md 时参照，不是用户文档。
> 基于行业共识：BetterStack、Swift.org（os_log 指引）、DataSet、OWASP Logging Cheat Sheet。

---

## A. 级别语义（Level Semantics）

### 精确判断标准

| 级别 | 核心问题 | 判断依据 |
|------|---------|---------|
| trace | "这行代码执行了吗？" | 仅在逐步追踪特定问题时有意义，生产环境永远关闭 |
| debug | "内部状态是什么？" | 开发/调试需要，生产不开。函数入口参数、中间计算结果、分支选择 |
| info | "系统做了什么有意义的事？" | 用户可感知的操作完成、服务启停、配置加载。正常运行时的"心跳" |
| warning | "不该发生但能继续" | 程序能自愈或降级。需要关注但不需要立即行动 |
| error | "操作失败，用户受影响" | 当前操作无法完成，需要人工干预或自动告警 |

### 边界案例指引

- **Expected failure 不是 error** — 网络超时重试、可选资源缺失、用户输入校验失败 → warning 或 debug
- **库/框架代码主要用 trace/debug** — 调用方决定是否需要可见性（Swift.org 官方指引：library code should primarily use debug and trace levels）
- **正常操作路径不用 info 以上** — 如果正常流量会产生大量 info，说明级别选高了
- **guard/precondition 失败** → warning（程序能继续）或 error（程序不能继续），不是 debug
- **catch 块** → 看影响范围：能恢复 → warning，不能恢复 → error，预期中的 → debug
- **状态机非法转换** → warning（如果忽略继续）或 error（如果中止操作）

---

## B. 消息质量（Message Quality）

### 好消息的三要素

1. **上下文（Context）** — 谁、在哪、处理什么标识符
2. **因果关系（Causality）** — 为什么走到这个分支、什么条件触发
3. **可操作性（Actionability）** — 看到这条日志后知道下一步查什么

### 正反例对比

| 原则 | 坏例子 | 好例子 |
|------|--------|--------|
| 包含标识符 | `"load failed"` | `"load failed", metadata: ["elementId": id, "source": path]` |
| 说明原因 | `"invalid state"` | `"unexpected state during save: expected .editing, got .locked"` |
| 提供恢复线索 | `"connection error"` | `"connection to sync server failed after 3 retries, will use local cache"` |
| 记录决策分支 | `"using fallback"` | `"primary renderer unavailable (metalSupported=false), falling back to CPU"` |
| 区分预期与异常 | `"file not found"` | `"optional config file not found at \(path), using defaults"` |

### 结构化 metadata 规范

- **用键值对，不用字符串拼接** — `metadata: ["id": id, "count": n]` 而非 `"id=\(id) count=\(n)"`
- **key 命名**：camelCase，具体而非通用（`elementId` 而非 `id`，`retryCount` 而非 `count`）
- **不在消息正文中换行** — 换行破坏日志聚合工具的解析，多行信息放 metadata

---

## C. 反模式清单（Anti-Patterns）

| 反模式 | 问题 | 修正 |
|--------|------|------|
| **Log and Throw** — 记了日志又抛异常 | 上层 catch 再记一次，同一个错误出现多条日志 | 选一个：底层抛、上层记。或底层用 debug、上层用 error |
| **吞掉异常信息** — 只记 message 不记完整 error | 丢失堆栈和类型信息，无法定位根因 | 始终传递完整错误对象：`Log.error("save failed", metadata: ["error": "\(error)"])` |
| **用 print 代替 Logger** | 无级别、无时间戳、无法过滤、无法关闭 | 遵循项目禁忌，使用项目规定的日志工具 |
| **级别滥用** — guard 失败用 debug、正常操作用 error | debug 在生产不可见导致问题隐藏；error 泛滥导致告警疲劳 | 按 A 节的判断标准选级别 |
| **过度日志** — 每行赋值都记 | 噪声淹没关键信息，影响性能 | 只在决策点（分支、错误、状态变化）记录 |
| **无上下文日志** — `"error occurred"` | 无法定位是哪个操作、哪个对象出了问题 | 包含标识符和状态值，见 B 节三要素 |
| **敏感信息入日志** — 密码、token、PII | 安全风险，违反隐私法规 | 永远不记录敏感数据。必要时记脱敏后的标识（如 token 末 4 位） |
| **条件检查后冗余日志** — if 检查失败后 else 里同一条信息记两次 | 重复无意义 | 只在有新信息的分支记录 |

---

## D. 生成规范时的自检清单（Self-Check for Generation）

生成或更新 LOG-RULES.md 后，逐项核对：

- [ ] **级别表判断标准具体可操作** — 不是"重要的事"这种模糊描述，而是"操作失败且用户会感知到"
- [ ] **必加位置覆盖项目实际关键路径** — FFI 边界、状态机转换、错误处理分支、异步回调入口
- [ ] **代码模式速查从项目真实代码提取** — 不是通用模板，包含项目实际的 Logger 实例和调用风格
- [ ] **禁忌条目与 CLAUDE.md 一致** — 如 CLAUDE.md 禁止 print()，LOG-RULES.md 必须包含对应禁忌
- [ ] **消息风格有正反例** — 至少覆盖：函数入口、guard 失败、错误处理、状态变化
- [ ] **Logger 列表完整且有用途说明** — 每个 Logger 实例标明适用场景，避免选错
- [ ] **级别速判表与详细判断标准一致** — 速判是缩写不是另一套标准

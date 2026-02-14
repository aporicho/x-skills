# LOG-RULES.md 规范

## 生成方式

从项目代码中提取（不是凭空编），包含以下内容：

```markdown
# LOG RULES

> 由 /xlog skill 基于代码扫描生成，可手动调整

更新时间：YYYY-MM-DD

## 日志工具

[描述项目使用的日志库/框架，如 swift-log、log crate、console 等]

## Logger 列表

| Logger | 用途 | 示例 |
|--------|------|------|
| [从代码中提取的 Logger 实例列表] |

## 级别使用

| 级别 | 判断标准 |
|------|---------|
| trace | 只有刻意调查某个具体问题时才需要看到 |
| debug | 开发时想看到，生产环境不需要 |
| info | 用户完成了一个有意义的操作 |
| warning | 不该发生但程序能继续运行 |
| error | 操作失败，用户会感知到 |

速判：guard 失败 → warning；catch/Err → error；函数入口 → debug；重要操作完成 → info

## 必须加日志的位置

- 有副作用的公共函数入口 — 参数摘要
- guard/if-let/Optional 失败的 else 分支 — 为什么失败
- match/switch 的 default/unexpected 分支 — 不该走到这里
- catch / Err / error 分支 — 错误详情
- 状态机转换 — from → to
- FFI / API 边界 — 参数校验、返回值
- 异步回调入口 — 回调是否被执行、参数

## 不该加日志的位置

- 纯计算函数（无分支、无副作用）
- 简单 getter/setter
- 循环体内每次迭代（除非用 trace）
- 已有充足日志的函数

## 消息风格

[从代码中提取：消息语言、metadata key 命名规范]

## 代码模式速查

[从代码中提取：每种语言的日志调用示例，覆盖函数入口、guard 失败、错误处理、状态变化等场景]

## 项目禁忌

[从 CLAUDE.md 提取：如禁止 print()、禁止特定日志方式等]
```

## 更新时机

- 项目新增 Logger 实例时
- 日志工具或风格发生变化时
- 用户手动调整后以用户版本为准

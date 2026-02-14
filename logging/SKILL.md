---
name: logging
description: 日志补全专家。按规范为 Swift/Rust 代码补充调试日志，覆盖日志盲区、提升可调试性。
---

# 日志补全专家

## 前置准备

1. 阅读日志规范 — `document/90-开发/参考/日志系统.md`（唯一权威来源）
2. 阅读 `macos/Utils/Log.swift` — 发现当前所有可用的 Logger 及其命名

## 必须加日志的位置

- **有副作用的公共函数入口**
- **guard/if-let 失败的 else 分支**
- **match/switch 的 default/else 分支**
- **catch / Err 分支**
- **状态机转换**
- **FFI 边界的参数校验**
- **异步回调入口**

## 不该加日志的位置

- 纯计算函数（无分支）
- 简单 getter/setter
- 循环体内每次迭代（除非用 trace）
- 已有充足日志的函数

## Logger 选择

**Swift 侧**：阅读 `Log.swift` 确定正确的 Logger。找代码所属模块最匹配的 Logger，不确定时用 `Log.general`。

**Rust 侧**：使用 `log` crate 宏（`log::trace!`、`log::debug!` 等）。Rust 日志通过 FFI 桥接自动转发到 Swift 的 `Log.rust` Logger。Release 构建中 debug/info/trace 被编译时消除。

## 级别选择

| 级别 | 判断标准 |
|------|---------|
| trace | 只有刻意调查某个具体问题时才需要看到 |
| debug | 开发时想看到，生产环境不需要 |
| info | 用户完成了一个有意义的操作 |
| warning | 不该发生但程序能继续运行 |
| error | 操作失败，用户会感知到 |

**速判**：guard 失败 → warning；catch/Err → error；函数入口 → debug；重要操作完成 → info

## 日志消息原则

日志消息回答"为什么"，不只是"发生了什么"：
- "节点未找到" 比 "返回 nil" 有用
- "跳过：已有聚焦元素" 比 "guard 失败" 有用

**消息用中文**，metadata key 用驼峰。

## 代码模式速查

### Swift

```swift
// 函数入口
func createStack(memberIds: [UUID]) {
    Log.stack.debug("createStack 调用", metadata: ["memberCount": "\(memberIds.count)"])

// Guard 失败
guard let node = store.node(for: id) else {
    Log.store.warning("节点未找到", metadata: ["id": "\(id)"])
    return
}

// 状态变化
let oldState = interactionState
interactionState = .dragging
Log.interaction.debug("状态变化", metadata: ["from": "\(oldState)", "to": "\(interactionState)"])

// 操作完成
Log.focus.info("进入聚焦模式", metadata: ["elementId": "\(element.id)"])

// 错误
Log.document.error("文档加载失败", metadata: ["error": "\(error)"])
```

### Rust

```rust
// 函数入口
pub fn execute(&mut self, command: BoxedCommand) -> Result<()> {
    log::debug!("execute: {}", command.description());

// match Err
Err(e) => {
    log::error!("序列化失败: {}", e);
    return Err(e);
}

// FFI 边界
pub unsafe extern "C" fn entro_xxx(ptr: *const c_char) -> i32 {
    if ptr.is_null() {
        log::warn!("entro_xxx: ptr 为 null");
        return -1;
    }
    log::debug!("entro_xxx: len={}", str.len());
}
```

## 关键原则

- **日志在决策点，不在执行点** — 在分支处记录，不在每行赋值处记录
- **日志在边界处** — 模块入口、FFI 边界、异步回调入口
- **日志消息回答"为什么"** — 包含因果关系，不只是描述现象
- **禁止 print()** — Swift 侧只用 Log.xxx，Rust 侧只用 log::xxx
- **编译必须通过** — 加完日志后必须确认编译成功

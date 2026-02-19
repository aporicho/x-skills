14 项项目信息，探测得到的属性，只读不创建，写入 SKILL-STATE.md。

按清单逐项探测，同一数据源的项归为一次操作，互不依赖的并行执行。

**A.1 项目身份**

A1 项目类型
- 简介: GUI 应用 / CLI 工具 / Web 服务 / 库。决定是否需要启动脚本、手动测试等
- 探测方式: 标志文件扫描（*.xcodeproj → GUI, Cargo.toml + main → CLI, package.json + dev → Web）

A2 CLAUDE.md 路径
- 简介: 项目指令文件的实际位置，部分项目可能不在根目录
- 探测方式: 扫描根目录 + .claude/

**A.2 构建与运行**

A3 构建命令
- 简介: 编译项目的完整命令，调试和测试前必须先构建成功
- 探测方式: CLAUDE.md 优先，否则从构建配置推导
- 使用者: xdebug, xtest, xlog

A4 测试命令
- 简介: 运行自动化测试的命令
- 探测方式: CLAUDE.md 优先，否则从构建系统推导
- 使用者: xtest

A5 启动方式
- 简介: 如何后台运行项目供手动测试
- 探测方式: CLAUDE.md + 构建系统推导
- 使用者: xdebug, xtest

A6 停止方式
- 简介: 如何停止运行中的项目
- 探测方式: 与启动方式对应推导
- 使用者: xdebug, xtest

**A.3 日志体系**

A7 日志框架
- 简介: 项目使用的日志工具（os.Logger / log crate / console 等）
- 探测方式: 代码中 import/use 语句 + CLAUDE.md
- 使用者: xlog

A8 日志输出位置
- 简介: 运行时日志去向（stdout / 文件 / 控制台）
- 探测方式: CLAUDE.md + 日志框架配置
- 使用者: xdebug, xtest

**A.4 目录与环境**

A9 文档目录
- 简介: 所有核心文件的统一存放位置（output_dir）
- 探测方式: 扫描 document/、docs/、doc/，未找到则记录"待创建 docs/"（不在此处创建）
- 使用者: 全部

A10 脚本目录
- 简介: 项目已有的脚本存放位置，run.sh 等放这里
- 探测方式: 目录扫描
- 使用者: xdebug, xtest

A11 .gitignore 状态
- 简介: 核心文件是否已被 gitignore
- 探测方式: 读 .gitignore 检查相关模式
- 使用者: xbase

A12 预检脚本
- 简介: 已有的 lint/format/check 脚本，提交前自动运行
- 探测方式: 扫描 scripts/ + package.json + Makefile
- 使用者: xcommit

**A.5 项目规范**

A13 Commit 风格
- 简介: 已有的 git 提交消息风格（语言、前缀、长度）
- 探测方式: git log --oneline -20 分析
- 使用者: xcommit

A14 编码规范/禁忌
- 简介: CLAUDE.md 中声明的规范和禁止事项
- 探测方式: 读 CLAUDE.md 提取规则列表
- 使用者: xreview, xcommit, xlog

**写入结果**

如 A9 未找到文档目录，在写入前先创建 `docs/`：
```bash
mkdir -p docs
```

```bash
python3 .claude/skills/xbase/scripts/skill-state.py write-info output_dir "<文档目录路径>"
```

> 其余探测结果（类型、构建命令、启动方式等）由各 skill 初始化时自行消费，写入各自的产出物文件（COMMIT-RULES.md、LOG-RULES.md 等），不存入 SKILL-STATE.md。

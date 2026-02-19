# xdebug 核心文件

## DEBUG-LOG.md（记录类）

- 简介: Bug 修复日志，记录每次修复的症状→根因→解决方案
- 搜索策略: 文件名含 debug, bug, 修复记录
- 格式规范: `references/debug-log-format.md`
- 状态字段: `debug_log`

## run.sh（工具类）

- 简介: 调试运行脚本，封装构建+后台启动+日志捕获+停止四个命令
- 搜索策略: 脚本目录中含 build/run/start 的 .sh
- 格式规范: `../xbase/references/infra-setup.md`
- 状态字段: 写入项目信息的 `运行脚本`

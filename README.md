# W1ndys-bot

基于 Python 和 NapCatQQ 的机器人实现

## 开发文档

NapCatQQ [NapCatQQ (napneko.github.io)](https://napneko.github.io/zh-CN/#/)

OneBot 11 标准 [botuniverse /onebot-11: OneBot 11 标准 (github.com)](https://github.com/botuniverse/onebot-11#/)

go-cqhttp [API | go-cqhttp 帮助中心](https://docs.go-cqhttp.org/api/)

> 备注：本机器人实现基于 **Python** 做核心开发，使用 **NapCatQQ** 作为消息平台，**OneBot 11** 作为 QQ 机器人 API 实现。

## 已实现功能

- [x] 收发消息
- [x] 敏感词监控
  - [x] 指定开启群聊
  - [x] 自定义敏感词库
- [x] 禁言解禁
- [x] 踢人
- [x] 测试语句
- [ ] 监控群名片
- [ ] 入群欢迎
- [ ] 退群欢送
- [ ] 邀请链检索
- [x] 全员禁言
- [x] 全员解禁
- [x] 关键词回复（可存换行符）
- [ ] 宵禁
- [x] QQ 内部实现 API 调用

## 使用手册

### 群管

> 群管功能的使用者需要程序管理员权限（并非群内管理员），且机器人账号需要在群内是群主或群管理员。

`全员禁言|ban-all`：全员禁言

`全员解禁|unban-all`：全员解禁

`ban+@某人+数字`：禁言指定用户指定分钟 (数字可省略，默认为 1 分钟)

`unban+@某人`：解禁指定用户

`kick|踢|t@某人`：踢出指定用户，例如：`t@某人`、`踢@某人`、`kick@某人`

`撤回|recall`：撤回一条消息，需要撤回哪条消息就把命令回复给这条消息

敏感词监控，群内指定开启，自定义敏感词库，群内发送包含敏感词的消息会被自动禁言并撤回并发送警告消息。

### QQ 内部 API 调用

API 参考文档：[botuniverse /onebot-11: OneBot 11 标准 (github.com)](https://github.com/botuniverse/onebot-11#/)

正向 WebSocket 连接参考文档：[onebot-11/communication/ws.md at master · botuniverse/onebot-11 (github.com)](https://github.com/botuniverse/onebot-11/blob/master/communication/ws.md)

使用方法：

1. 修改代码中的 QQ（`if user_id == 2769731875:  # 机器人管理员`）改成你的 QQ
1. 私聊机器人发送 `执行+要执行的语句json`
1. 例如 `执行{"action": "send_private_msg", "params": {"user_id": 2769731875, "message": "如果机器人回复这条消息，代表成功了\n换行内容测试"}}`
1. 机器人会回复你 `如果机器人回复这条消息，代表成功了\n换行内容测试`（在实际回复中这里\n 是换行）

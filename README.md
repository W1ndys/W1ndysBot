# W1ndys-bot

基于 Python 和 NapCatQQ 的机器人实现

## 开发文档

[NapCatQQ (napneko.github.io)](https://napneko.github.io/zh-CN/#/)

[botuniverse /onebot-11: OneBot 11 标准 (github.com)](https://github.com/botuniverse/onebot-11#/)

[API | go-cqhttp 帮助中心](https://docs.go-cqhttp.org/api/)

## 已实现功能

- [x] 收发消息
- [x] 敏感词监控
  - [x] 指定开启群聊
  - [x] 自定义敏感词库
- [x] 禁言解禁
- [x] 踢人
- [ ] 测试语句
- [ ] 监控群名片
- [ ] 入群欢迎
- [ ] 退群欢送
- [ ] 邀请链检索
- [x] 全员禁言
- [x] 全员解禁
- [ ] 宵禁

## 使用手册

### 群管

`全员禁言|ban-all`：全员禁言

`全员解禁|unban-all`：全员解禁

`ban+@某人+数字`：禁言指定用户指定分钟 (数字可省略，默认为 1 分钟)

`kick|踢|t@某人`：踢出指定用户，例如：`t@某人`、`踢@某人`、`kick@某人`

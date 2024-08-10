# W1ndys-bot

基于 Python 和 OneBot 11 的 QQ 机器人实现

W1ndys 开发的 QQ 机器人，励志成为功能丰富，使用方便的 QQ 机器人。

## 开发文档

NapCatQQ [NapCatQQ (napneko.github.io)](https://napneko.github.io/zh-CN/#/)

OneBot 11 标准 [botuniverse /onebot-11: OneBot 11 标准 (github.com)](https://github.com/botuniverse/onebot-11#/)

go-cqhttp [API | go-cqhttp 帮助中心](https://docs.go-cqhttp.org/api/)

> 备注：本机器人实现基于 **Python** 做核心开发，使用 **NapCatQQ** 作为消息平台，**OneBot 11** 作为 QQ 机器人 API 实现。

## 已实现功能

### 系统

- [x] 机器人连接成功通知到 root 管理员 QQ
- [x] 机器人断开通知到钉钉
- [x] 机器人断线自动重连
- [ ] 菜单

### 群管系统

- [x] 禁言
- [x] 禁言自己
- [x] 禁言指定用户
- [x] 禁言随机用户
- [x] 禁言指定用户指定秒
- [x] 禁言随机用户随机秒
- [x] 解禁
- [x] 踢人
- [x] 撤回消息
- [x] 撤回指定消息
- [x] 扫描邀请链
- [x] 添加违禁词
- [x] 移除违禁词
- [x] 列出违禁词
- [x] 启用违禁词检测
- [x] 禁用违禁词检测
- [x] 启用入群欢迎信息
- [x] 禁用入群欢迎信息
- [x] 启用邀请链功能
- [x] 禁用邀请链功能
- [x] 查看邀请链

### 黑名单系统

- [x] 添加黑名单
- [x] 删除黑名单
- [x] 列出黑名单
- [x] 禁用黑名单
- [x] 启用黑名单

### 知识库问答系统

- [x] 开启知识库
- [x] 关闭知识库
- [x] 添加知识库
- [x] 删除知识库某关键词下的某个问题
- [x] 删除知识库关键词下所有问题
- [x] 无效命令提示
- [x] 关键词识别
- [x] 问题识别

### Crypto

编解码系统

- [x] 支持私聊编解码
- [x] 支持群聊编解码
- [x] base64 编解码
- [x] MD5 编码
- [x] 进制转换
- [x] hash 计算
- [x] 密码生成

### Tools

- [ ] IP 地址查询
- [x] 快递查询

### 计划中的系统

- 词云统计

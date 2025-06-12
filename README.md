# 🤖 W1ndysBot

![GitHub stars](https://img.shields.io/github/stars/W1ndys/W1ndysBot?style=flat-square)
![GitHub forks](https://img.shields.io/github/forks/W1ndys/W1ndysBot?style=flat-square)
![GitHub issues](https://img.shields.io/github/issues/W1ndys/W1ndysBot?style=flat-square)
![GitHub license](https://img.shields.io/github/license/W1ndys/W1ndysBot?style=flat-square)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/W1ndys/W1ndysBot)

W1ndysBot，一款基于 NapCat 和 Python 开发的机器人程序，基于[W1ndysBotFrame](https://github.com/W1ndysBot/W1ndysBotFrame) 开发。

## ✨ 功能说明

- 🧩 含[W1ndysBotFrame](https://github.com/W1ndysBot/W1ndysBotFrame) 所有系统功能
- 🚫 黑名单系统，支持拉黑、解黑、查看黑名单、清空黑名单，新入群或发言时检测黑名单
- 🛡️ 基础群管功能，支持群禁言、解禁、踢出、全员禁言、全员解禁、撤回消息等
- 🔄 刷屏检测，支持检测用户 1 秒内发送的消息数量是否超过 5 条或存在连续重复的消息
- 🌳 邀请树记录，支持记录用户邀请用户，便于发现异常后梳理上下级关系
- 📚 FAQ 问答对系统，支持添加、删除、查看、修改 FAQ

## ⚙️ 配置说明

在 `app/.env` 中配置:

- `OWNER_ID`: 机器人管理员 QQ 号
- `WS_URL`: WebSocket 连接地址
- `TOKEN`: 认证 token(可选)
- `FEISHU_BOT_URL`: 飞书机器人 URL(可选)
- `FEISHU_BOT_SECRET`: 飞书机器人 Secret(可选)

## 更新方法

克隆新版本，覆盖原文件，重新运行即可

（注意备份好数据、日志、配置文件、自己开发的功能等，建议使用 git 管理，或复制新目录再覆盖）

```bash
git clone https://github.com/W1ndys/W1ndysBot.git
```

## 🌟 星标历史

[![Star History Chart](https://api.star-history.com/svg?repos=W1ndys/W1ndysBot&type=Date)](https://star-history.com/#W1ndys/W1ndysBot&Date)

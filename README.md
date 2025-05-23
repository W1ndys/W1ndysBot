# 🤖 W1ndysBotFrame

![GitHub stars](https://img.shields.io/github/stars/W1ndysBot/W1ndysBotFrame?style=flat-square)
![GitHub forks](https://img.shields.io/github/forks/W1ndysBot/W1ndysBotFrame?style=flat-square)
![GitHub issues](https://img.shields.io/github/issues/W1ndysBot/W1ndysBotFrame?style=flat-square)
![GitHub license](https://img.shields.io/github/license/W1ndysBot/W1ndysBotFrame?style=flat-square)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/W1ndysBot/W1ndysBotFrame)

W1ndysBotFrame，一款基于 NapCat 和 Python 开发的机器人程序。

本项目已发布 3.0 版本，经过了彻底重构，欢迎使用！如有任何问题，请提交 issue 或联系作者

## 📁 项目结构

```
app/
├── api/                    # API 接口模块
│   ├── user.py            # 用户相关接口
│   ├── message.py         # 消息处理接口
│   ├── generate.py        # 生成相关接口
│   └── group.py           # 群组管理接口
├── core/                   # 核心功能模块
│   ├── auth.py            # 权限认证
│   ├── del_self_msg.py # 自动撤回自己发送的消息
│   ├── online_detect.py   # 在线检测
│   └── switchs.py         # 开关管理
├── modules/               # 模块目录
│   └── template/          # 模板模块
│       ├── main.py              # 主程序入口
│       ├── handle_message.py   # 消息处理器
│       ├── handle_notice.py    # 通知处理器
│       ├── handle_request.py   # 请求处理器
│       ├── handle_response.py  # 响应处理器
│       └── README.md           # 说明文档
├── utils/                   # 工具函数模块
│   ├── feishu.py            # 飞书集成
│   └── logs_clean.py        # 日志清理
├── bot.py                 # 机器人主程序
├── handle_events.py      # 事件处理器
├── main.py               # 程序入口
├── logger.py             # 日志系统
└── config.py             # 配置文件
```

## 流程图

在这里->[流程图](./docs/flow_diagram.md)

## ✨ 功能说明

- ❤️ 每次心跳检测机器人是否在线
- 📢 支持掉线后自动发送通知到飞书
- 🔌 模块动态加载，无需侵入式修改代码
- 🔒 每个群可以单独控制功能的开启/关闭
- 🔐 每个私聊功能可以单独控制功能的开启/关闭
- ⏰ 支持定时任务
- 🔄 支持自动撤回自己发送的消息
- 📨 支持私聊转达到`OWNER`管理员
- 📝 支持日志记录和查询
- 🧩 功能模块可以独立开发和管理

## 🛠️ 开发说明

- 新功能开发请参考 `app/modules/template` 目录的示例
- 数据存储请在 `app/data` 下创建对应目录
- 如需定时撤回消息，请在[发送消息 API](https://github.com/W1ndysBot/W1ndysBotFrame/blob/main/app/api/message.py) 的`note`参数中传入`del_msg_秒数_消息ID`，例如`del_msg_10_1234567890`

## ⚙️ 配置说明

在 `app/config.py` 中配置:

- `OWNER_ID`: 机器人管理员 QQ 号
- `WS_URL`: WebSocket 连接地址
- `TOKEN`: 认证 token(可选)
- `FEISHU_BOT_URL`: 飞书机器人 URL(可选)
- `FEISHU_BOT_SECRET`: 飞书机器人 Secret(可选)

## 更新方法

克隆新版本，覆盖原文件，重新运行即可

（注意备份好数据、日志、配置文件、自己开发的功能等，建议使用 git 管理，或复制新目录再覆盖）

```bash
git clone https://github.com/W1ndysBot/W1ndysBotFrame.git
```

## 🌟 星标历史

[![Star History Chart](https://api.star-history.com/svg?repos=W1ndysBot/W1ndysBotFrame&type=Date)](https://star-history.com/#W1ndysBot/W1ndysBotFrame&Date)

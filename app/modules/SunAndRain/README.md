# Template 功能模块

模板模块是 W1ndysBotFrame 框架中用于快速创建新功能模块的基础结构。通过复制和修改此模板，开发者可以方便地实现自己的功能模块，无需从零开始编写代码结构。

## 模块文件结构

```
template/
├── __init__.py              # 模块初始化文件，定义模块基本信息
├── main.py                 # 模块主入口，处理事件分发
├── handle_message.py       # 消息处理主类
│   ├── handle_message_group.py    # 群聊消息处理类
│   └── handle_message_private.py  # 私聊消息处理类
├── handle_notice.py        # 通知事件处理主类
│   ├── handle_notice_friend.py    # 好友通知处理类
│   └── handle_notice_group.py     # 群组通知处理类
├── handle_request.py       # 请求事件处理类
├── handle_response.py      # 响应事件处理类
├── handle_meta_event.py    # 元事件处理类
└── README.md               # 模块说明文档
```

## 开发指南

### 1. 基本设置

在 **__init__.py** 中设置模块基本信息:

```python
# 修改模块名称和描述
MODULE_NAME = "your_module_name"
MODULE_DESCRIPTION = "你的模块描述"

# 可以添加自定义命令常量
COMMANDS1 = "命令1"
COMMANDS2 = "命令2"
```

### 2. 消息处理

- **群聊消息处理**：在 handle_message_group.py 的 `handle` 方法中实现功能
- **私聊消息处理**：在 handle_message_private.py 的 `handle` 方法中实现功能

### 3. 通知事件处理

- **好友通知处理**：在 handle_notice_friend.py 中实现各类好友通知处理方法
- **群组通知处理**：在 handle_notice_group.py 中实现各类群组通知处理方法

### 4. 请求与元事件处理

- **请求处理**：在 handle_request.py 中处理好友请求和群组请求
- **元事件处理**：在 handle_meta_event.py 中处理心跳等元事件，可实现定时任务

## 开关机制

模板模块已内置群聊和私聊的开关机制：

- 在群聊中发送 `模块名称` 可切换该群的模块开关状态
- 在私聊中发送 `模块名称` 可切换私聊的模块开关状态

## 使用示例

1. 复制模板目录并重命名
2. 修改 **__init__.py** 中的模块名称和描述
3. 在相应的处理器中实现你的功能逻辑
4. 在 handle_events.py 中注册你的新模块

## 注意事项

- 各处理器已实现异常捕获，确保单一功能的错误不会影响整个模块运行
- 使用 `logger` 进行日志记录，方便调试和问题排查
- 模块开关状态保存在 `data/模块名/switch.json` 文件中

更多详细文档请参考 流程图 和项目 README。

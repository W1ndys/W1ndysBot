## Template 功能模块

Template 是一个模板模块，用于快速创建新的功能模块。

## 模块结构

```
template
├── __init__.py # 模块初始化文件
├── handle_message.py # 消息处理类
├── handle_notice.py # 通知处理类
├── handle_request.py # 请求处理类
├── handle_meta_event.py # 元事件处理类
└── main.py # 主函数入口
```

## 开发流程

开发新的类函数，继承已有的类函数，并调用已有的类函数。

在 `__init__.py` 中定义模块名称、描述等。

在 `handle_message.py` 中实现消息处理逻辑。

在 `handle_notice.py` 中实现通知处理逻辑。

在 `handle_request.py` 中实现请求处理逻辑。

在 `handle_meta_event.py` 中实现元事件处理逻辑。

在项目根目录的`app/handle_events.py`中注册新的模块。

import json
import asyncio
import logger
import os
import importlib
import inspect
from datetime import datetime

# 核心模块列表 - 这些模块将始终被加载
# 格式: ("模块路径", "模块中的函数名")
# 请不要修改这些模块，除非你知道你在做什么
CORE_MODULES = [
    # 系统工具
    ("utils.clean_logs", "clean_logs"),  # 日志清理
    # 核心功能
    ("core.online_detect", "handle_events"),  # 在线监测
    ("core.del_self_msg", "handle_events"),  # 自动撤回自己发送的消息
    ("core.nc_get_rkey", "handle_events"),  # 自动刷新rkey
    # 在这里添加其他必须加载的核心模块
]


class EventHandler:
    def __init__(self):
        self.handlers = []

        # 加载核心模块（固定加载）
        self._load_core_modules()

        # 动态加载modules目录下的所有模块
        self._load_modules_dynamically()

        # 记录已加载的模块数量
        logger.success(f"总共加载了 {len(self.handlers)} 个事件处理器")

    def _load_core_modules(self):
        """加载核心模块"""
        for module_path, handler_name in CORE_MODULES:
            try:
                module = importlib.import_module(module_path)
                handler = getattr(module, handler_name)
                self.handlers.append(handler)
                logger.success(f"已加载核心模块: {module_path}.{handler_name}")
            except Exception as e:
                logger.error(
                    f"加载核心模块失败: {module_path}.{handler_name}, 错误: {e}"
                )

    def _load_modules_dynamically(self):
        """动态加载modules目录下的所有模块"""
        modules_dir = os.path.join(os.path.dirname(__file__), "modules")
        if not os.path.exists(modules_dir):
            logger.warning(f"模块目录不存在: {modules_dir}")
            return

        # 遍历模块目录
        for module_name in os.listdir(modules_dir):
            module_path = os.path.join(modules_dir, module_name)

            # 跳过非目录和以下划线开头的目录
            if not os.path.isdir(module_path) or module_name.startswith("_"):
                continue

            # 检查模块是否有main.py文件
            main_file = os.path.join(module_path, "main.py")
            if not os.path.exists(main_file):
                logger.warning(f"模块 {module_name} 缺少main.py文件，已跳过")
                continue

            try:
                # 动态导入模块
                module_import_path = f"modules.{module_name}.main"
                module = importlib.import_module(module_import_path)

                # 检查模块是否有handle_events函数
                if hasattr(module, "handle_events") and inspect.iscoroutinefunction(
                    module.handle_events
                ):
                    self.handlers.append(module.handle_events)
                    logger.success(f"已加载模块: {module_name}")
                else:
                    logger.warning(
                        f"模块 {module_name} 缺少异步handle_events函数，已跳过"
                    )
            except Exception as e:
                logger.error(f"加载模块失败: {module_name}, 错误: {e}")

    async def _safe_handle(self, handler, websocket, msg):
        try:
            await handler(websocket, msg)
        except Exception as e:
            logger.error(f"模块 {handler} 处理消息时出错: {e}")

    def format_napcat_msg(self, msg):
        """美化napcat日志"""
        time = msg.get("time", "未知时间戳")
        post_type = msg.get("post_type", "未知消息类型")
        format_msg = f"时间戳: {time} | 事件类型: {post_type}"

        # 元事件
        if post_type == "meta_event":
            meta_event_type = msg.get("meta_event_type")
            if meta_event_type is not None:
                format_msg += f" | 元事件类型: {meta_event_type}"
            sub_type = msg.get("sub_type")
            if sub_type is not None:
                format_msg += f" | 子事件类型: {sub_type}"

        # 消息事件
        elif post_type == "message":
            message_type = msg.get("message_type")
            if message_type is not None:
                format_msg += f" | 消息类型: {message_type}"
            sub_type = msg.get("sub_type")
            if sub_type is not None:
                format_msg += f" | 子消息类型: {sub_type}"
            sender = msg.get("sender", {})
            sender_id = sender.get("user_id")
            if sender_id is not None:
                format_msg += f" | 发送者ID: {sender_id}"
            sender_nickname = sender.get("nickname")
            if sender_nickname is not None:
                format_msg += f" | 发送者昵称: {sender_nickname}"
            sender_card = sender.get("card")
            if sender_card is not None:
                format_msg += f" | 发送者名片: {sender_card}"
            sender_level = sender.get("level")
            if sender_level is not None:
                format_msg += f" | 发送者等级: {sender_level}"
            sender_role = sender.get("role")
            if sender_role is not None:
                format_msg += f" | 发送者身份: {sender_role}"
            sender_title = sender.get("title")
            if sender_title is not None:
                format_msg += f" | 发送者头衔: {sender_title}"
            sender_avatar = sender.get("avatar")
            if sender_avatar is not None:
                format_msg += f" | 发送者头像: {sender_avatar}"
            sender_age = sender.get("age")
            if sender_age is not None:
                format_msg += f" | 发送者年龄: {sender_age}"
            message_id = msg.get("message_id")
            if message_id is not None:
                format_msg += f" | 消息ID: {message_id}"
            raw_message = msg.get("raw_message")
            if raw_message is not None:
                format_msg += f" | 原消息内容: {raw_message}"

        return format_msg

    async def handle_message(self, websocket, message):
        """处理websocket消息"""
        try:
            msg = json.loads(message)

            logger.debug(f"接收到websocket消息: {msg}")
            # 美化napcat日志
            formatted_msg = self.format_napcat_msg(msg)
            logger.napcat(f"{formatted_msg}")

            # 每个 handler 独立异步后台处理
            for handler in self.handlers:
                asyncio.create_task(self._safe_handle(handler, websocket, msg))

        except Exception as e:
            logger.error(f"处理websocket消息的逻辑错误: {e}")

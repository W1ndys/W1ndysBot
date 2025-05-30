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

    def format_event_log(self, msg):
        """根据不同消息事件格式化日志

        Args:
            msg (dict): 消息事件数据

        Returns:
            str: 格式化后的日志字符串
        """
        try:
            time = msg.get("time", "unknown")
            post_type = msg.get("post_type", "unknown")
            status = msg.get("status", "")

            log_message = f"时间戳: {time} | "

            # 根据不同的post_type处理
            if post_type == "message":
                # https://napneko.github.io/develop/event#message-%E4%BA%8B%E4%BB%B6

                # 消息类型事件
                msg_type = msg.get("message_type", "unknown")  # 消息类型
                sub_type = msg.get("sub_type", "unknown")  # 子类型
                msg_id = msg.get("message_id", "unknown")  # 消息ID
                user_id = msg.get("user_id", "unknown")  # 发送者ID
                raw_message = msg.get("raw_message", "")  # 原始消息

                # 获取发送者信息
                sender_info = ""
                sender = msg.get("sender", {})
                if sender:
                    nickname = sender.get("nickname", "")
                    card = sender.get("card", "")  # 群名片
                    display_name = card if card else nickname

                    if msg_type == "private":
                        sender_info = f"发送者: {display_name}({user_id})"
                    elif msg_type == "group":
                        role = sender.get("role", "")  # 群身份
                        role_info = f", 身份: {role}" if role else ""
                        sender_info = f"发送者: {display_name}({user_id}){role_info}"

                # 根据消息类型构建日志
                if msg_type == "private":
                    log_message += f"[私聊消息] 类型: {sub_type} | {sender_info} | 消息内容: {raw_message}"
                elif msg_type == "group":
                    group_id = msg.get("group_id", "unknown")
                    log_message += f"[群消息] 类型: {sub_type} | 群号: {group_id} | {sender_info} | 消息内容: {raw_message}"
                else:
                    log_message += f"[未知消息] 消息类型: {msg_type} | 子类型: {sub_type} | 消息内容: {raw_message}"

                return log_message

            if post_type == "message_sent":
                # 消息发送事件
                msg_type = msg.get("message_type", "unknown")
                sub_type = msg.get("sub_type", "unknown")
                msg_id = msg.get("message_id", "unknown")

                # 处理消息内容
                raw_message = msg.get("raw_message", "")
                message = msg.get("message", "")
                content = raw_message if raw_message else message

                # 根据消息类型构建日志
                if msg_type == "private":
                    target_id = msg.get(
                        "target_id", msg.get("user_id", "unknown"))
                    log_message += f"[发送私聊] 类型: {sub_type} | 目标: {target_id} | 消息ID: {msg_id} | 内容: {content}"
                elif msg_type == "group":
                    group_id = msg.get("group_id", "unknown")
                    log_message += f"[发送群消息] 类型: {sub_type} | 群号: {group_id} | 消息ID: {msg_id} | 内容: {content}"
                else:
                    log_message += f"[发送未知消息] 消息类型: {msg_type} | 子类型: {sub_type} | 消息ID: {msg_id} | 内容: {content}"

                return log_message

            if post_type == "notice":
                # 通知事件
                # group_upload, group_admin, etc.
                notice_type = msg.get("notice_type", "unknown")
                # set, unset, ban, etc.
                sub_type = msg.get("sub_type", "unknown")
                user_id = msg.get("user_id", "unknown")

                # 操作者信息
                operator_info = ""
                operator_id = msg.get("operator_id", "")
                if operator_id and operator_id != user_id:
                    operator_info = f", 操作者: {operator_id}"

                # 群组相关信息
                group_info = ""
                group_id = msg.get("group_id", "")
                if group_id:
                    group_info = f", 群组: {group_id}"

                # 特定通知类型的额外信息
                extra_info = ""
                if notice_type == "group_ban":
                    duration = msg.get("duration", 0)
                    if duration:
                        extra_info = f", 禁言时长: {duration}秒"
                elif notice_type == "group_recall" or notice_type == "friend_recall":
                    msg_id = msg.get("message_id", "")
                    if msg_id:
                        extra_info = f", 消息ID: {msg_id}"
                elif notice_type == "group_upload":
                    file = msg.get("file", {})
                    if file:
                        file_name = file.get("name", "")
                        if file_name:
                            extra_info = f", 文件: {file_name}"

                log_message += f"[通知] 类型: {notice_type} | 子类型: {sub_type} | 用户: {user_id}{group_info}{operator_info}{extra_info}"

                return log_message

            if post_type == "request":
                # 请求事件
                request_type = msg.get(
                    "request_type", "unknown")  # friend, group
                # add, invite
                sub_type = msg.get("sub_type", "unknown")
                user_id = msg.get("user_id", "unknown")
                comment = msg.get("comment", "")

                # 请求标识
                flag_info = ""
                flag = msg.get("flag", "")
                if flag:
                    flag_info = f", 请求标识: {flag}"

                # 群组信息
                group_info = ""
                if request_type == "group":
                    group_id = msg.get("group_id", "")
                    if group_id:
                        group_info = f", 群组: {group_id}"

                log_message += f"[请求] 类型: {request_type} | 子类型: {sub_type} | 用户: {user_id}{group_info}{flag_info}, 备注: {comment}"

            if post_type == "meta_event":
                # 元事件
                # heartbeat, lifecycle
                meta_type = msg.get("meta_event_type", "unknown")
                # connect, enable, etc.
                sub_type = msg.get("sub_type", "unknown")

                # 心跳事件特有字段
                extra_info = ""
                if meta_type == "heartbeat":
                    status = msg.get("status", {})
                    if status:
                        online = status.get("online", False)
                        good = status.get("good", False)
                        stat_str = "在线" if online else "离线"
                        stat_str += ", 状态良好" if good else ", 状态异常"
                        extra_info = f", 状态: {stat_str}"

                        # 统计信息
                        stat = status.get("stat", {})
                        if stat:
                            packet_received = stat.get("packet_received", 0)
                            packet_sent = stat.get("packet_sent", 0)
                            extra_info += (
                                f", 收包: {packet_received}, 发包: {packet_sent}"
                            )

                log_message += (
                    f"[元事件] 类型: {meta_type} | 子类型: {sub_type}{extra_info}"
                )
                return log_message

            if status:
                log_message = f"[返回消息]: 状态：{status} | echo: {msg.get('echo', 'unknown')} | 返回内容：{msg.get('data', 'unknown')}"
                return log_message

        except Exception as e:
            return f"日志格式化错误: {e}, 原始数据: {msg}"

    async def handle_message(self, websocket, message):
        """处理websocket消息"""
        try:
            msg = json.loads(message)
            logger.debug(f"接收到消息: {msg}")
            event_log = self.format_event_log(msg)
            logger.napcat(event_log)

            # 每个 handler 独立异步后台处理
            for handler in self.handlers:
                asyncio.create_task(self._safe_handle(handler, websocket, msg))

        except Exception as e:
            logger.error(f"处理websocket消息的逻辑错误: {e}")

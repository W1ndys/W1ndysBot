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
        post_type = msg.get("post_type", "未知消息类型")
        format_msg = ""

        status = msg.get("status")
        if status in ("ok", "failed", "timeout"):
            post_type = "状态"
            if status == "ok":
                data = msg.get("data")
                format_msg += f" | 数据体: {data}"
            else:
                message = msg.get("message")
                wording = msg.get("wording")
                if message:
                    format_msg += f" | 错误信息: {message}"
                if wording:
                    format_msg += f" | 错误描述: {wording}"
            return format_msg

        format_msg += f"[{post_type}]"

        # 元事件
        if post_type == "meta_event":
            meta_event_type = msg.get("meta_event_type")
            if meta_event_type is not None:
                format_msg += f" | 元事件类型: {meta_event_type}"
            sub_type = msg.get("sub_type")
            if sub_type is not None:
                format_msg += f" | 子事件类型: {sub_type}"

        # message 事件
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

        # message_sent 事件
        elif post_type == "message_sent":
            # 该事件并没有相关上报，可能是NapCatQQ以后的更新，暂时忽略
            pass

        # request 事件
        elif post_type == "request":
            request_type = msg.get("request_type")
            if request_type is not None:
                format_msg += f" | 请求类型: {request_type}"
            flag = msg.get("flag")
            if flag is not None:
                format_msg += f" | 请求ID: {flag}"
            comment = msg.get("comment")
            if comment is not None:
                format_msg += f" | 请求备注: {comment}"
            if request_type == "friend":
                if msg.get("sub_type") == "add":  # 添加好友请求
                    user_id = msg.get("user_id")
                    format_msg += f" | 请求类型: 添加好友请求"
                    if user_id is not None:
                        format_msg += f" | 请求者ID: {user_id}"
                elif msg.get("sub_type") == "invite":  # 邀请登录号入群请求
                    format_msg += f" | 请求类型: 邀请登录号入群请求"
                    user_id = msg.get("user_id")
                    if user_id is not None:
                        format_msg += f" | 请求者ID: {user_id}"
                    group_id = msg.get("group_id")
                    if group_id is not None:
                        format_msg += f" | 群ID: {group_id}"

        # notice 事件
        elif post_type == "notice":
            notice_type = msg.get("notice_type")  # 共有

            if notice_type == "friend_add":
                format_msg += " | 通知类型: 好友添加"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 用户ID: {user_id}"

            elif notice_type == "friend_recall":
                format_msg += " | 通知类型: 私聊消息撤回"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 用户ID: {user_id}"
                message_id = msg.get("message_id")
                if message_id is not None:
                    format_msg += f" | 消息ID: {message_id}"

            elif notice_type == "group_admin":
                format_msg += " | 通知类型: 群管理员变动"
                group_id = msg.get("group_id")
                if group_id is not None:
                    format_msg += f" | 群ID: {group_id}"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 变动用户ID: {user_id}"
                sub_type = msg.get("sub_type")
                if sub_type == "set":
                    format_msg += " | 操作: 设置为管理员"
                elif sub_type == "unset":
                    format_msg += " | 操作: 取消管理员"
                elif sub_type is not None:
                    format_msg += f" | 子通知类型: {sub_type}"

            elif notice_type == "group_ban":
                format_msg += " | 通知类型: 群聊禁言"
                group_id = msg.get("group_id")
                if group_id is not None:
                    format_msg += f" | 群ID: {group_id}"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 被禁言用户ID: {user_id}"
                operator_id = msg.get("operator_id")
                if operator_id is not None:
                    format_msg += f" | 操作者ID: {operator_id}"
                duration = msg.get("duration")
                if duration is not None:
                    format_msg += f" | 禁言时长: {duration}秒"
                sub_type = msg.get("sub_type")
                if sub_type is not None:
                    format_msg += f" | 子通知类型: {sub_type}"

            elif notice_type == "group_card":
                format_msg += " | 通知类型: 群成员名片更新"
                group_id = msg.get("group_id")
                if group_id is not None:
                    format_msg += f" | 群ID: {group_id}"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 用户ID: {user_id}"
                card_old = msg.get("card_old")
                if card_old is not None:
                    format_msg += f" | 原名片: {card_old}"
                card_new = msg.get("card_new")
                if card_new is not None:
                    format_msg += f" | 新名片: {card_new}"

            elif notice_type == "group_decrease":
                format_msg += " | 通知类型: 群成员减少"
                group_id = msg.get("group_id")
                if group_id is not None:
                    format_msg += f" | 群ID: {group_id}"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 成员ID: {user_id}"
                sub_type = msg.get("sub_type")
                operator_id = msg.get("operator_id")
                if sub_type == "leave":
                    format_msg += " | 事件: 用户主动退群"
                elif sub_type == "kick":
                    format_msg += " | 事件: 成员被踢出"
                    if operator_id is not None:
                        format_msg += f" | 操作人ID: {operator_id}"
                elif sub_type == "kick_me":
                    format_msg += " | 事件: 登录号被踢出"
                    if operator_id is not None:
                        format_msg += f" | 操作人ID: {operator_id}"
                else:
                    if sub_type is not None:
                        format_msg += f" | 子通知类型: {sub_type}"
                    if operator_id is not None:
                        format_msg += f" | 操作人ID: {operator_id}"

            elif notice_type == "group_increase":
                format_msg += " | 通知类型: 群成员增加"
                group_id = msg.get("group_id")
                if group_id is not None:
                    format_msg += f" | 群ID: {group_id}"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 新成员ID: {user_id}"
                sub_type = msg.get("sub_type")
                operator_id = msg.get("operator_id")
                if sub_type == "approve":
                    format_msg += " | 事件: 管理员同意入群"
                    if operator_id is not None:
                        format_msg += f" | 操作人ID: {operator_id}"
                elif sub_type == "invite":
                    format_msg += " | 事件: 管理员邀请入群"
                    if operator_id is not None:
                        format_msg += f" | 邀请人ID: {operator_id}"
                else:
                    if sub_type is not None:
                        format_msg += f" | 子通知类型: {sub_type}"
                    if operator_id is not None:
                        format_msg += f" | 操作人ID: {operator_id}"

            elif notice_type == "group_recall":
                format_msg += " | 通知类型: 群聊消息撤回"
                group_id = msg.get("group_id")
                if group_id is not None:
                    format_msg += f" | 群ID: {group_id}"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 撤回者ID: {user_id}"
                operator_id = msg.get("operator_id")
                if operator_id is not None:
                    format_msg += f" | 操作人ID: {operator_id}"
                message_id = msg.get("message_id")
                if message_id is not None:
                    format_msg += f" | 消息ID: {message_id}"

            elif notice_type == "group_upload":
                format_msg += " | 通知类型: 群文件上传"
                group_id = msg.get("group_id")
                if group_id is not None:
                    format_msg += f" | 群ID: {group_id}"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 上传者ID: {user_id}"
                file_info = msg.get("file")
                if file_info:
                    file_id = file_info.get("id")
                    file_name = file_info.get("name")
                    file_size = file_info.get("size")
                    busid = file_info.get("busid")
                    if file_id is not None:
                        format_msg += f" | 文件ID: {file_id}"
                    if file_name is not None:
                        format_msg += f" | 文件名: {file_name}"
                    if file_size is not None:
                        format_msg += f" | 文件大小: {file_size}字节"
                    if busid is not None:
                        format_msg += f" | busid: {busid}"

            elif notice_type == "group_msg_emoji_like":
                format_msg += " | 通知类型: 群聊表情回应"
                group_id = msg.get("group_id")
                if group_id is not None:
                    format_msg += f" | 群ID: {group_id}"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 用户ID: {user_id}"
                message_id = msg.get("message_id")
                if message_id is not None:
                    format_msg += f" | 消息ID: {message_id}"
                likes = msg.get("likes")
                if likes and isinstance(likes, list):
                    emoji_info = []
                    for like in likes:
                        emoji_id = like.get("emoji_id")
                        count = like.get("count")
                        if emoji_id is not None and count is not None:
                            emoji_info.append(f"表情ID: {emoji_id}, 数量: {count}")
                    if emoji_info:
                        format_msg += " | " + " ; ".join(emoji_info)

            elif notice_type == "essence":
                format_msg += " | 通知类型: 群聊设精"
                group_id = msg.get("group_id")
                if group_id is not None:
                    format_msg += f" | 群ID: {group_id}"
                message_id = msg.get("message_id")
                if message_id is not None:
                    format_msg += f" | 消息ID: {message_id}"
                operator_id = msg.get("operator_id")
                if operator_id is not None:
                    format_msg += f" | 操作人ID: {operator_id}"
                sub_type = msg.get("sub_type")
                if sub_type is not None:
                    format_msg += f" | 子类型: {sub_type}"

            elif notice_type == "notify" and msg.get("sub_type") == "poke":
                format_msg += " | 通知类型: 戳一戳"
                group_id = msg.get("group_id")
                if group_id is not None:
                    format_msg += f" | 群ID: {group_id}"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 用户ID: {user_id}"
                target_id = msg.get("target_id")
                if target_id is not None:
                    format_msg += f" | 目标ID: {target_id}"
                raw_info = msg.get("raw_info")
                if raw_info and isinstance(raw_info, list):
                    raw_info_strs = []
                    for item in raw_info:
                        if item.get("type") == "qq":
                            uid = item.get("uid")
                            if uid:
                                raw_info_strs.append(f"QQ UID: {uid}")
                        elif item.get("type") == "img":
                            src = item.get("src")
                            if src:
                                raw_info_strs.append(f"图片: {src}")
                        elif item.get("type") == "nor":
                            txt = item.get("txt")
                            if txt:
                                raw_info_strs.append(f"文本: {txt}")
                    if raw_info_strs:
                        format_msg += " | " + " ; ".join(raw_info_strs)

            elif notice_type == "notify" and msg.get("sub_type") == "input_status":
                format_msg += " | 通知类型: 输入状态"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 用户ID: {user_id}"
                group_id = msg.get("group_id")
                if group_id is not None and group_id != 0:
                    format_msg += f" | 群ID: {group_id}"
                status_text = msg.get("status_text")
                if status_text:
                    format_msg += f" | 状态文本: {status_text}"

            elif notice_type == "notify" and msg.get("sub_type") == "title":
                format_msg += " | 通知类型: 群头衔变更"
                group_id = msg.get("group_id")
                if group_id is not None:
                    format_msg += f" | 群ID: {group_id}"
                user_id = msg.get("user_id")
                if user_id is not None:
                    format_msg += f" | 用户ID: {user_id}"
                title = msg.get("title")
                if title:
                    format_msg += f" | 新头衔: {title}"

            elif notice_type == "notify" and msg.get("sub_type") == "profile_like":
                format_msg += " | 通知类型: 点赞"
                operator_id = msg.get("operator_id")
                if operator_id is not None:
                    format_msg += f" | 操作人ID: {operator_id}"
                operator_nick = msg.get("operator_nick")
                if operator_nick:
                    format_msg += f" | 操作人昵称: {operator_nick}"
                times = msg.get("times")
                if times is not None:
                    format_msg += f" | 点赞次数: {times}"

        else:
            format_msg += f" | [未知内容]"
            # 由于状态类型结构复杂，这里直接加入原内容
            format_msg += f" | 原内容: {msg}"

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

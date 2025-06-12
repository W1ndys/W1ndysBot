import asyncio
from datetime import datetime
from . import (
    MODULE_NAME,
    BAN_WORD_WEIGHT_MAX,
    BAN_WORD_DURATION,
    UNBAN_WORD_COMMAND,
    KICK_BAN_WORD_COMMAND,
)
from .data_manager_words import DataManager
from logger import logger
from api.message import send_group_msg, delete_msg, send_private_msg
from api.generate import generate_text_message, generate_at_message
from api.group import set_group_ban
from config import OWNER_ID
from utils.feishu import send_feishu_msg


class ForwardMessageHandler:
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.messages = self.data.get("messages", [])
        self.echo = msg.get("echo", "")
        self.group_id = None  # 转发消息发送者群号
        self.user_id = None  # 转发消息发送者QQ号
        self.message_id = None  # 转发消息ID
        self.data_manager = DataManager(group_id=self.group_id)
        self.raw_message = ""
        self.formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def handle_forward_message(self):
        """处理转发消息"""
        try:
            # 解析echo内的参数
            parts = self.echo.split("-")
            for part in parts[2:]:  # 跳过 'get_forward_msg' 和 MODULE_NAME
                if "=" in part:
                    key, value = part.split("=")
                    if key == "group_id":
                        self.group_id = value
                    elif key == "user_id":
                        self.user_id = value
                    elif key == "message_id":
                        self.message_id = value
            logger.info(
                f"[{MODULE_NAME}]收到转发消息解析响应: 群号: {self.group_id}, 发送者QQ号: {self.user_id}, 消息ID: {self.message_id}"
            )
            # 拼接message里的所有raw_message
            raw_message = ""
            for item in self.messages:
                raw_message += item.get("raw_message", "")
            self.raw_message = raw_message
            logger.info(f"[{MODULE_NAME}]拼接后的所有原始消息内容: {raw_message}")

            # 计算违禁词权重
            total_weight, matched_words = self.data_manager.calc_message_weight(
                raw_message
            )
            is_banned = total_weight > BAN_WORD_WEIGHT_MAX
            if is_banned:
                # 返回True，表示违规
                await set_group_ban(
                    self.websocket,
                    self.group_id,
                    self.user_id,
                    BAN_WORD_DURATION,
                )
                # 撤回消息
                await delete_msg(self.websocket, self.message_id)
                # 设置用户状态
                self.data_manager.set_user_status(self.user_id, "ban")
                # 发送警告消息
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_at_message(self.user_id),
                        generate_text_message(
                            f"({self.user_id})请勿发送违禁消息，如误封请联系管理员"
                        ),
                    ],
                    note="del_msg=20",
                )
                # 发送管理员消息
                await send_private_msg(
                    self.websocket,
                    OWNER_ID,
                    [
                        generate_text_message(
                            f"[{self.formatted_time}]\n"
                            f"群{self.group_id}用户{self.user_id}发送违禁词\n"
                            f"已封禁{BAN_WORD_DURATION}秒\n"
                            f"涉及违禁词: {', '.join(matched_words)}\n"
                            f"相关消息已通过飞书上报\n"
                            f"发送{UNBAN_WORD_COMMAND} {self.group_id} {self.user_id}解封用户\n"
                            f"发送{KICK_BAN_WORD_COMMAND} {self.group_id} {self.user_id}踢出用户"
                        )
                    ],
                )

                # 异步延迟0.3秒
                await asyncio.sleep(0.3)

                # 发送快速命令便于复制
                await send_private_msg(
                    self.websocket,
                    OWNER_ID,
                    [
                        generate_text_message(
                            f"{UNBAN_WORD_COMMAND} {self.group_id} {self.user_id}"
                        )
                    ],
                )
                await asyncio.sleep(0.3)
                await send_private_msg(
                    self.websocket,
                    OWNER_ID,
                    [
                        generate_text_message(
                            f"{KICK_BAN_WORD_COMMAND} {self.group_id} {self.user_id}"
                        )
                    ],
                )

                # 发送飞书消息
                send_feishu_msg(
                    title=f"触发违禁词",
                    content=f"时间: {self.formatted_time}\n"
                    f"群{self.group_id}用户{self.user_id}发送违禁词\n"
                    f"已封禁{BAN_WORD_DURATION}秒\n"
                    f"涉及违禁词: {', '.join(matched_words)}\n"
                    f"原始消息: {self.raw_message}",
                )
                return True
            else:
                # 检测用户状态
                user_status = self.data_manager.get_user_status(self.user_id)
                if user_status == "ban":
                    # 撤回消息
                    await delete_msg(self.websocket, self.message_id)
                    # 禁言
                    await set_group_ban(
                        self.websocket,
                        self.group_id,
                        self.user_id,
                        BAN_WORD_DURATION,
                    )
                    return True
            return False
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理转发消息失败: {e}")

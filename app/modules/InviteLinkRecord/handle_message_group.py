from . import (
    MODULE_NAME,
    SWITCH_NAME,
    VIEW_INVITE_RECORD,
    KICK_INVITE_RECORD,
)
import logger
from core.switchs import is_group_switch_on, toggle_group_switch
from api.message import send_group_msg
from api.generate import generate_reply_message, generate_text_message
from api.group import set_group_kick, set_group_ban
from datetime import datetime
from .data_manager import InviteLinkRecordDataManager
import re
import asyncio


class GroupMessageHandler:
    """群消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.sub_type = msg.get("sub_type", "")  # 子类型，只有normal
        self.group_id = str(msg.get("group_id", ""))  # 群号
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.message = msg.get("message", {})  # 消息段数组
        self.raw_message = msg.get("raw_message", "")  # 原始消息
        self.sender = msg.get("sender", {})  # 发送者信息
        self.nickname = self.sender.get("nickname", "")  # 昵称
        self.card = self.sender.get("card", "")  # 群名片
        self.role = self.sender.get("role", "")  # 群身份

    async def handle_module_switch(self):
        """
        处理模块开关命令
        """
        try:
            switch_status = toggle_group_switch(self.group_id, MODULE_NAME)
            switch_status = "开启" if switch_status else "关闭"
            reply_message = generate_reply_message(self.message_id)
            text_message = generate_text_message(
                f"[{MODULE_NAME}]群聊开关已切换为【{switch_status}】"
            )
            await send_group_msg(
                self.websocket,
                self.group_id,
                [reply_message, text_message],
                note="del_msg_10",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理模块开关命令失败: {e}")

    async def handle(self):
        """
        处理群消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                await self.handle_module_switch()
                return

            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            invite_link_record = InviteLinkRecordDataManager(self.msg)
            # 查看邀请记录命令
            if self.raw_message.startswith(VIEW_INVITE_RECORD):
                # 使用正则提取参数，支持QQ号或CQ码
                operator_id = None
                # 匹配CQ码 [CQ:at,qq=123456789]
                cq_match = re.search(r"\[CQ:at,qq=(\d+)\]", self.raw_message)
                if cq_match:
                    operator_id = cq_match.group(1)
                else:
                    # 匹配空格后面的纯数字QQ号
                    num_match = re.search(
                        rf"{VIEW_INVITE_RECORD}\s+(\d+)", self.raw_message
                    )
                    if num_match:
                        operator_id = num_match.group(1)

                if not operator_id:
                    # 没有找到参数，提示格式错误
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [generate_text_message("请提供正确的QQ号或@某人。")],
                    )
                    return
                # 调用查看邀请记录

                # 生成完整邀请链路和树状结构
                invite_chain_str = invite_link_record.get_full_invite_chain_str(
                    operator_id
                )
                # 发送邀请记录
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_text_message(
                            f"{operator_id}邀请链结构\n\n" + invite_chain_str
                        )
                    ],
                )
                return

            # 踢出邀请树命令
            if self.raw_message.startswith(KICK_INVITE_RECORD):
                # 使用正则提取参数，支持QQ号或CQ码
                operator_id = None
                # 匹配CQ码 [CQ:at,qq=123456789]
                cq_match = re.search(r"\[CQ:at,qq=(\d+)\]", self.raw_message)
                if cq_match:
                    operator_id = cq_match.group(1)
                else:
                    # 匹配空格后面的纯数字QQ号
                    num_match = re.search(
                        rf"{KICK_INVITE_RECORD}\s+(\d+)", self.raw_message
                    )
                    if num_match:
                        operator_id = num_match.group(1)

                if not operator_id:
                    # 没有找到参数，提示格式错误
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [generate_text_message("请提供正确的QQ号或@某人。")],
                    )
                    return

                # 获取相关邀请者
                related_users = invite_link_record.get_related_invite_users(operator_id)
                # 发送踢出邀请树
                for user_id in related_users:
                    # 踢出邀请树
                    await set_group_kick(self.websocket, self.group_id, user_id)
                    # 删除邀请记录
                    invite_link_record.delete_invite_record_by_invited_id(user_id)
                    await asyncio.sleep(0.5)

                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_text_message(
                            f"已执行踢出邀请树: {','.join(related_users)}"
                        )
                    ],
                )
                return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

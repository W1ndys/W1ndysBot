from datetime import datetime
import asyncio
import logger
from .data_manager import DataManager
from . import (
    MODULE_NAME,
    SCAN_VERIFICATION,
    STATUS_KICKED,
    STATUS_VERIFIED,
    WARNING_COUNT,
    STATUS_UNVERIFIED,
)
from api.group import set_group_kick
from api.message import send_group_msg, send_private_msg
from api.generate import generate_text_message, generate_at_message
from config import OWNER_ID


class GroupHumanVerificationHandler:
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.sub_type = msg.get("sub_type", "")  # 子类型,friend/group
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.group_id = str(msg.get("group_id", ""))  # 群组ID
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.message = msg.get("message", {})  # 消息段数组
        self.raw_message = msg.get("raw_message", "")  # 原始消息
        self.sender = msg.get("sender", {})  # 发送者信息
        self.nickname = self.sender.get("nickname", "")  # 昵称

    async def handle_scan_verification(self):
        """
        处理扫描入群验证
        """
        try:
            with DataManager() as dm:
                unverified_users = dm.get_all_unverified_users_with_code_and_warning()
                result_msgs = []  # 新增：用于统计结果
                if unverified_users:
                    for group_id, user_list in unverified_users.items():
                        # 记录需要踢出的用户
                        kick_users = []
                        # 记录需要提醒的用户消息
                        msg_list = []
                        for user_id, warning_count, code in user_list:
                            if warning_count > 1:
                                dm.update_warning_count(
                                    group_id, user_id, warning_count - 1
                                )
                                # 生成@和文本消息
                                msg_at = generate_at_message(user_id)
                                msg_text = generate_text_message(
                                    f"({user_id}) 请尽快完成验证，你的验证码是：{code}（剩余警告{warning_count - 1}/{WARNING_COUNT}）"
                                )
                                msg_list.extend([msg_at, msg_text])
                                # 统计
                                result_msgs.append(
                                    f"群{group_id} 用户{user_id} 警告-1，剩余{warning_count-1}"
                                )
                            else:
                                # 警告次数为0，踢群并标记为超时
                                kick_users.append(user_id)
                                result_msgs.append(
                                    f"群{group_id} 用户{user_id} 已被踢出（警告用尽）"
                                )
                        # 合并提醒消息，一次性发到群里
                        if msg_list:
                            await send_group_msg(self.websocket, group_id, msg_list)
                        # 依次踢出需要踢出的用户
                        for user_id in kick_users:
                            await set_group_kick(self.websocket, group_id, user_id)
                            dm.update_status(group_id, user_id, STATUS_KICKED)
                            # 踢人操作间隔1秒，防止风控
                            await asyncio.sleep(1)
                        # 发消息间隔1秒，防止风控
                        await asyncio.sleep(1)
                # 新增：扫描结果私聊通知管理员
                if result_msgs:
                    msg = "\n".join(result_msgs)
                    await send_private_msg(
                        self.websocket, self.user_id, f"[扫描验证结果]\n{msg}"
                    )
                else:
                    await send_private_msg(
                        self.websocket, self.user_id, "[扫描验证结果] 当前无未验证用户"
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理扫描入群验证失败: {e}")

    async def handle_admin_command(self):
        """
        处理管理员命令
        """
        try:
            # 鉴权
            if self.user_id != OWNER_ID:
                return

            # 处理扫描入群验证
            if self.raw_message.startswith(SCAN_VERIFICATION):
                await self.handle_scan_verification()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理管理员命令失败: {e}")

    async def handle_user_command(self):
        """
        处理用户命令
        """
        try:
            with DataManager() as dm:
                # 有群号时，按群号和用户ID检测验证码
                if self.group_id:
                    code = dm.get_code_with_group_and_user(self.group_id, self.user_id)
                    if self.raw_message == code:
                        dm.update_status(self.group_id, self.user_id, STATUS_VERIFIED)
                        msg_at = generate_at_message(self.user_id)
                        msg_text = generate_text_message(
                            f"({self.user_id}) 你在群 {self.group_id} 的验证已通过，你可以正常发言了！"
                        )
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [msg_at, msg_text],
                            note="del_msg=60",
                        )
                else:
                    # 无群号时，根据用户发的消息和QQ号检测数据库里该验证码所在群的状态是否是未验证
                    # 某用户在多个群的验证码相同的情况极少发生
                    group_id = dm.get_group_with_code_and_user(
                        self.user_id, self.raw_message
                    )
                    if group_id:
                        # 找到未验证的群，更新其状态
                        dm.update_status(group_id, self.user_id, STATUS_VERIFIED)
                        msg_at = generate_at_message(self.user_id)
                        msg_text = generate_text_message(
                            f"({self.user_id}) 你在群 {group_id} 的验证已通过，你可以正常发言了！"
                        )
                        await send_group_msg(
                            self.websocket,
                            group_id,
                            [msg_at, msg_text],
                            note="del_msg=60",
                        )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理用户命令失败: {e}")

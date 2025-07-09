from .. import (
    MODULE_NAME,
    SWITCH_NAME,
    VIEW_INVITE_RECORD,
    KICK_INVITE_RECORD,
)
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from api.message import send_group_msg
from utils.generate import generate_reply_message, generate_text_message
from api.group import set_group_kick
from datetime import datetime
from .data_manager import InviteTreeRecordDataManager
import re
import asyncio
from core.menu_manager import MenuManager
from utils.auth import is_group_admin, is_system_admin


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

    async def handle(self):
        """
        处理群消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                # 鉴权
                if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                    return
                await handle_module_group_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.group_id,
                    self.message_id,
                )
                return

            # 处理菜单命令（无视开关状态）
            if self.raw_message.lower() == f"{SWITCH_NAME}{MENU_COMMAND}".lower():
                menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(menu_text),
                    ],
                    note="del_msg=30",
                )
                return

            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 使用 with 语法管理数据库连接
            with InviteTreeRecordDataManager(
                self.websocket, self.msg
            ) as invite_tree_record:
                # 查看邀请记录命令
                if self.raw_message.startswith(VIEW_INVITE_RECORD):
                    # 鉴权
                    if not is_group_admin(self.role) and not is_system_admin(
                        self.user_id
                    ):
                        return

                    # 移除命令前缀
                    remaining_text = self.raw_message.removeprefix(
                        VIEW_INVITE_RECORD
                    ).strip()

                    operator_id = None
                    show_time = False

                    # 检查是否包含时间参数
                    if "时间" in remaining_text or "time" in remaining_text.lower():
                        show_time = True
                        # 移除时间关键词
                        remaining_text = (
                            remaining_text.replace("时间", "")
                            .replace("time", "")
                            .strip()
                        )

                    # 优先从CQ码中提取QQ号
                    cq_match = re.search(r"\[CQ:at,qq=(\d+)\]", remaining_text)
                    if cq_match:
                        operator_id = cq_match.group(1)
                    else:
                        # 从剩余文本中提取数字（支持无空格的情况）
                        num_match = re.search(r"(\d+)", remaining_text)
                        if num_match:
                            operator_id = num_match.group(1)

                    if not operator_id:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [generate_text_message("请提供正确的QQ号或@某人。")],
                        )
                        return

                    invite_chain_str = invite_tree_record.get_full_invite_chain_str(
                        operator_id, show_time=show_time
                    )

                    time_tip = (
                        "\n\n提示：使用「查看邀请记录时间 QQ号」可查看带时间的邀请树"
                        if not show_time
                        else ""
                    )

                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"{operator_id}邀请树结构\n\n"
                                + invite_chain_str
                                + time_tip
                                + f"\n\n消息将于30秒后撤回，请及时记录"
                            ),
                        ],
                        note="del_msg=30",
                    )
                    return

                # 踢出邀请树命令
                if self.raw_message.startswith(KICK_INVITE_RECORD):
                    # 鉴权
                    if not is_group_admin(self.role) and not is_system_admin(
                        self.user_id
                    ):
                        return

                    operator_id = None
                    cq_match = re.search(r"\[CQ:at,qq=(\d+)\]", self.raw_message)
                    if cq_match:
                        operator_id = cq_match.group(1)
                    else:
                        num_match = re.search(
                            rf"{KICK_INVITE_RECORD}\s+(\d+)", self.raw_message
                        )
                        if num_match:
                            operator_id = num_match.group(1)

                    if not operator_id:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [generate_text_message("请提供正确的QQ号或@某人。")],
                        )
                        return

                    related_users = invite_tree_record.get_related_invite_users(
                        operator_id
                    )
                    # 创建异步任务列表
                    tasks = []
                    for user_id in related_users:
                        # 创建踢出用户的协程任务
                        tasks.append(
                            asyncio.create_task(
                                set_group_kick(self.websocket, self.group_id, user_id)
                            )
                        )
                        # 删除该用户的所有相关邀请记录（包括作为邀请者和被邀请者的记录）
                        invite_tree_record.delete_all_invite_records_by_user_id(user_id)
                        await asyncio.sleep(0.05)  # 等待0.05秒，交出控制权

                    # 等待所有任务完成
                    await asyncio.gather(*tasks)

                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"已执行踢出邀请树: {'， '.join(related_users)}"
                            ),
                        ],
                        note="del_msg=10",
                    )
                    return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

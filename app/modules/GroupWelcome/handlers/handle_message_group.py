from .. import MODULE_NAME, SWITCH_NAME, GWSET
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from utils.auth import is_system_admin, is_group_admin
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime
from .data_manager import DataManager
from core.menu_manager import MenuManager


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

    async def _handle_switch_command(self):
        """
        处理群聊开关命令
        """
        if self.raw_message.lower() == SWITCH_NAME.lower():
            # 鉴权
            if not is_system_admin(self.user_id):
                logger.error(f"[{MODULE_NAME}]{self.user_id}无权限切换群聊开关")
                return True
            await handle_module_group_switch(
                MODULE_NAME,
                self.websocket,
                self.group_id,
                self.message_id,
            )
            return True
        return False

    async def _handle_menu_command(self):
        """
        处理菜单命令（无视开关状态）
        """
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
            return True
        return False

    async def _handle_set_in_welcome_message(self, message):
        """
        处理设置入群消息
        """
        try:
            with DataManager() as dm:
                dm.set_notice_content(self.group_id, "in", message)
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("入群消息设置成功"),
                    ],
                )
                logger.info(
                    f"[{MODULE_NAME}]设置入群消息成功，群号：{self.group_id}，消息：{message}"
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理设置入群消息失败: {e}")

    async def _handle_set_out_welcome_message(self, message):
        """
        处理设置退群消息
        """
        try:
            with DataManager() as dm:
                dm.set_notice_content(self.group_id, "out", message)
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("退群消息设置成功"),
                    ],
                )
                logger.info(
                    f"[{MODULE_NAME}]设置退群消息成功，群号：{self.group_id}，消息：{message}"
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理设置退群消息失败: {e}")

    async def _handle_set_welcome_message(self):
        """
        处理设置入群欢迎退群通知消息
        """
        try:
            if self.raw_message.startswith(GWSET):
                # 获取参数
                params = self.raw_message.split()
                if len(params) < 3:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                "参数不足，请使用/gwset [参数1] [参数2]，参数1可选in或out，参数2为入群欢迎退群提醒信息"
                            ),
                        ],
                        note="del_msg=10",
                    )
                    return
                # 获取参数1
                param1 = params[1]
                # 获取参数2，参数1往后的所有内容都算参数2，保留换行
                param2 = self.raw_message.split(None, 2)[2] if len(params) > 2 else ""

                # 判断参数1是否为in或out
                if param1 not in ["in", "out"]:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                "参数1错误，请使用/gwset [参数1] [参数2]，参数1可选in或out"
                            ),
                        ],
                        note="del_msg=10",
                    )
                    return

                # 判断参数2是否为空
                if not param2:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message("参数2不能为空"),
                        ],
                    )
                    return

                # 处理存储入群消息
                if param1 == "in":
                    # 存储入群消息
                    await self._handle_set_in_welcome_message(param2)
                elif param1 == "out":
                    # 存储退群消息
                    await self._handle_set_out_welcome_message(param2)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理设置入群欢迎退群通知消息失败: {e}")

    async def handle(self):
        """
        处理群消息
        """
        try:
            # 处理群聊开关命令
            if await self._handle_switch_command():
                return

            # 处理菜单命令
            if await self._handle_menu_command():
                return

            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 鉴权
            if not is_system_admin(self.user_id) and not is_group_admin(self.role):
                return

            # 处理设置入群欢迎退群通知消息
            await self._handle_set_welcome_message()

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

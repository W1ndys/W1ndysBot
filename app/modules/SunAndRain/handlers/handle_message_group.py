from .. import MODULE_NAME, SWITCH_NAME, SIGN_IN_COMMAND, SELECT_COMMAND
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from utils.auth import is_system_admin
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

    async def _handle_sign_in_command(self):
        """
        处理签到命令
        """
        try:
            if self.raw_message.startswith(SIGN_IN_COMMAND):
                with DataManager() as dm:
                    # 首先检查用户是否已经选择了类型
                    user_info = dm.get_user_info(self.group_id, self.user_id)

                    if user_info["code"] != 200 or not user_info["data"]:
                        # 用户没有选择类型
                        no_selection_message = (
                            "❌ 您还没有选择类型！\n"
                            "🌟 请先选择您的类型：\n"
                            "✨ 阳光类型：发送「选择 阳光」\n"
                            "💧 雨露类型：发送「选择 雨露」\n"
                            "📝 选择后即可开始签到获得奖励！"
                        )
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [
                                generate_reply_message(self.message_id),
                                generate_text_message(no_selection_message),
                            ],
                        )
                        return

                    # 获取用户的类型（可能有多个，取第一个）
                    user_type = user_info["data"][0][3]  # type字段

                    # 执行签到
                    result = dm.daily_checkin(self.group_id, self.user_id, user_type)
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(result["message"]),
                        ],
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理签到命令失败: {e}")

    async def _handle_select_command(self):
        """
        处理选择命令
        """
        try:
            if self.raw_message.startswith(SELECT_COMMAND):
                # 解析用户选择的类型
                message_parts = self.raw_message.strip().split()

                if len(message_parts) < 2:
                    # 用户只输入了"选择"，提供帮助信息
                    help_message = (
                        "🌟 请选择您的类型：\n"
                        "✨ 阳光类型：发送「选择 阳光」\n"
                        "💧 雨露类型：发送「选择 雨露」\n"
                        "📝 选择后即可开始签到获得奖励！"
                    )
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(help_message),
                        ],
                    )
                    return

                choice = message_parts[1].strip()
                user_type = None

                if choice in ["阳光", "阳光类型", "阳光型", "sun", "sunshine"]:
                    user_type = 0
                elif choice in [
                    "雨露",
                    "雨露",
                    "雨露类型",
                    "雨露类型",
                    "rain",
                    "raindrop",
                ]:
                    user_type = 1
                else:
                    # 无效选择
                    error_message = (
                        "❌ 选择无效！\n"
                        "🌟 请选择以下类型之一：\n"
                        "✨ 阳光类型：发送「选择 阳光」\n"
                        "💧 雨露类型：发送「选择 雨露」\n"
                        "📝 提示：输入格式为「选择 类型名称」"
                    )
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(error_message),
                        ],
                    )
                    return

                # 添加用户
                with DataManager() as dm:
                    result = dm.add_user(self.group_id, self.user_id, user_type)
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(result["message"]),
                        ],
                    )
                    return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理选择命令失败: {e}")

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

            # 示例：使用with语句块进行数据库操作
            if self.raw_message.startswith(SIGN_IN_COMMAND):
                await self._handle_sign_in_command()
                return
            if self.raw_message.startswith(SELECT_COMMAND):
                await self._handle_select_command()
                return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

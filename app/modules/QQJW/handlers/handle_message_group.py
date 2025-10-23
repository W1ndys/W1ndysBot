from .. import MODULE_NAME, SWITCH_NAME, STATUS_COMMAND, FORWARD_GROUP_ID
from core.menu_manager import MENU_COMMAND
from logger import logger
from datetime import datetime
from core.switchs import is_group_switch_on, handle_module_group_switch
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_reply_message
from core.menu_manager import MenuManager
from utils.auth import is_group_admin
from core.get_group_list import get_group_member_info_by_id
from ..utils.data_manager import DataManager


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
            if not is_group_admin(self.role):
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
            )
            return True
        return False

    async def _handle_status_command(self):
        """
        处理状态查询命令（仅限中转群）
        """
        if self.raw_message.lower() == STATUS_COMMAND.lower():
            # 只在中转群中生效
            if self.group_id != FORWARD_GROUP_ID:
                return False

            try:
                # 获取启用群列表
                enable_groups_list = self._get_enable_groups_list()
                if not enable_groups_list:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message("📊当前没有启用的教务群"),
                        ],
                    )
                    return True

                # 获取群详细信息
                enable_groups_info_list = self._get_enable_groups_info_list(
                    enable_groups_list
                )
                if not enable_groups_info_list:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message("❌无法获取群详细信息"),
                        ],
                    )
                    return True

                # 构建状态消息
                status_message = self._build_status_message(enable_groups_info_list)
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(status_message),
                    ],
                )
                return True

            except Exception as e:
                logger.error(f"[{MODULE_NAME}]处理状态查询命令失败: {e}")
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("❌查询群状态失败，请稍后再试"),
                    ],
                )
                return True

        return False

    def _get_enable_groups_list(self):
        """
        获取教务启用群列表
        """
        try:
            with DataManager() as data_manager:
                group_list = (
                    data_manager.get_enable_group_list()
                    .get("data", {})
                    .get("group_list", [])
                )
                if not isinstance(group_list, list):
                    logger.error(f"[{MODULE_NAME}]获取到的群列表不是列表类型")
                    raise TypeError("获取到的群列表不是列表类型")
                return group_list
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取教务启用群列表失败: {e}")
            raise

    def _get_enable_groups_info_list(self, enable_groups_list):
        """
        获取每个群的群名、当前人数和最大人数
        """
        enable_groups_info_list = []
        for group_id in enable_groups_list:
            try:
                group_member_info = get_group_member_info_by_id(group_id)
                if not group_member_info:
                    logger.error(f"[{MODULE_NAME}]未获取到群{group_id}的信息")
                    continue
                enable_groups_info_list.append(
                    {
                        "group_id": group_id,
                        "group_name": group_member_info.get("group_name"),
                        "member_count": group_member_info.get("member_count"),
                        "max_member_count": group_member_info.get("max_member_count"),
                    }
                )
            except Exception as e:
                logger.error(f"[{MODULE_NAME}]获取群{group_id}信息失败: {e}")
        return enable_groups_info_list

    def _build_status_message(self, enable_groups_info_list):
        """
        构建群状态信息消息
        """
        try:
            if not enable_groups_info_list:
                return "📊当前没有可用的教务群信息"

            # 按群号排序
            sorted_groups = sorted(
                enable_groups_info_list, key=lambda x: str(x.get("group_id", ""))
            )

            status_message = "📊【教务群状态查询】\n"
            status_message += f"📅查询时间：{self.formatted_time}\n"
            status_message += f"🔢启用群数量：{len(sorted_groups)}个\n\n"

            for i, group_info in enumerate(sorted_groups, 1):
                group_id = group_info.get("group_id", "")
                group_name = group_info.get("group_name", "未知群名")
                member_count = group_info.get("member_count", 0)
                max_member_count = group_info.get("max_member_count", 0)
                remaining_count = max_member_count - member_count

                # 计算填充度百分比
                fill_percentage = (
                    (member_count / max_member_count * 100)
                    if max_member_count > 0
                    else 0
                )

                # 根据填充度选择图标
                if fill_percentage >= 95:
                    status_icon = "🔴"  # 几乎满员
                elif fill_percentage >= 80:
                    status_icon = "🟡"  # 人数较多
                else:
                    status_icon = "🟢"  # 人数较少

                status_message += f"{status_icon}{i}. 【{group_name}】\n"
                status_message += f"   群号：{group_id}\n"
                status_message += f"   人数：{member_count}/{max_member_count}\n"
                status_message += f"   剩余：{remaining_count}个名额\n"
                status_message += f"   填充：{fill_percentage:.1f}%\n\n"

            status_message += "💡提示：🟢空闲 🟡较满 🔴几乎满员"
            return status_message

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]构建群状态信息消息失败: {e}")
            return "❌构建群状态信息失败"

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

            # 处理状态查询命令（仅限中转群，无视开关状态）
            if await self._handle_status_command():
                return

            # 如果没开启群聊开关，则不处理其他消息
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

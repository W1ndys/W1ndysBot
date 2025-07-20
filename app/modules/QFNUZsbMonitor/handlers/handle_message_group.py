from .. import MODULE_NAME, SWITCH_NAME, QUERY_ADMISSION_STATUS_COMMAND, DATA_DIR
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from utils.auth import is_system_admin, is_group_admin
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime
from core.menu_manager import MenuManager
import os
import json


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
            if not is_system_admin(self.user_id) and not is_group_admin(self.role):
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

    async def _handle_query_admission_status_command(self):
        """
        处理招生状态查询命令
        """
        try:
            # 分离参数
            params = self.raw_message.split(" ")
            if len(params) < 2:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    "请输入省份",
                )
                return True
            province = params[1]
            status_file = os.path.join(DATA_DIR, "status.json")

            if not os.path.exists(status_file):
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    "暂无招生状态信息。",
                )
                return True

            with open(status_file, "r", encoding="utf-8") as f:
                status_data = json.load(f)

            if not status_data.get("can_query", False):
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    "当前暂不可查询。",
                )
                return True

            province_status = status_data.get("provinces", {}).get(province)

            if not province_status:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    f"未找到省份【{province}】的招生信息，请检查省份名称是否正确。",
                )
                return True

            year = status_data.get("year", "")
            school_name = status_data.get("school_name", "")
            message_lines = [f"{school_name} {year}年 在【{province}】的录取状态:"]

            for category, details in province_status.items():
                status_text = details.get("status_text", "暂无信息")
                message_lines.append(f"· {category}: {status_text}")

            if len(message_lines) == 1:
                message = f"暂未查询到【{province}】的详细录取状态信息。"
            else:
                message = "\n".join(message_lines)

            message += "\n数据仅供参考，以官方为准，数据一分钟更新一次。"
            if self.group_id != "264545015":
                message += (
                    "\n曲阜师范大学新生群 1046961227 提供技术支持，欢迎互相邀请加入。"
                )

            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(message),
                ],
            )
            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理招生状态查询命令失败: {e}")
            return False

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

            # 处理招生状态查询命令
            if self.raw_message.startswith(QUERY_ADMISSION_STATUS_COMMAND):
                await self._handle_query_admission_status_command()

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

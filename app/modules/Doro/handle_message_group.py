from . import MODULE_NAME, SWITCH_NAME, MENU_COMMAND, COMMANDS
import logger
from core.switchs import is_group_switch_on, toggle_group_switch
from api.message import send_group_msg
from api.generate import (
    generate_reply_message,
    generate_text_message,
    generate_image_message,
)
from datetime import datetime


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
                note="del_msg=10",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理模块开关命令失败: {e}")

    async def handle_menu(self):
        """
        处理菜单命令
        """
        try:
            reply_message = generate_reply_message(self.message_id)
            menu_text = f"[{MODULE_NAME}]可用命令列表：\n"
            for cmd, desc in COMMANDS.items():
                menu_text += f"- {cmd}: {desc}\n"
            text_message = generate_text_message(menu_text)
            await send_group_msg(
                self.websocket,
                self.group_id,
                [reply_message, text_message],
                note="del_msg=30",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理菜单命令失败: {e}")

    async def handle(self):
        """
        处理群消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                await self.handle_module_switch()
                return

            # 处理菜单命令（无视开关状态）
            if self.raw_message.lower() == (SWITCH_NAME + MENU_COMMAND).lower():
                await self.handle_menu()
                return

            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 新增功能：异步请求 Doro 随机表情包 API
            import aiohttp

            # 判断是否触发 Doro 指令
            from . import DORO_COMMANDS

            if self.raw_message.strip() == DORO_COMMANDS:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("正在获取Doro表情包..."),
                    ],
                    note="del_msg=3",
                )
                api_url = "https://www.doro.asia/api/random-sticker"
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get("success") and "sticker" in data:
                                sticker = data["sticker"]
                                url = sticker.get("url", "")
                                # 只发送图片消息，不发送文字描述和回复id
                                image_message = generate_image_message(url)
                                await send_group_msg(
                                    self.websocket,
                                    self.group_id,
                                    [image_message],
                                    note="del_msg=60",
                                )
                                return
                            else:
                                # 失败时也不发描述和回复id，直接返回
                                return
                        else:
                            # API请求失败也直接返回
                            return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

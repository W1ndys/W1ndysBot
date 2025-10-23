from .. import MODULE_NAME, SWITCH_NAME, BIND_COMMAND, QUERY_COMMAND
from core.menu_manager import MENU_COMMAND
from logger import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from utils.auth import is_system_admin
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime
from .data_manager import DataManager
from core.menu_manager import MenuManager
import re
from ..core.ElectricityQuery import ElectricityQuery


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

    async def _handle_bind_command(self):
        """
        处理绑定命令
        """
        try:
            # 正则提取openid，形如 http://wechat.sdkdch.cn/h5/?openId=xxxxxxxxx，提取openId=后面的xxxxxxxxx
            open_id_pattern = r"openId=([^&]+)"
            open_id_match = re.search(open_id_pattern, self.raw_message)
            if open_id_match:
                open_id = open_id_match.group(1)
                # 保存openid到数据库，如果已经存在，则更新
                with DataManager() as dm:
                    if dm.check_user_exists(self.user_id):
                        dm.update_openid(self.user_id, open_id)
                    else:
                        dm.add_user_openid(self.user_id, open_id)
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            f"绑定成功，绑定成功后，您可以查询电费，您现在可以撤回链接了"
                        ),
                    ],
                )
                return True
            else:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(f"绑定失败，请检查电费链接是否正确"),
                    ],
                )
        except Exception as e:
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(f"处理绑定命令失败: {e}"),
                ],
            )
            logger.error(f"[{MODULE_NAME}]处理绑定命令失败: {e}")

    async def _handle_query_command(self):
        """
        处理查询命令
        """
        try:
            with DataManager() as dm:
                openid = dm.get_openid_by_user_id(self.user_id)
                if not openid:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(f"您未绑定电费链接，请先绑定"),
                        ],
                    )
                    return True
                else:
                    # 查询电费
                    electricity_query = ElectricityQuery()
                    result = await electricity_query.parse_result(openid)
                    logger.info(f"[{MODULE_NAME}]查询电费结果: {result}")
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                result.get("message", "查询失败，未知错误")
                            ),
                        ],
                    )
                    return True
        except Exception as e:
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(f"处理查询命令失败: {e}"),
                ],
            )
            logger.error(f"[{MODULE_NAME}]处理查询命令失败: {e}")

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

            # 处理绑定命令
            if self.raw_message.startswith(BIND_COMMAND):
                logger.info(
                    f"[{MODULE_NAME}]处理绑定命令，user_id:{self.user_id}，group_id:{self.group_id}"
                )
                await self._handle_bind_command()
                return

            # 处理查询命令
            if self.raw_message.startswith(QUERY_COMMAND):
                logger.info(
                    f"[{MODULE_NAME}]处理查询命令，user_id:{self.user_id}，group_id:{self.group_id}"
                )
                await self._handle_query_command()
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

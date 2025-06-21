from . import MODULE_NAME, SWITCH_NAME, SAVE_JW_ACCOUNT_COMMAND
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_private_switch_on, handle_module_private_switch
from api.message import send_private_msg
from api.generate import generate_text_message, generate_reply_message
from datetime import datetime
from .data_manager import DataManager
from core.auth import is_system_admin
from core.menu_manager import MenuManager


class PrivateMessageHandler:
    """私聊消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.sub_type = msg.get("sub_type", "")  # 子类型,friend/group
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.message = msg.get("message", {})  # 消息段数组
        self.raw_message = msg.get("raw_message", "")  # 原始消息
        self.sender = msg.get("sender", {})  # 发送者信息
        self.nickname = self.sender.get("nickname", "")  # 昵称

    async def handle(self):
        """
        处理私聊消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                # 鉴权
                if not is_system_admin(self.user_id):
                    logger.error(f"[{MODULE_NAME}]{self.user_id}无权限切换私聊开关")
                    return
                await handle_module_private_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.user_id,
                    self.message_id,
                )
                return

            # 处理菜单命令（无视开关状态）
            if self.raw_message.lower() == f"{SWITCH_NAME}{MENU_COMMAND}".lower():
                menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(menu_text),
                    ],
                    note="del_msg=30",
                )
                return

            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            # 新增：根据sub_type判断消息类型
            if self.sub_type == "friend":
                # 处理好友私聊消息
                # 存储教务账号密码
                if self.raw_message.lower() == SAVE_JW_ACCOUNT_COMMAND.lower():
                    # 存储教务账号密码
                    # 鉴权
                    if not is_system_admin(self.user_id):
                        logger.error(
                            f"[{MODULE_NAME}]{self.user_id}无权限存储教务账号密码"
                        )
                        return
                    # 存储教务账号密码
                    # 分离参数
                    params = self.raw_message.split(" ")
                    if len(params) != 3:
                        logger.error(
                            f"[{MODULE_NAME}]存储教务账号密码参数错误: {self.raw_message}"
                        )
                        return
                    # 存储教务账号密码
                    with DataManager() as dm:
                        dm.save_credential(params[1], params[2])
                        await send_private_msg(
                            self.websocket,
                            self.user_id,
                            [
                                generate_reply_message(self.message_id),
                                generate_text_message(
                                    f"[{MODULE_NAME}]存储教务账号密码成功: {params[1]} {params[2]}"
                                ),
                            ],
                            note="del_msg=30",
                        )
                        return
            elif self.sub_type == "group":
                # 处理临时会话消息（如群临时会话）
                with DataManager() as dm:
                    # 这里可以进行数据库操作，如：dm.cursor.execute(...)
                    pass
            else:
                # 其他类型的私聊消息
                logger.info(
                    f"[{MODULE_NAME}]收到未知sub_type的私聊消息: {self.sub_type}"
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")

from . import MODULE_NAME, SWITCH_NAME, MENU_COMMAND
from . import (
    CMD_SET_REGEX,
    CMD_GET_REGEX,
    CMD_DEL_REGEX,
    CMD_SET_DEFAULT,
    CMD_GET_DEFAULT,
    CMD_SET_LOCK,
    CMD_GET_LOCK,
    CMD_DEL_LOCK,
)
import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from api.message import send_group_msg
from api.generate import (
    generate_reply_message,
    generate_text_message,
    generate_at_message,
)
from api.group import set_group_card
from datetime import datetime
from .data_manager import DataManager
import re
from core.auth import is_group_admin, is_system_owner
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

    async def handle(self):
        """
        处理群消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                # 鉴权
                if not is_system_owner(self.user_id):
                    return
                await handle_module_group_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.group_id,
                    self.message_id,
                )
                return

            # 处理菜单命令（无视开关状态）
            if self.raw_message.lower() == (SWITCH_NAME + MENU_COMMAND).lower():
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

            with DataManager() as dm:
                # 权限判断函数
                def is_admin():
                    return is_group_admin(self.role)

                # 管理命令处理（仅群主/管理员）
                if self.raw_message.startswith(
                    (
                        CMD_SET_REGEX,
                        CMD_GET_REGEX,
                        CMD_DEL_REGEX,
                        CMD_SET_DEFAULT,
                        CMD_GET_DEFAULT,
                        CMD_SET_LOCK,
                        CMD_GET_LOCK,
                        CMD_DEL_LOCK,
                    )
                ):
                    if not is_admin():
                        return

                if self.raw_message.startswith(CMD_SET_REGEX):
                    regex = self.raw_message[len(CMD_SET_REGEX) :].strip()
                    # 只处理英文中括号的Unicode
                    regex = regex.replace(r"&#91;", "[").replace(r"&#93;", "]")
                    dm.set_group_regex(self.group_id, regex)
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(f"群正则已设置为: {regex}"),
                        ],
                        note="del_msg=10",
                    )
                    return
                elif self.raw_message.startswith(CMD_GET_REGEX):
                    regex = dm.get_group_regex(self.group_id)
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"当前群正则: {regex if regex else '未设置'}"
                            ),
                        ],
                        note="del_msg=10",
                    )
                    return
                elif self.raw_message.startswith(CMD_DEL_REGEX):
                    dm.del_group_regex(self.group_id)
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message("群正则已删除"),
                        ],
                        note="del_msg=10",
                    )
                    return
                elif self.raw_message.startswith(CMD_SET_DEFAULT):
                    default_name = self.raw_message[len(CMD_SET_DEFAULT) :].strip()
                    dm.set_group_default_name(self.group_id, default_name)
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(f"群默认名已设置为: {default_name}"),
                        ],
                        note="del_msg=10",
                    )
                    return
                elif self.raw_message.startswith(CMD_GET_DEFAULT):
                    default_name = dm.get_group_default_name(self.group_id)
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"当前群默认名: {default_name if default_name else '未设置'}"
                            ),
                        ],
                        note="del_msg=10",
                    )
                    return
                elif self.raw_message.startswith(CMD_SET_LOCK):
                    # 格式: 锁定昵称 QQ号 昵称
                    args = self.raw_message[len(CMD_SET_LOCK) :].strip().split()
                    if len(args) >= 2:
                        user_id, lock_name = args[0], " ".join(args[1:])
                        dm.set_user_lock_name(self.group_id, user_id, lock_name)
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [
                                generate_reply_message(self.message_id),
                                generate_text_message(
                                    f"已锁定{user_id}昵称为: {lock_name}"
                                ),
                            ],
                            note="del_msg=10",
                        )
                    else:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [
                                generate_reply_message(self.message_id),
                                generate_text_message(
                                    "格式错误，应为: 锁定昵称 QQ号 昵称"
                                ),
                            ],
                            note="del_msg=10",
                        )
                    return
                elif self.raw_message.startswith(CMD_GET_LOCK):
                    locks = dm.get_all_user_locks(self.group_id)
                    if locks:
                        msg = "锁定昵称列表:\n" + "\n".join(
                            [f"{u}: {n}" for u, n in locks]
                        )
                    else:
                        msg = "无锁定昵称"
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(msg),
                        ],
                        note="del_msg=10",
                    )
                    return
                elif self.raw_message.startswith(CMD_DEL_LOCK):
                    # 格式: 删除锁定 QQ号
                    args = self.raw_message[len(CMD_DEL_LOCK) :].strip().split()
                    if len(args) >= 1:
                        user_id = args[0]
                        dm.del_user_lock_name(self.group_id, user_id)
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [
                                generate_reply_message(self.message_id),
                                generate_text_message(f"已删除{user_id}的锁定昵称"),
                            ],
                            note="del_msg=10",
                        )
                    else:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [
                                generate_reply_message(self.message_id),
                                generate_text_message("格式错误，应为: 删除锁定 QQ号"),
                            ],
                            note="del_msg=10",
                        )
                    return

                # --- 核心昵称检测逻辑 ---
                # 1. 检查用户锁定昵称（优先级高）
                lock_name = dm.get_user_lock_name(self.group_id, self.user_id)
                if lock_name and self.card != lock_name:
                    await set_group_card(
                        self.websocket, self.group_id, self.user_id, lock_name
                    )
                    logger.info(
                        f"[{MODULE_NAME}]用户{self.user_id}群名片不符锁定，已自动改为: {lock_name}"
                    )
                    return
                # 2. 检查群正则
                regex = dm.get_group_regex(self.group_id)
                if regex:
                    try:
                        if not re.fullmatch(regex, self.card):
                            # 检查提醒时间间隔
                            from . import NICKNAME_REMINDER_INTERVAL_SECONDS
                            import time

                            last_remind = dm.get_last_nickname_reminder_at(
                                self.group_id, self.user_id
                            )
                            now = time.time()
                            if (
                                last_remind is None
                                or now - last_remind
                                > NICKNAME_REMINDER_INTERVAL_SECONDS
                            ):
                                # 发送提醒
                                await send_group_msg(
                                    self.websocket,
                                    self.group_id,
                                    [
                                        generate_at_message(self.user_id),
                                        generate_text_message(
                                            f"{self.user_id}您的群昵称不符合群规定，请及时修改为群公告的指定格式！"
                                        ),
                                    ],
                                    note="del_msg=10",
                                )
                                # 更新提醒时间
                                dm.set_last_nickname_reminder_at(
                                    self.group_id, self.user_id, now
                                )
                            default_name = dm.get_group_default_name(self.group_id)
                            if default_name:
                                await set_group_card(
                                    self.websocket,
                                    self.group_id,
                                    self.user_id,
                                    default_name,
                                )
                                logger.info(
                                    f"[{MODULE_NAME}]用户{self.user_id}群名片不符正则，已自动改为默认名: {default_name}"
                                )
                                return
                    except Exception as e:
                        logger.error(f"[{MODULE_NAME}]正则检测异常: {e}")

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

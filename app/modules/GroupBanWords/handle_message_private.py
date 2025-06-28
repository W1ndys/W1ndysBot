from . import (
    MODULE_NAME,
    SWITCH_NAME,
    UNBAN_WORD_COMMAND,
    KICK_BAN_WORD_COMMAND,
    ADD_GLOBAL_BAN_WORD_COMMAND,
    DELETE_GLOBAL_BAN_WORD_COMMAND,
    COPY_BAN_WORD_COMMAND,
)
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_private_switch_on, handle_module_private_switch
from api.message import send_private_msg, get_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime
from .data_manager_words import DataManager
from core.auth import is_system_admin
from core.menu_manager import MenuManager
from .handle_GroupBanWords import GroupBanWordsHandler
import asyncio
import re


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

    async def copy_ban_word_private(self):
        """
        私聊复制违禁词功能
        用法：复制违禁词 来源群号 目标群号
        """
        try:
            # 鉴权
            if not is_system_admin(self.user_id):
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [generate_text_message("权限不足，只有系统管理员可以执行此操作")],
                )
                return

            # 过滤命令
            content = self.raw_message.lstrip(COPY_BAN_WORD_COMMAND).strip()
            # 检查参数是否完整
            parts = content.split()
            if len(parts) != 2:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_text_message(
                            f"格式错误，正确用法：{COPY_BAN_WORD_COMMAND} 来源群号 目标群号"
                        ),
                    ],
                )
                return

            # 获取来源群号和目标群号
            source_group_id = parts[0]
            target_group_id = parts[1]

            # 实例化来源群数据管理器
            with DataManager(source_group_id) as source_dm:
                # 获取来源群违禁词
                ban_words = source_dm.get_all_words_and_weight()

            if not ban_words:
                source_name = (
                    "全局词库" if source_group_id == "0" else f"群 {source_group_id}"
                )
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_text_message(f"来源{source_name}没有违禁词数据"),
                    ],
                )
                return

            # 发送开始处理的提示
            source_name = (
                "全局词库" if source_group_id == "0" else f"群 {source_group_id}"
            )
            target_name = (
                "全局词库" if target_group_id == "0" else f"群 {target_group_id}"
            )
            await send_private_msg(
                self.websocket,
                self.user_id,
                [
                    generate_text_message(
                        f"开始从{source_name}复制 {len(ban_words)} 个违禁词到{target_name}，请稍候..."
                    ),
                ],
            )

            # 创建一个异步任务来处理违禁词添加，避免阻塞主线程
            async def process_ban_words():
                try:
                    with DataManager(target_group_id) as target_dm:
                        success_count = 0
                        batch_size = 20  # 每批处理20个违禁词

                        for i in range(0, len(ban_words), batch_size):
                            batch = ban_words[i : i + batch_size]

                            # 处理当前批次
                            for word, weight in batch:
                                if target_dm.add_word(word, weight):
                                    success_count += 1

                            # 每处理一批后让出控制权，防止阻塞
                            await asyncio.sleep(0.1)

                            # 发送进度更新（可选）
                            if len(ban_words) > 50:  # 只有在词数较多时才发送进度
                                processed = min(i + batch_size, len(ban_words))
                                progress = int(processed / len(ban_words) * 100)
                                if progress % 25 == 0:  # 每25%发送一次进度
                                    await send_private_msg(
                                        self.websocket,
                                        self.user_id,
                                        [
                                            generate_text_message(
                                                f"复制进度: {progress}% ({processed}/{len(ban_words)})"
                                            ),
                                        ],
                                    )

                    # 发送完成消息
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [
                            generate_text_message(
                                f"复制完成！已成功从{source_name}复制 {success_count}/{len(ban_words)} 个违禁词到{target_name}"
                            ),
                        ],
                    )

                except Exception as e:
                    logger.error(f"[{MODULE_NAME}]处理违禁词批次时出错: {e}")
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [
                            generate_text_message(f"复制过程中发生错误：{str(e)}"),
                        ],
                    )

            # 创建任务但不等待它完成，让它在后台运行
            asyncio.create_task(process_ban_words())

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]私聊复制违禁词失败: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [
                    generate_text_message(f"复制违禁词时发生错误：{str(e)}"),
                ],
            )

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

            # 实例化GroupBanWords，使用群号"0"表示私聊环境下的全局操作
            group_ban_words = GroupBanWordsHandler(
                self.websocket, {**self.msg, "group_id": "0"}
            )
            # 处理管理员解封 踢出
            if self.raw_message.lower().startswith(UNBAN_WORD_COMMAND.lower()):
                await group_ban_words.handle_unban_word()
            elif self.raw_message.lower().startswith(KICK_BAN_WORD_COMMAND.lower()):
                await group_ban_words.handle_kick_ban_word()
            # 处理全局违禁词管理
            elif self.raw_message.lower().startswith(
                ADD_GLOBAL_BAN_WORD_COMMAND.lower()
            ):
                await group_ban_words.add_global_ban_word()
            elif self.raw_message.lower().startswith(
                DELETE_GLOBAL_BAN_WORD_COMMAND.lower()
            ):
                await group_ban_words.delete_global_ban_word()
            # 处理私聊复制违禁词
            elif self.raw_message.lower().startswith(COPY_BAN_WORD_COMMAND.lower()):
                await self.copy_ban_word_private()

            # 新的解封踢出功能
            # 原消息内容: [CQ:reply,id=1734368035]{命令}，通过消息ID获取消息内容，进而解析用户ID，群号
            if self.raw_message.startswith("[CQ:reply,id=") and (
                UNBAN_WORD_COMMAND in self.raw_message
                or KICK_BAN_WORD_COMMAND in self.raw_message
            ):
                # 正则提取消息ID
                pattern = r"\[CQ:reply,id=(\d+)\]"
                match = re.search(pattern, self.raw_message)
                if match:
                    message_id = match.group(1)
                else:
                    logger.error(f"[{MODULE_NAME}]提取消息ID失败")
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message("提取消息ID失败")],
                    )
                    return
                # 发送API获取消息内容，备注：{对应命令}，便于ResponseHandler处理
                await get_msg(
                    self.websocket,
                    message_id,
                    note=f"{MODULE_NAME}-action={KICK_BAN_WORD_COMMAND if KICK_BAN_WORD_COMMAND in self.raw_message else UNBAN_WORD_COMMAND}",
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")

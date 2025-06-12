import asyncio
from datetime import datetime
from . import (
    MODULE_NAME,
    ADD_BAN_WORD_COMMAND,
    DELETE_BAN_WORD_COMMAND,
    BAN_WORD_WEIGHT_MAX,
    BAN_WORD_DURATION,
    UNBAN_WORD_COMMAND,
    KICK_BAN_WORD_COMMAND,
    COPY_BAN_WORD_COMMAND,
)
from .data_manager_words import DataManager
from .ban_words_utils import check_and_handle_ban_words
from logger import logger
from core.auth import is_group_admin, is_system_admin
from api.message import send_group_msg, delete_msg, send_private_msg, get_forward_msg
from api.generate import (
    generate_text_message,
    generate_reply_message,
    generate_at_message,
)
from api.group import set_group_ban, set_group_kick
from config import OWNER_ID
from utils.feishu import send_feishu_msg


class GroupBanWordsHandler:
    def __init__(self, websocket, msg):
        self.websocket = websocket
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
        self.data_manager = DataManager(self.group_id)

    async def handle_unban_word(self):
        try:
            # 检测是否为管理员
            if not is_system_admin(self.user_id):
                return
            # 过滤命令
            self.raw_message = self.raw_message.lstrip(UNBAN_WORD_COMMAND).strip()
            # 获取群号
            banned_group_id = self.raw_message.split(" ")[0]
            # 获取被封禁用户ID
            banned_user_id = self.raw_message.split(" ")[1]
            # 解封用户
            await set_group_ban(
                self.websocket,
                banned_group_id,
                banned_user_id,
                0,
            )
            # 更新用户状态为已解封
            self.data_manager.set_user_status(banned_user_id, "unban")
            # 发送成功消息
            await send_group_msg(
                self.websocket,
                banned_group_id,
                [
                    generate_at_message(banned_user_id),
                    generate_text_message(f"({banned_user_id})你被管理员解除禁言"),
                ],
                note="del_msg=10",
            )
            # 发送管理员私聊消息
            await send_private_msg(
                self.websocket,
                OWNER_ID,
                [
                    generate_text_message(
                        f"群{banned_group_id}用户({banned_user_id})因发送违禁词被封禁，已被管理员解除禁言"
                    ),
                ],
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]解封用户失败: {e}")

    async def handle_kick_ban_word(self):
        try:
            # 检测是否为管理员
            if not is_system_admin(self.user_id):
                return
            # 过滤命令
            ban_word = self.raw_message.lstrip(KICK_BAN_WORD_COMMAND).strip()
            # 获取被封禁用户ID
            banned_user_id = ban_word.split(" ")[1]
            # 获取群号
            banned_group_id = ban_word.split(" ")[0]
            # 更新用户状态为已踢出
            self.data_manager.set_user_status(banned_user_id, "kick")
            # 发送成功消息
            await send_group_msg(
                self.websocket,
                banned_group_id,
                [
                    generate_at_message(banned_user_id),
                    generate_text_message(
                        f"({banned_user_id})你将因发送违禁消息被管理员踢出群"
                    ),
                ],
                note="del_msg=10",
            )
            # 踢出用户
            await asyncio.sleep(0.3)
            await set_group_kick(
                self.websocket,
                banned_group_id,
                banned_user_id,
            )
            # 发送管理员私聊消息
            await asyncio.sleep(0.3)
            await send_private_msg(
                self.websocket,
                OWNER_ID,
                [
                    generate_text_message(
                        f"群{banned_group_id}用户({banned_user_id})发送违禁词，已被管理员踢出群"
                    ),
                ],
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]踢出用户失败: {e}")

    async def add_ban_word(self):
        try:
            if not is_group_admin(self.role):
                return
            # 过滤命令
            content = self.raw_message.lstrip(ADD_BAN_WORD_COMMAND).strip()
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            results = []
            # 判断是否批量
            if len(lines) > 1:
                for line in lines:
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) == 2:
                        word, weight = parts
                    elif len(parts) == 1:
                        word, weight = parts[0], 10
                    else:
                        results.append(f"格式错误: {line}")
                        continue
                    is_success = self.data_manager.add_word(word, weight)
                    if is_success:
                        results.append(f"添加成功: {word} 权重: {weight}")
                    else:
                        results.append(f"添加失败: {word}")
                reply = "\n".join(results)
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(reply),
                    ],
                    note="del_msg=10",
                )
            else:
                # 单条兼容原有逻辑
                ban_word = content
                if not ban_word:
                    return
                parts = ban_word.split()
                if len(parts) == 2:
                    word, weight = parts
                elif len(parts) == 1:
                    word, weight = parts[0], 10
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(f"格式错误: {ban_word}"),
                        ],
                        note="del_msg=10",
                    )
                    return
                is_success = self.data_manager.add_word(word, weight)
                if not is_success:
                    return
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(f"添加违禁词成功: {word} 权重: {weight}"),
                    ],
                    note="del_msg=10",
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加违禁词失败: {e}")

    async def delete_ban_word(self):
        try:
            if not is_group_admin(self.role):
                return
            # 过滤命令
            content = self.raw_message.lstrip(DELETE_BAN_WORD_COMMAND).strip()
            words = [w for w in content.split() if w]
            results = []
            if len(words) > 1:
                for word in words:
                    is_success = self.data_manager.delete_word(word)
                    if is_success:
                        results.append(f"删除成功: {word}")
                    else:
                        results.append(f"未找到: {word}")
                reply = "\n".join(results)
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(reply),
                    ],
                    note="del_msg=10",
                )
            else:
                # 单条兼容原有逻辑
                ban_word = content
                if not ban_word:
                    return
                is_success = self.data_manager.delete_word(ban_word)
                if not is_success:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(f"未找到: {ban_word}"),
                        ],
                        note="del_msg=10",
                    )
                    return
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(f"删除违禁词成功: {ban_word}"),
                    ],
                    note="del_msg=10",
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]删除违禁词失败: {e}")

    async def check_and_handle_ban_words(self):
        """检测违禁词并处理相关逻辑"""

        # 如果是群管理，则不处理
        if is_group_admin(self.role):
            return

        # 如果消息是转发消息，发送获取转发消息内容的请求
        if self.raw_message.startswith("[CQ:forward,id="):
            await get_forward_msg(
                self.websocket,
                self.message_id,
                note=f"{MODULE_NAME}-group_id={self.group_id}-user_id={self.user_id}-message_id={self.message_id}",
            )
            logger.info(
                f"[{MODULE_NAME}]已发送获取转发消息内容的请求, 群号: {self.group_id}, 发送者QQ号: {self.user_id}, 消息ID: {self.message_id}"
            )
            return

        # 使用提取的通用函数检测和处理违禁词
        return await check_and_handle_ban_words(
            self.websocket,
            self.data_manager,
            self.group_id,
            self.user_id,
            self.message_id,
            self.raw_message,
            self.formatted_time,
        )

    async def copy_ban_word(self):
        """
        复制违禁词到当前群
        用法：私聊：复制违禁词 群号1(把群号1的违禁词复制到当前群)
        群聊：复制违禁词 群号1(把群号1的违禁词复制到当前群)
        """
        try:
            # 鉴权
            if not is_system_admin(self.user_id):
                return
            # 过滤命令
            content = self.raw_message.lstrip(COPY_BAN_WORD_COMMAND).strip()
            # 检查参数是否完整
            parts = content.split()
            if len(parts) < 1:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_text_message(
                            f"格式错误，正确用法：{COPY_BAN_WORD_COMMAND} 来源群号"
                        ),
                    ],
                )
                return
            # 获取来源群号（群号1）
            group_id_source = parts[0]
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_text_message(f"正在从群 {group_id_source} 复制违禁词"),
                ],
                note="del_msg=10",
            )
            # 实例化来源群数据管理器
            data_manager_source = DataManager(group_id_source)
            # 获取来源群违禁词
            ban_words = data_manager_source.get_all_words_and_weight()
            # 添加违禁词到本群
            for word, weight in ban_words:
                self.data_manager.add_word(word, weight)
            # 发送成功消息
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_text_message(
                        f"已成功从群 {group_id_source} 复制 {len(ban_words)} 个违禁词"
                    ),
                ],
                note="del_msg=10",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]复制违禁词失败: {e}")

    async def handle(self):
        try:
            # 添加违禁词
            if self.raw_message.startswith(ADD_BAN_WORD_COMMAND):
                await self.add_ban_word()
                return
            # 删除违禁词
            if self.raw_message.startswith(DELETE_BAN_WORD_COMMAND):
                await self.delete_ban_word()
                return

            # 复制违禁词
            if self.raw_message.startswith(COPY_BAN_WORD_COMMAND):
                await self.copy_ban_word()
                return

            # 检测违禁词
            if await self.check_and_handle_ban_words():
                return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理违禁词失败: {e}")

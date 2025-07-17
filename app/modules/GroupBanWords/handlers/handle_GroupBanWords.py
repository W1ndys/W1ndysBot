import asyncio
from datetime import datetime
import re
from .. import (
    MODULE_NAME,
    ADD_BAN_WORD_COMMAND,
    DELETE_BAN_WORD_COMMAND,
    ADD_GLOBAL_BAN_WORD_COMMAND,
    DELETE_GLOBAL_BAN_WORD_COMMAND,
    UNBAN_WORD_COMMAND,
    KICK_BAN_WORD_COMMAND,
    COPY_BAN_WORD_COMMAND,
    ADD_BAN_SAMPLE_COMMAND,
    DELETE_BAN_SAMPLE_COMMAND,
    LIST_BAN_SAMPLES_COMMAND,
)
from .data_manager_words import DataManager
from .ban_words_utils import check_and_handle_ban_words
from logger import logger
from utils.auth import is_group_admin, is_system_admin
from api.message import (
    send_group_msg,
    delete_msg,
    send_private_msg,
    get_forward_msg,
    get_msg,
)
from utils.generate import (
    generate_text_message,
    generate_reply_message,
    generate_at_message,
)
from api.group import set_group_ban, set_group_kick
from config import OWNER_ID
from utils.feishu import send_feishu_msg
import base64


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

        # 判断是否在私聊环境（group_id为"0"表示私聊环境）
        self.is_private = self.group_id == "0"

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
            self.data_manager.set_user_status(banned_user_id, "kick", banned_group_id)
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
            # 在私聊中，任何系统管理员都可以添加全局违禁词
            # 在群聊中，群管理员和系统管理员可以添加群专属违禁词
            if self.is_private:
                if not is_system_admin(self.user_id):
                    return
                # 私聊中使用全局词库的DataManager
                data_manager = DataManager(DataManager.GLOBAL_GROUP_ID)
                word_type = "全局违禁词"
            else:
                if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                    return
                data_manager = self.data_manager
                word_type = "违禁词"

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
                    is_success = data_manager.add_word(word, weight)
                    if is_success:
                        results.append(f"添加{word_type}成功: {word} 权重: {weight}")
                    else:
                        results.append(f"添加{word_type}失败: {word}")
                reply = "\n".join(results)

                # 根据环境选择发送方式
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(reply)],
                    )
                else:
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
                    error_msg = f"格式错误: {ban_word}"
                    if self.is_private:
                        await send_private_msg(
                            self.websocket,
                            self.user_id,
                            [generate_text_message(error_msg)],
                        )
                    else:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [
                                generate_reply_message(self.message_id),
                                generate_text_message(error_msg),
                            ],
                            note="del_msg=10",
                        )
                    return
                is_success = data_manager.add_word(word, weight)
                if not is_success:
                    return

                success_msg = f"添加{word_type}成功: 【{word}】 权重: 【{weight}】"
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(success_msg)],
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(success_msg),
                        ],
                        note="del_msg=10",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加违禁词失败: {e}")

    async def delete_ban_word(self):
        try:
            # 在私聊中，任何系统管理员都可以删除全局违禁词
            # 在群聊中，群管理员和系统管理员可以删除群专属违禁词
            if self.is_private:
                if not is_system_admin(self.user_id):
                    return
                # 私聊中使用全局词库的DataManager
                data_manager = DataManager(DataManager.GLOBAL_GROUP_ID)
                word_type = "全局违禁词"
            else:
                if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                    return
                data_manager = self.data_manager
                word_type = "违禁词"

            # 过滤命令
            content = self.raw_message.lstrip(DELETE_BAN_WORD_COMMAND).strip()
            words = [w for w in content.split() if w]
            results = []
            if len(words) > 1:
                for word in words:
                    is_success = data_manager.delete_word(word)
                    if is_success:
                        results.append(f"删除{word_type}成功: {word}")
                    else:
                        results.append(f"未找到{word_type}: {word}")
                reply = "\n".join(results)

                # 根据环境选择发送方式
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(reply)],
                    )
                else:
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
                is_success = data_manager.delete_word(ban_word)
                if not is_success:
                    error_msg = f"未找到{word_type}: 【{ban_word}】"
                    if self.is_private:
                        await send_private_msg(
                            self.websocket,
                            self.user_id,
                            [generate_text_message(error_msg)],
                        )
                    else:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [
                                generate_reply_message(self.message_id),
                                generate_text_message(error_msg),
                            ],
                            note="del_msg=10",
                        )
                    return

                success_msg = f"删除{word_type}成功: 【{ban_word}】"
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(success_msg)],
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(success_msg),
                        ],
                        note="del_msg=10",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]删除违禁词失败: {e}")

    async def add_global_ban_word(self):
        try:
            # 鉴权，只有系统管理员可以添加全局违禁词
            if not is_system_admin(self.user_id):
                return

            # 使用全局词库的DataManager（群号"0"）
            global_data_manager = DataManager(DataManager.GLOBAL_GROUP_ID)

            # 过滤命令
            content = self.raw_message.lstrip(ADD_GLOBAL_BAN_WORD_COMMAND).strip()
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
                    is_success = global_data_manager.add_word(word, weight)
                    if is_success:
                        results.append(f"添加成功: {word} 权重: {weight}")
                    else:
                        results.append(f"添加失败: {word}")
                reply = "\n".join(results)

                # 根据环境选择发送方式
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(reply)],
                    )
                else:
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
                    error_msg = f"格式错误: {ban_word}"
                    if self.is_private:
                        await send_private_msg(
                            self.websocket,
                            self.user_id,
                            [generate_text_message(error_msg)],
                        )
                    else:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [
                                generate_reply_message(self.message_id),
                                generate_text_message(error_msg),
                            ],
                            note="del_msg=10",
                        )
                    return
                is_success = global_data_manager.add_word(word, weight)
                if not is_success:
                    return

                success_msg = f"添加全局违禁词成功: {word} 权重: {weight}"
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(success_msg)],
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(success_msg),
                        ],
                        note="del_msg=10",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加全局违禁词失败: {e}")

    async def delete_global_ban_word(self):
        try:
            # 鉴权，只有系统管理员可以删除全局违禁词
            if not is_system_admin(self.user_id):
                return

            # 使用全局词库的DataManager（群号"0"）
            global_data_manager = DataManager(DataManager.GLOBAL_GROUP_ID)

            # 过滤命令
            content = self.raw_message.lstrip(DELETE_GLOBAL_BAN_WORD_COMMAND).strip()
            words = [w for w in content.split() if w]
            results = []
            if len(words) > 1:
                for word in words:
                    is_success = global_data_manager.delete_word(word)
                    if is_success:
                        results.append(f"删除成功: {word}")
                    else:
                        results.append(f"未找到: {word}")
                reply = "\n".join(results)

                # 根据环境选择发送方式
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(reply)],
                    )
                else:
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
                is_success = global_data_manager.delete_word(ban_word)
                if not is_success:
                    error_msg = f"未找到: {ban_word}"
                    if self.is_private:
                        await send_private_msg(
                            self.websocket,
                            self.user_id,
                            [generate_text_message(error_msg)],
                        )
                    else:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [
                                generate_reply_message(self.message_id),
                                generate_text_message(error_msg),
                            ],
                            note="del_msg=10",
                        )
                    return

                success_msg = f"删除全局违禁词成功: {ban_word}"
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(success_msg)],
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(success_msg),
                        ],
                        note="del_msg=10",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]删除全局违禁词失败: {e}")

    async def add_ban_sample(self):
        """添加违禁样本"""
        try:
            # 在私聊中，任何系统管理员都可以添加全局违禁样本
            # 在群聊中，群管理员和系统管理员可以添加群专属违禁样本
            if self.is_private:
                if not is_system_admin(self.user_id):
                    return
                # 私聊中使用全局样本库的DataManager
                data_manager = DataManager(DataManager.GLOBAL_GROUP_ID)
                sample_type = "全局违禁样本"
            else:
                if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                    return
                data_manager = self.data_manager
                sample_type = "违禁样本"

            # 过滤命令
            content = self.raw_message.lstrip(ADD_BAN_SAMPLE_COMMAND).strip()

            if not content:
                error_msg = "请提供Base64编码的样本内容"
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(error_msg)],
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(error_msg),
                        ],
                        note="del_msg=10",
                    )
                return

            try:
                # 解码base64
                decoded_bytes = base64.b64decode(content)

                # 尝试多种编码方式解码
                sample_text = None
                encoding_attempts = [
                    "utf-8",
                ]

                for encoding in encoding_attempts:
                    try:
                        sample_text = decoded_bytes.decode(encoding)
                        logger.info(f"[{MODULE_NAME}]成功使用{encoding}编码解码样本")
                        break
                    except UnicodeDecodeError:
                        continue

                if sample_text is None:
                    # 如果所有编码都失败，使用错误处理方式
                    sample_text = decoded_bytes.decode("utf-8", errors="replace")
                    logger.warning(
                        f"[{MODULE_NAME}]使用替换模式解码样本，可能存在字符丢失"
                    )

            except Exception as e:
                error_msg = f"Base64解码失败: {str(e)}\n请确保提供的是有效的Base64编码"
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(error_msg)],
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(error_msg),
                        ],
                        note="del_msg=10",
                    )
                return

            # 验证解码后的内容
            if not sample_text or len(sample_text.strip()) == 0:
                error_msg = "解码后的样本内容为空"
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(error_msg)],
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(error_msg),
                        ],
                        note="del_msg=10",
                    )
                return

            # 添加样本
            is_success = data_manager.add_sample(sample_text.strip(), 10)
            if is_success:
                success_msg = f"添加{sample_type}成功\n样本内容: {sample_text[:50]}{'...' if len(sample_text) > 50 else ''}"
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(success_msg)],
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(success_msg),
                        ],
                        note="del_msg=10",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加违禁样本失败: {e}")

    async def delete_ban_sample(self):
        """删除违禁样本"""
        try:
            # 权限检查逻辑同add_ban_sample
            if self.is_private:
                if not is_system_admin(self.user_id):
                    return
                data_manager = DataManager(DataManager.GLOBAL_GROUP_ID)
                sample_type = "全局违禁样本"
            else:
                if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                    return
                data_manager = self.data_manager
                sample_type = "违禁样本"

            # 过滤命令，获取样本文本（直接文本，不是base64）
            sample_text = self.raw_message.lstrip(DELETE_BAN_SAMPLE_COMMAND).strip()

            if not sample_text:
                return

            is_success = data_manager.delete_sample(sample_text)
            if is_success:
                success_msg = f"删除{sample_type}成功"
            else:
                success_msg = f"未找到该{sample_type}"

            if self.is_private:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [generate_text_message(success_msg)],
                )
            else:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(success_msg),
                    ],
                    note="del_msg=10",
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]删除违禁样本失败: {e}")

    async def list_ban_samples(self):
        """查看违禁样本列表"""
        try:
            # 权限检查
            if self.is_private:
                if not is_system_admin(self.user_id):
                    return
                data_manager = DataManager(DataManager.GLOBAL_GROUP_ID)
                sample_type = "全局违禁样本"
            else:
                if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                    return
                data_manager = self.data_manager
                sample_type = "违禁样本"

            samples = data_manager.get_all_samples()

            if not samples:
                msg = f"当前没有{sample_type}"
            else:
                sample_list = []
                for i, (sample_text, weight) in enumerate(samples, 1):
                    # 限制显示长度
                    display_text = (
                        sample_text[:30] + "..."
                        if len(sample_text) > 30
                        else sample_text
                    )
                    sample_list.append(f"{i}. {display_text} (权重: {weight})")

                msg = f"{sample_type}列表 (共{len(samples)}个):\n" + "\n".join(
                    sample_list
                )

            if self.is_private:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [generate_text_message(msg)],
                )
            else:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(msg),
                    ],
                    note="del_msg=30",
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]查看违禁样本失败: {e}")

    async def check_and_handle_ban_words(self):
        """检测违禁词并处理相关逻辑"""

        # 如果是群管理或系统管理员，则不处理
        if is_group_admin(self.role) or is_system_admin(self.user_id):
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

            # 实例化来源群数据管理器
            with DataManager(group_id_source) as data_manager_source:
                # 获取来源群违禁词
                ban_words = data_manager_source.get_all_words_and_weight()

            if not ban_words:
                source_name = (
                    "全局词库" if group_id_source == "0" else f"群 {group_id_source}"
                )
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_text_message(f"来源{source_name}没有违禁词数据"),
                    ],
                    note="del_msg=10",
                )
                return

            # 发送开始处理的提示
            source_name = (
                "全局词库" if group_id_source == "0" else f"群 {group_id_source}"
            )
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_text_message(
                        f"开始从{source_name}复制{len(ban_words)}个违禁词到当前群，请稍候..."
                    ),
                ],
                note="del_msg=10",
            )

            # 创建一个新的异步任务来处理违禁词添加
            async def process_ban_words():
                try:
                    success_count = 0
                    batch_size = 20  # 每批处理20个违禁词

                    for i in range(0, len(ban_words), batch_size):
                        batch = ban_words[i : i + batch_size]

                        # 处理当前批次
                        for word, weight in batch:
                            if self.data_manager.add_word(word, weight):
                                success_count += 1

                        # 每处理一批后让出控制权，防止阻塞
                        await asyncio.sleep(0.1)

                    # 发送成功消息
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_text_message(
                                f"已成功从{source_name}复制 {success_count}/{len(ban_words)} 个违禁词"
                            )
                        ],
                        note="del_msg=10",
                    )
                except Exception as e:
                    logger.error(f"[{MODULE_NAME}]处理违禁词批次时出错: {e}")
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_text_message(f"复制过程中发生错误：{str(e)}"),
                        ],
                        note="del_msg=10",
                    )

            # 创建任务但不等待它完成
            asyncio.create_task(process_ban_words())

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]复制违禁词失败: {e}")

    async def handle(self):
        try:
            # 添加违禁词 - 私聊中添加全局违禁词，群聊中添加群专属违禁词
            if self.raw_message.startswith(ADD_BAN_WORD_COMMAND):
                await self.add_ban_word()
                return
            # 删除违禁词 - 私聊中删除全局违禁词，群聊中删除群专属违禁词
            if self.raw_message.startswith(DELETE_BAN_WORD_COMMAND):
                await self.delete_ban_word()
                return

            # 保留旧命令的兼容性（已废弃但仍可使用）
            if self.raw_message.startswith(ADD_GLOBAL_BAN_WORD_COMMAND):
                await self.add_global_ban_word()
                return
            if self.raw_message.startswith(DELETE_GLOBAL_BAN_WORD_COMMAND):
                await self.delete_global_ban_word()
                return

            # 添加违禁样本
            if self.raw_message.startswith(ADD_BAN_SAMPLE_COMMAND):
                await self.add_ban_sample()
                return

            # 删除违禁样本
            if self.raw_message.startswith(DELETE_BAN_SAMPLE_COMMAND):
                await self.delete_ban_sample()
                return

            # 查看违禁样本
            if self.raw_message.startswith(LIST_BAN_SAMPLES_COMMAND):
                await self.list_ban_samples()
                return

            # 处理群内的管理员解封踢出命令（群管理员和系统管理员可使用）
            if (
                self.raw_message.startswith("[CQ:reply,id=")
                and (
                    UNBAN_WORD_COMMAND in self.raw_message
                    or KICK_BAN_WORD_COMMAND in self.raw_message
                )
                and (is_group_admin(self.role) or is_system_admin(self.user_id))
            ):
                # 正则提取消息ID
                pattern = r"\[CQ:reply,id=(\d+)\]"
                match = re.search(pattern, self.raw_message)
                message_id = match.group(1) if match else None
                if message_id:
                    await get_msg(
                        self.websocket,
                        message_id,
                        note=f"{MODULE_NAME}-action={KICK_BAN_WORD_COMMAND if KICK_BAN_WORD_COMMAND in self.raw_message else UNBAN_WORD_COMMAND}",
                    )
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

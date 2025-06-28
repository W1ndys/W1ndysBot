import os
import logger
from . import (
    MODULE_NAME,
    ADD_FAQ,
    DELETE_FAQ,
    GET_FAQ,
    HIGH_THRESHOLD,
    LOW_THRESHOLD,
    MAX_SUGGESTIONS,
    DELETE_TIME,
)
from core.auth import is_group_admin, is_system_admin
from .db_manager import FAQDatabaseManager
from .handle_match_qa import AdvancedFAQMatcher
from api.message import send_group_msg, send_group_msg_with_cq, get_msg
from utils.generate import generate_reply_message, generate_text_message
import re
from utils.replace_rkey import replace_rkey


class QaHandler:
    def __init__(self, websocket, msg):
        """
        初始化 QaHandler 实例。

        参数:
            websocket: WebSocket 连接对象，用于发送消息。
            msg: dict，包含消息的详细信息，如原始消息、群号、用户ID等。
        """
        self.websocket = websocket
        self.msg = msg
        self.raw_message = msg.get("raw_message")
        self.group_id = str(msg.get("group_id"))
        self.user_id = str(msg.get("user_id"))
        self.message_id = str(msg.get("message_id"))
        self.sender = msg.get("sender", {})
        self.role = self.sender.get("role")

    async def handle(self):
        """
        处理群消息的主入口。

        根据消息内容判断是添加问答、删除问答对还是进行问答匹配，并调用相应的处理函数。
        """
        try:
            # 如果消息是添加问答命令，则调用添加问答函数
            if self.raw_message.startswith(ADD_FAQ):
                await self.handle_add_qa()
                return
            # 如果消息是删除问答对命令，则调用删除问答对函数
            if self.raw_message.startswith(DELETE_FAQ):
                await self.handle_delete_qa()
                return
            # 如果消息是获取问答命令，则调用获取问答函数
            if self.raw_message.startswith(GET_FAQ):
                await self.handle_get_qa()
                return
            # 如果是回复引用类型的添加问答，则调用API获取被回复的消息内容
            if (
                self.raw_message.startswith("[CQ:reply,id=")
                and ADD_FAQ in self.raw_message
            ):
                await self.handle_add_qa_by_reply()
                return

            # 否则，调用匹配问答对函数
            await self.handle_match_qa()  # type: ignore
            return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

    async def handle_add_qa_by_reply(self):
        """
        处理回复引用类型的添加问答命令。
        格式：[CQ:reply,id=xxxx][CQ:at,qq=xxxx] 命令前缀 问题
        示例： [CQ:reply,id=28070871][CQ:at,qq=3578392074] 添加问答 问答测试
        """
        try:
            # 删除所有[CQ:at,qq=xxxx]格式的艾特标记
            self.raw_message = re.sub(r"\[CQ:at,qq=\d+\]", "", self.raw_message)
            # 删除命令前缀，并去除空格
            self.raw_message = self.raw_message.replace(ADD_FAQ, "", 1).strip()
            # 正则提取要获取的回复消息的ID
            reply_message_id = re.search(r"\[CQ:reply,id=(\d+)\]", self.raw_message)
            if reply_message_id:
                reply_message_id = reply_message_id.group(1)
                logger.info(
                    f"[{MODULE_NAME}]回复引用类型的添加问答命令，获取到的回复消息ID：{reply_message_id}"
                )
            else:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            "❌ 添加失败，请检查问题格式。\n"
                            f"例如：\n引用一条消息，在消息后添加：{ADD_FAQ} 问题\n"
                        ),
                    ],
                    note="del_msg=10",
                )
            # 提取问题
            question = self.raw_message.split(" ", 1)[1].strip()

            if question:
                # 发送获取消息内容的API请求，把相关信息添加到echo字段
                await get_msg(
                    self.websocket,
                    reply_message_id,  # 被回复的消息ID
                    note=f"{MODULE_NAME}-group_id={self.group_id}-question={question}-reply_message_id={self.message_id}",  # 群号，问题，本条消息的消息ID(用于后续回复这条命令消息)
                )
            else:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            "❌ 添加失败，请检查问题格式。\n"
                            f"例如：\n引用一条消息，在消息后添加：{ADD_FAQ} 问题\n"
                        ),
                    ],
                    note="del_msg=10",
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理回复引用类型的添加问答命令失败: {e}")

    async def handle_add_qa(self):
        """
        处理添加问答命令。

        支持单条和批量添加。仅群管理员或系统拥有者可添加问答。添加成功后发送反馈消息。
        批量格式：
        添加命令
        问题1 答案1
        问题2 答案2

        单条格式：
        添加命令 问题 答案
        """
        matcher = None
        try:
            if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                return

            # 判断是否为批量添加（多行）
            lines = self.raw_message.strip().splitlines()
            matcher = AdvancedFAQMatcher(self.group_id)
            success_list = []
            fail_list = []

            if len(lines) > 1 and lines[0].startswith(ADD_FAQ):
                # 批量添加
                for idx, line in enumerate(lines[1:], 1):
                    line = line.strip()
                    if not line:
                        continue
                    # 按第一个空格分割为问题和答案
                    parts = line.split(" ", 1)
                    if len(parts) != 2:
                        fail_list.append(f"第{idx+1}行格式错误")
                        continue
                    question, answer = parts[0].strip(), parts[1].strip()
                    if not question or not answer:
                        fail_list.append(f"第{idx+1}行内容缺失")
                        continue
                    # 新增或更新
                    old_id = matcher.get_FAQ_id_by_question(question)
                    result_id = matcher.add_FAQ_pair(question, answer)
                    if result_id is not None:
                        if old_id != -1:
                            success_list.append(
                                f"━━━━━━━━━━━━━━\n"
                                f"🌟 问题：{question}\n"
                                f"🆔 ID：{str(result_id)}（更新成功）\n"
                            )
                        else:
                            success_list.append(
                                f"━━━━━━━━━━━━━━\n"
                                f"🌟 问题：{question}\n"
                                f"🆔 ID：{str(result_id)}（添加成功）\n"
                            )
                    else:
                        fail_list.append(
                            f"━━━━━━━━━━━━━━\n问题：{question}\n添加失败\n"
                        )
                # 组织反馈消息
                reply_msgs = [generate_reply_message(self.message_id)]
                if success_list:
                    reply_msgs.append(generate_text_message("✅ 批量添加成功：\n"))
                    for s in success_list:
                        reply_msgs.append(generate_text_message(s))
                if fail_list:
                    reply_msgs.append(generate_text_message("❌ 以下内容添加失败：\n"))
                    for f in fail_list:
                        reply_msgs.append(generate_text_message(f))
                reply_msgs.append(
                    generate_text_message("⏳ 消息将在20秒后撤回，请及时保存")
                )
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    reply_msgs,
                    note="del_msg=20",
                )
            else:
                # 单条添加
                # 去除命令前缀
                content = self.raw_message.replace(ADD_FAQ, "", 1).strip()
                parts = content.split(" ", 1)
                if len(parts) != 2:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"❗ 格式错误，应为：\n{ADD_FAQ} 问题 答案\n"
                                f"例如：\n{ADD_FAQ} 你好 你好呀\n"
                            ),
                            generate_text_message("⏳ 消息将在20秒后撤回，请及时保存"),
                        ],
                        note="del_msg=20",
                    )
                    return
                question, answer = parts[0].strip(), parts[1].strip()
                if not question or not answer:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"❗ 问题或答案不能为空，应为：\n{ADD_FAQ} 问题 答案\n"
                                f"例如：\n{ADD_FAQ} 你好 你好呀\n"
                            ),
                            generate_text_message("⏳ 消息将在20秒后撤回，请及时保存"),
                        ],
                        note="del_msg=20",
                    )
                    return
                # 新增或更新
                old_id = matcher.get_FAQ_id_by_question(question)
                result_id = matcher.add_FAQ_pair(question, answer)
                if result_id is not None:
                    if old_id != -1:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [
                                generate_reply_message(self.message_id),
                                generate_text_message("✅ 更新成功\n"),
                                generate_text_message(
                                    "━━━━━━━━━━━━━━\n"
                                    f"🌟 问题：{question}\n"
                                    f"💡 答案：{answer}\n"
                                    f"🆔 问答对ID：{str(result_id)}\n"
                                    "━━━━━━━━━━━━━━\n"
                                ),
                                generate_text_message(
                                    "⏳ 消息将在10秒后撤回，请及时保存"
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
                                generate_text_message("✅ 添加成功\n"),
                                generate_text_message(
                                    "━━━━━━━━━━━━━━\n"
                                    f"🌟 问题：{question}\n"
                                    f"💡 答案：{answer}\n"
                                    f"🆔 问答对ID：{str(result_id)}\n"
                                    "━━━━━━━━━━━━━━\n"
                                ),
                                generate_text_message(
                                    "⏳ 消息将在10秒后撤回，请及时保存"
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
                            generate_text_message("❌ 添加失败\n"),
                            generate_text_message("⏳ 消息将在20秒后撤回，请及时保存"),
                        ],
                        note="del_msg=20",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理添加问答命令失败: {e}")
        finally:
            if matcher is not None:
                pass  # 已不需要关闭db，由上下文管理器自动处理

    async def handle_delete_qa(self):
        """
        处理删除问答对命令，支持批量删除。
        格式：删除命令 id1 id2 ...，空格分隔多个ID
        """
        try:
            if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                return

            # 去除命令前缀
            content = self.raw_message.replace(DELETE_FAQ, "", 1).strip()
            if not content:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            "❗ 请提供要删除的问答对ID（可空格分隔多个ID）\n"
                            f"例如：\n{DELETE_FAQ} 1 2 3\n"
                        ),
                        generate_text_message("⏳ 消息将在10秒后撤回，请及时保存"),
                    ],
                    note="del_msg=10",
                )
                return

            # 支持批量删除，空格分隔
            id_strs = content.split()
            if not id_strs:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            "❗ 请提供要删除的问答对ID（可空格分隔多个ID）\n"
                            f"例如：\n{DELETE_FAQ} 1 2 3\n"
                        ),
                        generate_text_message("⏳ 消息将在10秒后撤回，请及时保存"),
                    ],
                    note="del_msg=10",
                )
                return

            matcher = AdvancedFAQMatcher(self.group_id)
            success_ids = []
            fail_ids = []
            for id_str in id_strs:
                try:
                    qa_id = int(id_str)
                    result = matcher.delete_FAQ_pair(qa_id)
                    if result:
                        success_ids.append(str(qa_id))
                    else:
                        fail_ids.append(str(qa_id))
                except Exception:
                    fail_ids.append(str(id_str))

            msg_list = [generate_reply_message(self.message_id)]
            if success_ids:
                msg_list.append(
                    generate_text_message(
                        "✅ 删除成功的ID：\n"
                        "━━━━━━━━━━━━━━\n"
                        f"{' '.join(success_ids)}\n"
                        "━━━━━━━━━━━━━━\n"
                        "⏳ 消息将在10秒后撤回，请及时保存"
                    )
                )
            if fail_ids:
                msg_list.append(
                    generate_text_message(
                        "❌ 删除失败的ID：\n"
                        "━━━━━━━━━━━━━━\n"
                        f"{' '.join(fail_ids)}\n"
                        "━━━━━━━━━━━━━━\n"
                        "⏳ 消息将在10秒后撤回，请及时保存"
                    )
                )
            if not success_ids and not fail_ids:
                msg_list.append(generate_text_message("未能识别要删除的问答对ID"))

            await send_group_msg(
                self.websocket,
                self.group_id,
                msg_list,
                note="del_msg=10",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理删除问答对命令失败: {e}")

    async def handle_get_qa(self):
        """
        处理获取问答命令。
        支持格式：获取问答 ID - 获取指定ID的问答对
        """
        try:
            # 去除命令前缀
            content = self.raw_message.replace(GET_FAQ, "", 1).strip()
            db_manager = FAQDatabaseManager(self.group_id)

            if not content:
                # 显示帮助信息和统计
                total_count = db_manager.get_FAQ_count()
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            f" 当前群组共有 {total_count} 个问答对\n"
                            f"🔍 使用方法：\n"
                            f"{GET_FAQ} ID - 获取指定ID的问答对\n"
                            f"直接发送相关问题"
                        ),
                    ],
                    note="del_msg=20",
                )
                return

            # 尝试解析为ID
            try:
                qa_id = int(content)
                # 获取指定ID的问答对
                result = db_manager.get_FAQ_pair(qa_id)
                if result:
                    qa_id, question, answer = result
                    # 处理答案中的转义换行符
                    answer = re.sub(r"\\n", "\n", answer)

                    # 处理答案中的图片rkey替换
                    answer = replace_rkey(answer)

                    await send_group_msg_with_cq(
                        self.websocket,
                        self.group_id,
                        f"[CQ:reply,id={self.message_id}]"
                        f"📖 问答详情\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"🌟 问题：{question}\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"💡 答案：{answer}\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"🆔 ID：{qa_id}\n"
                        f"⏳ 本消息将在{DELETE_TIME}秒后撤回，请及时保存",
                        note=f"del_msg={DELETE_TIME}",
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"❌ 未找到ID为 {qa_id} 的问答对\n"
                                f"⏳ 消息将在10秒后撤回，请及时保存"
                            ),
                        ],
                        note="del_msg=10",
                    )
            except ValueError:
                # 不是数字，提示格式错误
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            f"❌ 格式错误，请输入正确的问答ID\n"
                            f"例如：{GET_FAQ} 123\n"
                            f"⏳ 消息将在10秒后撤回，请及时保存"
                        ),
                    ],
                    note="del_msg=10",
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理获取问答命令失败: {e}")
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(
                        "❌ 获取问答失败，请稍后重试\n"
                        "⏳ 消息将在10秒后撤回，请及时保存"
                    ),
                ],
                note="del_msg=10",
            )

    async def handle_match_qa(self):
        """
        处理匹配问答对命令。

        根据收到的消息内容，在问答库中查找最相似的问题：
        - 相似度 >= HIGH_THRESHOLD：直接回复对应答案
        - LOW_THRESHOLD <= 相似度 < HIGH_THRESHOLD：显示相关问题引导
        - 相似度 < LOW_THRESHOLD：不回复
        """
        try:
            # 检查输入消息是否为空或只包含停用词
            if not self.raw_message or len(self.raw_message.strip()) == 0:
                return

            matcher = AdvancedFAQMatcher(self.group_id)
            matcher.build_index()

            try:
                orig_question, answer, score, qa_id = matcher.find_best_match(
                    self.raw_message
                )
            except ValueError as ve:
                logger.warning(f"[{MODULE_NAME}]文本分析失败: {ve}")
                return

            # 根据相似度阈值进行不同处理
            if score >= HIGH_THRESHOLD:
                # 高相似度：直接回复答案
                await self._send_direct_answer(orig_question, answer, score, qa_id)
            elif score >= LOW_THRESHOLD:
                # 中等相似度：显示相关问题引导
                await self._send_question_suggestions(matcher)
            else:
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理匹配问答对命令失败: {e}")

    async def _send_direct_answer(self, orig_question, answer, score, qa_id):
        """发送直接答案回复"""
        if answer is not None:
            # 如果答案中有被转义的换行，则替换为实际的换行
            answer = re.sub(r"\\n", "\n", answer)

            # 如果答案中有图片（包含rkey），则替换为本地缓存的rkey
            answer = replace_rkey(answer)

            # 直接回复答案（不显示原问题和相似度）
            await send_group_msg_with_cq(
                self.websocket,
                self.group_id,
                f"[CQ:reply,id={self.message_id}]"
                f"🌟 问题：{orig_question}\n"
                f"━━━━━━━━━━━━━━\n"
                f"💡 答案：{answer}\n"
                f"━━━━━━━━━━━━━━\n"
                f"📊 相似度：{score:.2f} 🆔ID:{qa_id}\n"
                f"⏳ 本消息将在{DELETE_TIME}秒后撤回，请及时保存",
                note=f"del_msg={DELETE_TIME}",
            )

    async def _send_question_suggestions(self, matcher):
        """发送相关问题引导"""
        try:
            # 获取所有高于低阈值的相关问题
            suggestions = matcher.find_multiple_matches(
                self.raw_message, min_score=LOW_THRESHOLD, max_results=MAX_SUGGESTIONS
            )

            if not suggestions:
                return

            # 构建引导消息
            msg_parts = [
                f"[CQ:reply,id={self.message_id}]",
                f"🤔 匹配到你可能想问如下问题，请发送具体的问题或使用命令“{GET_FAQ}+空格+ID”进行咨询：\n",
                "━━━━━━━━━━━━━━\n",
            ]

            for question, _, score, qa_id in suggestions:
                msg_parts.append(
                    f"ID:{qa_id}，问题：{question} (相似度: {score:.2f})\n"
                )

            msg_parts.append("━━━━━━━━━━━━━━\n")
            msg_parts.append(f"⏳ 本消息将在30秒后撤回，请及时保存")

            await send_group_msg_with_cq(
                self.websocket,
                self.group_id,
                "".join(msg_parts),
                note=f"del_msg=30",
            )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]发送问题建议失败: {e}")

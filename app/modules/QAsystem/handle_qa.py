import logger
from . import MODULE_NAME, ADD_QA, DELETE_QA
from core.auth import is_group_admin, is_system_owner
from .handle_match_qa import AdvancedQAMatcher
from api.message import send_group_msg, send_group_msg_with_cq
from api.generate import generate_reply_message, generate_text_message


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

        根据消息内容判断是添加问答对、删除问答对还是进行问答匹配，并调用相应的处理函数。
        """
        try:
            # 如果消息是添加问答对命令，则调用添加问答对函数
            if self.raw_message.startswith(ADD_QA):
                await self.handle_add_qa()
                return
            # 如果消息是删除问答对命令，则调用删除问答对函数
            if self.raw_message.startswith(DELETE_QA):
                await self.handle_delete_qa()
                return

            # 否则，调用匹配问答对函数
            await self.handle_match_qa()  # type: ignore

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

    async def handle_add_qa(self):
        """
        处理添加问答对命令。

        支持单条和批量添加。仅群管理员或系统拥有者可添加问答对。添加成功后发送反馈消息。
        批量格式：
        添加命令
        问题1 答案1
        问题2 答案2

        单条格式：
        添加命令 问题 答案
        """
        try:
            if not is_group_admin(self.role) and not is_system_owner(self.user_id):
                return

            # 判断是否为批量添加（多行）
            lines = self.raw_message.strip().splitlines()
            matcher = AdvancedQAMatcher(self.group_id)
            success_list = []
            fail_list = []

            if len(lines) > 1 and lines[0].startswith(ADD_QA):
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
                    result_id = matcher.add_qa_pair(question, answer)
                    if result_id is not None:
                        # 确保ID为字符串类型
                        success_list.append(f"问题: {question}，ID: {str(result_id)}\n")
                    else:
                        fail_list.append(f"问题: {question} 添加失败\n")
                # 组织反馈消息
                reply_msgs = [generate_reply_message(self.message_id)]
                if success_list:
                    reply_msgs.append(generate_text_message("批量添加成功：\n"))
                    for s in success_list:
                        reply_msgs.append(generate_text_message(s))
                if fail_list:
                    reply_msgs.append(generate_text_message("以下内容添加失败：\n"))
                    for f in fail_list:
                        reply_msgs.append(generate_text_message(f))
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    reply_msgs,
                    note="del_msg_20",
                )
            else:
                # 单条添加
                # 去除命令前缀
                content = self.raw_message.replace(ADD_QA, "", 1).strip()
                parts = content.split(" ", 1)
                if len(parts) != 2:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"格式错误，应为：{ADD_QA} 问题 答案",
                            ),
                        ],
                        note="del_msg_20",
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
                                f"问题或答案不能为空，应为：{ADD_QA} 问题 答案",
                            ),
                        ],
                        note="del_msg_20",
                    )
                    return
                result_id = matcher.add_qa_pair(question, answer)
                if result_id is not None:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message("添加成功\n"),
                            generate_text_message(f"问题: {question}\n"),
                            generate_text_message(f"答案: {answer}\n"),
                            generate_text_message(f"问答对ID: {str(result_id)}"),
                        ],
                        note="del_msg_20",
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message("添加失败"),
                        ],
                        note="del_msg_20",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理添加问答对命令失败: {e}")

    async def handle_delete_qa(self):
        """
        处理删除问答对命令，支持批量删除。
        格式：删除命令 id1 id2 ...，空格分隔多个ID
        """
        try:
            if not is_group_admin(self.role) and not is_system_owner(self.user_id):
                return

            # 去除命令前缀
            content = self.raw_message.replace(DELETE_QA, "", 1).strip()
            if not content:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            "请提供要删除的问答对ID（可空格分隔多个ID）"
                        ),
                    ],
                    note="del_msg_20",
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
                            "请提供要删除的问答对ID（可空格分隔多个ID）"
                        ),
                    ],
                    note="del_msg_20",
                )
                return

            matcher = AdvancedQAMatcher(self.group_id)
            success_ids = []
            fail_ids = []
            for id_str in id_strs:
                try:
                    qa_id = int(id_str)
                    result = matcher.delete_qa_pair(qa_id)
                    if result:
                        success_ids.append(str(qa_id))
                    else:
                        fail_ids.append(str(qa_id))
                except Exception:
                    fail_ids.append(str(id_str))

            msg_list = [generate_reply_message(self.message_id)]
            if success_ids:
                msg_list.append(
                    generate_text_message(f"删除成功的ID: {' '.join(success_ids)}")
                )
            if fail_ids:
                msg_list.append(
                    generate_text_message(f"删除失败的ID: {' '.join(fail_ids)}")
                )
            if not success_ids and not fail_ids:
                msg_list.append(generate_text_message("未能识别要删除的问答对ID"))

            await send_group_msg(
                self.websocket,
                self.group_id,
                msg_list,
                note="del_msg_20",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理删除问答对命令失败: {e}")

    async def handle_match_qa(self):
        """
        处理匹配问答对命令。

        根据收到的消息内容，在问答库中查找最相似的问题，并返回对应的答案及相似度。
        """
        try:
            matcher = AdvancedQAMatcher(self.group_id)
            matcher.build_index()
            orig_question, answer, score, qa_id = matcher.find_best_match(
                self.raw_message
            )
            if orig_question and answer:
                await send_group_msg_with_cq(
                    self.websocket,
                    self.group_id,
                    f"[CQ:reply,id={self.message_id}]"
                    "你可能想问\n"
                    f"问题: {orig_question}\n"
                    f"回复: {answer}\n"
                    f"相似度: {score:.2f} ，ID: {qa_id}",
                )
                return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理匹配问答对命令失败: {e}")

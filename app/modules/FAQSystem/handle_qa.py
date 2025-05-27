import os
import logger
from . import MODULE_NAME, ADD_FAQ, DELETE_FAQ
from core.auth import is_group_admin, is_system_owner
from .handle_match_qa import AdvancedFAQMatcher
from api.message import send_group_msg, send_group_msg_with_cq
from api.generate import generate_reply_message, generate_text_message
import re
import json


RKEY_DIR = os.path.join("data", "nc_get_rkey.json")


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
            if self.raw_message.startswith(ADD_FAQ):
                await self.handle_add_qa()
                return
            # 如果消息是删除问答对命令，则调用删除问答对函数
            if self.raw_message.startswith(DELETE_FAQ):
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
        matcher = None
        try:
            if not is_group_admin(self.role) and not is_system_owner(self.user_id):
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
            logger.error(f"[{MODULE_NAME}]处理添加问答对命令失败: {e}")
        finally:
            if matcher is not None:
                pass  # 已不需要关闭db，由上下文管理器自动处理

    async def handle_delete_qa(self):
        """
        处理删除问答对命令，支持批量删除。
        格式：删除命令 id1 id2 ...，空格分隔多个ID
        """
        try:
            if not is_group_admin(self.role) and not is_system_owner(self.user_id):
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

    async def handle_match_qa(self):
        """
        处理匹配问答对命令。

        根据收到的消息内容，在问答库中查找最相似的问题，并返回对应的答案及相似度。
        """
        try:
            matcher = AdvancedFAQMatcher(self.group_id)
            matcher.build_index()
            orig_question, answer, score, qa_id = matcher.find_best_match(
                self.raw_message
            )

            # 如果答案中有图片（包含rkey），则替换为本地缓存的rkey
            # 示例图片格式：
            # [CQ:image,file=92C3698A5D8CEB42EDE70B316514F211.jpg,sub_type=0,url=https://multimedia.nt.qq.com.cn/download?appid=1407&amp;fileid=xxx&amp;rkey=xxx,file_size=45934]
            if answer is not None:

                def replace_rkey(match):
                    cq_img = match.group(0)
                    # 查找rkey参数
                    rkey_pattern = r"rkey=([^,^\]]+)"
                    rkey_search = re.search(rkey_pattern, cq_img)
                    if rkey_search:
                        # 读取本地rkey
                        try:
                            with open(RKEY_DIR, "r", encoding="utf-8") as f:
                                rkey_json = json.load(f)
                            new_rkey = rkey_json.get("rkey")
                            if new_rkey:
                                # 替换rkey参数
                                new_cq_img = re.sub(
                                    rkey_pattern, f"rkey={new_rkey}", cq_img
                                )
                                return new_cq_img
                        except Exception as e:
                            logger.error(f"[{MODULE_NAME}]本地rkey替换失败: {e}")
                    return cq_img  # 未找到rkey或替换失败则返回原内容

                answer = re.sub(r"\[CQ:image,[^\]]+\]", replace_rkey, answer)

            if orig_question and answer:
                msg = (
                    f"[CQ:reply,id={self.message_id}]"
                    "🌟 你可能想问：\n"
                    "━━━━━━━━━━━━━━\n"
                    f"❓ 问题：{orig_question}\n"
                    "━━━━━━━━━━━━━━\n"
                    f"💡 回复：\n{answer}\n"
                    "━━━━━━━━━━━━━━\n"
                    f"🔎 相似度：{score:.2f}   🆔 ID：{qa_id}\n"
                    "⏳ 本消息将在30秒后撤回，请及时保存"
                )
                await send_group_msg_with_cq(
                    self.websocket,
                    self.group_id,
                    msg,
                    note="del_msg=30",
                )
                return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理匹配问答对命令失败: {e}")

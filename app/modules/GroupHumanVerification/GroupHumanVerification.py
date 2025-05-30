import logger
from . import MODULE_NAME, MAX_WARNINGS
from api.message import send_private_msg, send_group_msg
from api.generate import generate_text_message, generate_at_message
from .data_manager import DataManager
from api.group import set_group_kick, set_group_ban
import asyncio


class GroupHumanVerificationHandler:
    def __init__(self, websocket, user_id, raw_message):
        self.websocket = websocket
        self.user_id = user_id
        self.raw_message = raw_message

    async def handle_verification_code(self):
        """
        收到用户消息时，遍历所有待验证记录，判断是否有待验证，且内容为数字且等于验证码即为答对，否则答错。
        答对：解除禁言、群内和私聊通知、标记为已验证。
        答错：扣减机会，机会用完踢人，否则提醒。输入不是数字也算答错。
        """
        try:
            user_input = self.raw_message.strip()
            with DataManager() as dm:
                # 查找该用户所有待验证记录
                user_records = dm.get_user_records(self.user_id)

            if not user_records:
                # 没有待验证记录，忽略
                return

            matched = False
            for rec in user_records:
                group_id = rec[1]
                unique_id = rec[3]
                attempts = rec[6]
                # 只允许数字验证码
                if user_input.isdigit() and user_input == unique_id:
                    # 答对，解除禁言
                    with DataManager() as dm:
                        dm.update_verify_status(self.user_id, group_id, "已验证")
                    # 解除禁言（duration=0）
                    await set_group_ban(self.websocket, group_id, self.user_id, 0)
                    # 群内通知
                    await send_group_msg(
                        self.websocket,
                        group_id,
                        [
                            generate_at_message(self.user_id),
                            generate_text_message(
                                f"({self.user_id})恭喜你通过卷卷的验证，你可以正常发言了！🎉"
                            ),
                        ],
                        note="del_msg=10",
                    )
                    # 私聊通知
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [
                            generate_text_message(
                                f"群{group_id}验证码验证成功，恭喜你通过卷卷的验证，你可以返回群聊正常发言了！🎉"
                            )
                        ],
                        note="del_msg=10",
                    )
                    matched = True
                    break
            if not matched:
                # 答错，扣减机会
                for rec in user_records:
                    group_id = rec[1]
                    unique_id = rec[3]
                    attempts = rec[6]
                    if attempts > 1:
                        with DataManager() as dm:
                            dm.update_attempt_count(unique_id, attempts - 1)
                        await send_private_msg(
                            self.websocket,
                            self.user_id,
                            [
                                generate_text_message(
                                    f"验证码错误，你还有{attempts - 1}次机会 ⚠️"
                                )
                            ],
                            note="del_msg=10",
                        )
                    else:
                        with DataManager() as dm:
                            dm.update_attempt_count(unique_id, 0)
                            dm.update_verify_status(
                                self.user_id, group_id, "验证超时")
                        # 私聊通知
                        await send_private_msg(
                            self.websocket,
                            self.user_id,
                            [
                                generate_text_message(
                                    "验证码错误次数超过上限，你将在30秒后被移出群聊 ❌"
                                )
                            ],
                            note="del_msg=10",
                        )
                        # 群内通知
                        await send_group_msg(
                            self.websocket,
                            group_id,
                            [
                                generate_at_message(self.user_id),
                                generate_text_message(
                                    "验证码错误次数超过上限，你将在30秒后被移出群聊 ❌"
                                ),
                            ],
                            note="del_msg=10",
                        )
                        # 暂停30秒
                        await asyncio.sleep(30)
                        # 踢出群聊
                        await set_group_kick(self.websocket, group_id, self.user_id)
                return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理验证码失败: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [generate_text_message(f"处理失败: {e} ❌")],
            )

    async def handle_approve_request(self):
        """
        处理批准入群验证请求，命令格式：同意入群验证 <群号> <QQ号>
        """
        try:
            parts = self.raw_message.strip().split()
            if len(parts) < 3:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_text_message(
                            "格式错误，应为：同意入群验证 <群号> <QQ号> ⚠️"
                        )
                    ],
                    note="del_msg=10",
                )
                return
            group_id = parts[1]
            user_id = parts[2]
            with DataManager() as dm:
                # 查找该群该用户的待验证记录
                records = dm.get_user_records_by_group_id_and_user_id(
                    group_id, user_id)
            if not records:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_text_message(
                            f"未找到群{group_id}、QQ号{user_id}的待验证记录 ❌"
                        )
                    ],
                )
                return
            with DataManager() as dm:
                dm.update_verify_status(user_id, group_id, "管理员已批准")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [
                    generate_text_message(
                        f"已批准群{group_id}、QQ号{user_id}的入群验证请求 ✅"
                    )
                ],
                note="del_msg=10",
            )
            # 群内同步通知
            await send_group_msg(
                self.websocket,
                group_id,
                [
                    generate_at_message(user_id),
                    generate_text_message(
                        f"({self.user_id})你的入群验证已被管理员手动通过，可以正常发言了！🎉"
                    ),
                ],
                note="del_msg=120",
            )
            # 解除禁言（duration=0）
            await set_group_ban(self.websocket, group_id, user_id, 0)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理批准入群验证请求失败: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [generate_text_message(f"处理失败: {e} ❌")],
            )

    async def handle_reject_request(self):
        """
        处理拒绝入群验证请求，命令格式：拒绝入群验证 <群号> <QQ号>
        """
        try:
            parts = self.raw_message.strip().split()
            if len(parts) < 3:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_text_message(
                            "格式错误，应为：拒绝入群验证 <群号> <QQ号> ⚠️"
                        )
                    ],
                    note="del_msg=10",
                )
                return
            group_id = parts[1]
            user_id = parts[2]
            with DataManager() as dm:
                # 查找该群该用户的待验证记录
                records = dm.get_user_records_by_group_id_and_user_id(
                    group_id, user_id)
            if not records:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_text_message(
                            f"未找到群{group_id}、QQ号{user_id}的待验证记录 ❌"
                        )
                    ],
                    note="del_msg=10",
                )
                return
            with DataManager() as dm:
                dm.update_verify_status(user_id, group_id, "管理员已拒绝")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [
                    generate_text_message(
                        f"已拒绝群{group_id}、QQ号{user_id}的入群验证请求 ❌"
                    )
                ],
                note="del_msg=10",
            )
            # 群内同步通知
            await send_group_msg(
                self.websocket,
                group_id,
                [
                    generate_at_message(user_id),
                    generate_text_message(
                        f"({self.user_id})你的入群验证已被管理员拒绝，1分钟后将自动被踢出，如有疑问请联系管理员。❌"
                    ),
                ],
                note="del_msg=60",
            )
            # 暂停1分钟
            await asyncio.sleep(60)
            # 踢出群聊
            await set_group_kick(self.websocket, group_id, user_id)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理拒绝入群验证请求失败: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [generate_text_message(f"处理失败: {e} ❌")],
            )
            # 生成处理结果报告
            report_parts = []

            for group_id, users in group_map.items():
                # 该群的踢出用户
                kicked_users = []
                # 该群的警告用户
                warned_users = []
                # 该群的最后一次警告用户
                last_warn_users = []

                for record in users:
                    unique_id = record[3]
                    user_id = record[2]
                    remaining_warnings = record[7]

                    if remaining_warnings > 1:
                        new_count = remaining_warnings - 1
                        warned_count = MAX_WARNINGS - new_count
                        with DataManager() as dm:
                            dm.update_warning_count(unique_id, new_count)
                        warned_users.append(user_id)
                    elif remaining_warnings == 1:
                        warned_count = MAX_WARNINGS
                        # 最后一次警告
                        with DataManager() as dm:
                            dm.update_warning_count(unique_id, 0)
                            dm.update_verify_status(user_id, group_id, "验证超时")
                        kicked_users.append(user_id)
                        last_warn_users.append(user_id)

                # 发送合并的警告消息
                if warned_users or kicked_users or last_warn_users:
                    report_parts.append(
                        generate_text_message(
                            f"群 {group_id} 的处理结果："
                        )
                    )
                    if kicked_users:
                        report_parts.append(
                            generate_text_message(
                                f"踢出用户：{', '.join([str(u) for u in kicked_users])}"
                            )
                        )
                    if warned_users:
                        report_parts.append(
                            generate_text_message(
                                f"警告用户：{', '.join([str(u) for u in warned_users])}"
                            )
                        )
                    if last_warn_users:
                        report_parts.append(
                            generate_text_message(
                                f"最后一次警告用户：{', '.join([str(u) for u in last_warn_users])}"
                            )
                        )
                    report_parts.append(
                        generate_text_message(" ")
                    )
            if report_parts:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    report_parts,
                )

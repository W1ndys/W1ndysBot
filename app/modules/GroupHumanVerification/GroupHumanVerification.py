import logger
from . import MODULE_NAME
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
                                f"({self.user_id})恭喜你通过卷卷的验证，你可以正常发言了！"
                            ),
                        ],
                        note="del_msg=30",
                    )
                    # 私聊通知
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [
                            generate_text_message(
                                f"群{group_id}验证码验证成功，恭喜你通过卷卷的验证，你可以返回群聊正常发言了！"
                            )
                        ],
                        note="del_msg=30",
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
                                    f"验证码错误，你还有{attempts - 1}次机会"
                                )
                            ],
                            note="del_msg=30",
                        )
                    else:
                        with DataManager() as dm:
                            dm.update_attempt_count(unique_id, 0)
                            dm.update_verify_status(self.user_id, group_id, "验证超时")
                        # 私聊通知
                        await send_private_msg(
                            self.websocket,
                            self.user_id,
                            [
                                generate_text_message(
                                    "验证码错误次数超过上限，你将在30秒后被移出群聊"
                                )
                            ],
                            note="del_msg=30",
                        )
                        # 群内通知
                        await send_group_msg(
                            self.websocket,
                            group_id,
                            [
                                generate_at_message(self.user_id),
                                generate_text_message(
                                    "验证码错误次数超过上限，你将在30秒后被移出群聊"
                                ),
                            ],
                            note="del_msg=30",
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
                [generate_text_message(f"处理失败: {e}")],
            )

    async def handle_approve_request(self):
        """
        处理批准入群验证请求
        """
        try:
            parts = self.raw_message.strip().split()
            if len(parts) < 2:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [generate_text_message("格式错误，应为：同意入群验证 <唯一ID>")],
                )
                return
            unique_id = parts[1]
            with DataManager() as dm:
                record = dm.get_record_by_unique_id(unique_id)
            if not record:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [generate_text_message(f"未找到唯一ID为{unique_id}的验证记录")],
                )
                return
            group_id = record[0]  # group_id
            user_id = record[1]  # user_id
            with DataManager() as dm:
                dm.update_verify_status(self.user_id, group_id, "已验证")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [generate_text_message(f"已批准唯一ID为{unique_id}的入群验证请求")],
            )
            # 群内同步通知
            await send_group_msg(
                self.websocket,
                group_id,
                [
                    generate_at_message(user_id),
                    generate_text_message(
                        f"({self.user_id})你的入群验证已被管理员手动通过，欢迎加入群聊！"
                    ),
                ],
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理批准入群验证请求失败: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [generate_text_message(f"处理失败: {e}")],
            )

    async def handle_reject_request(self):
        """
        处理拒绝入群验证请求
        """
        try:
            parts = self.raw_message.strip().split()
            if len(parts) < 2:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [generate_text_message("格式错误，应为：拒绝入群验证 <唯一ID>")],
                )
                return
            unique_id = parts[1]
            with DataManager() as dm:
                record = dm.get_record_by_unique_id(unique_id)
            if not record:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [generate_text_message(f"未找到唯一ID为{unique_id}的验证记录")],
                )
                return
            group_id = record[0]  # group_id
            user_id = record[1]  # user_id
            with DataManager() as dm:
                dm.update_verify_status(self.user_id, group_id, "验证超时")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [generate_text_message(f"已拒绝唯一ID为{unique_id}的入群验证请求")],
            )
            # 群内同步通知
            await send_group_msg(
                self.websocket,
                group_id,
                [
                    generate_at_message(user_id),
                    generate_text_message(
                        f"({self.user_id})你的入群验证已被管理员拒绝，1分钟后将自动被踢出，如有疑问请联系管理员。"
                    ),
                ],
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
                [generate_text_message(f"处理失败: {e}")],
            )

    async def handle_scan_request(self):
        """
        管理员扫描未验证用户，群内警告，超限则踢出并标记为验证超时
        按照数据库建表顺序严格取字段
        """
        try:
            parts = self.raw_message.strip().split()
            group_id = parts[1] if len(parts) > 1 else None
            with DataManager() as dm:
                unverified_users = dm.get_unverified_users(group_id)
            if not unverified_users:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [generate_text_message("未找到未验证用户")],
                )
                return
            # 按群分组
            group_map = {}
            for record in unverified_users:
                gid = record[0]  # group_id
                group_map.setdefault(gid, []).append(record)

            for gid, users in group_map.items():
                # 构建合并消息
                message_parts = []
                users_to_kick = []

                for record in users:
                    unique_id = record[3]
                    user_id = record[1]
                    remaining_warnings = record[6]

                    if remaining_warnings > 1:
                        new_count = remaining_warnings - 1
                        with DataManager() as dm:
                            dm.update_warning_count(unique_id, new_count)
                        message_parts.append(generate_at_message(user_id))
                        message_parts.append(
                            generate_text_message(
                                f"({user_id})请及时加我为好友私聊验证码【{unique_id}】进行验证（警告{new_count}/3）"
                            )
                        )
                    elif remaining_warnings == 1:
                        # 最后一次警告
                        with DataManager() as dm:
                            dm.update_warning_count(unique_id, 0)
                            dm.update_verify_status(user_id, gid, "验证超时")
                        users_to_kick.append((user_id, unique_id))

                # 发送合并的警告消息
                if message_parts:
                    warning_message = (
                        "\n".join(message_parts) + "\n超过3次将会被踢出群聊"
                    )
                    await send_group_msg(
                        self.websocket,
                        gid,
                        [generate_text_message(warning_message)],
                    )

                # 处理需要踢出的用户
                for user_id, unique_id in users_to_kick:
                    await send_group_msg(
                        self.websocket,
                        gid,
                        [
                            generate_at_message(user_id),
                            generate_text_message(
                                "你未完成入群验证，已达到最后一次警告，马上将被移出群聊！"
                            ),
                        ],
                    )
                    await asyncio.sleep(2)  # 稍作延迟
                    await set_group_kick(self.websocket, gid, user_id)

            await send_private_msg(
                self.websocket,
                self.user_id,
                [generate_text_message("扫描并处理完毕")],
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]扫描验证失败: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [generate_text_message(f"扫描失败: {e}")],
            )

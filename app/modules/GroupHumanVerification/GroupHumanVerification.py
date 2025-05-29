import logger
from . import MODULE_NAME
from api.message import send_private_msg, send_group_msg
from api.generate import generate_text_message, generate_at_message
from .data_manager import DataManager
from api.group import set_group_kick
import asyncio


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
        with DataManager(None) as dm:
            record = dm.get_record_by_unique_id(unique_id)
        if not record:
            await send_private_msg(
                self.websocket,
                self.user_id,
                [generate_text_message(f"未找到唯一ID为{unique_id}的验证记录")],
            )
            return
        group_id = record[1]  # group_id
        qq_id = record[2]  # qq_id
        with DataManager(None) as dm:
            dm.update_verify_status(unique_id, "管理员通过")
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
                generate_at_message(qq_id),
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
        with DataManager(None) as dm:
            record = dm.get_record_by_unique_id(unique_id)
        if not record:
            await send_private_msg(
                self.websocket,
                self.user_id,
                [generate_text_message(f"未找到唯一ID为{unique_id}的验证记录")],
            )
            return
        group_id = record[1]  # group_id
        qq_id = record[2]  # qq_id
        with DataManager(None) as dm:
            dm.update_verify_status(unique_id, "管理员拒绝")
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
                generate_at_message(qq_id),
                generate_text_message(
                    f"({self.user_id})你的入群验证已被管理员拒绝，1分钟后将自动被踢出，如有疑问请联系管理员。"
                ),
            ],
        )
        # 暂停1分钟
        await asyncio.sleep(60)
        # 踢出群聊
        await set_group_kick(self.websocket, group_id, qq_id)

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
        # 解析群号参数
        group_id = parts[1] if len(parts) > 1 else None
        with DataManager(group_id) as dm:
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
            gid = record[1]  # group_id
            group_map.setdefault(gid, []).append(record)

        for gid, users in group_map.items():
            # 构建合并消息
            message_parts = []
            users_to_kick = []

            for record in users:
                # 按照建表顺序
                # 0: id
                # 1: group_id
                # 2: qq_id
                # 3: unique_id
                # 4: verify_status
                # 5: join_time
                # 6: remaining_attempts
                # 7: remaining_warnings
                # 8: created_at
                unique_id = record[3]
                qq_id = record[2]
                remaining_warnings = record[7]

                if remaining_warnings > 1:
                    new_count = remaining_warnings - 1
                    with DataManager(None) as dm:
                        dm.update_warning_count(unique_id, new_count)
                    message_parts.append(generate_at_message(qq_id))
                    message_parts.append(
                        generate_text_message(
                            f"({qq_id})请及时加我为好友私聊验证码【{unique_id}】进行验证（警告{new_count}/3）"
                        )
                    )
                elif remaining_warnings == 1:
                    # 最后一次警告
                    with DataManager(None) as dm:
                        dm.update_warning_count(unique_id, 0)
                        dm.update_verify_status(unique_id, "验证超时")
                    users_to_kick.append((qq_id, unique_id))

            # 发送合并的警告消息
            if message_parts:
                warning_message = "\n".join(message_parts) + "\n超过3次将会被踢出群聊"
                await send_group_msg(
                    self.websocket,
                    gid,
                    [generate_text_message(warning_message)],
                )

            # 处理需要踢出的用户
            for qq_id, unique_id in users_to_kick:
                await send_group_msg(
                    self.websocket,
                    gid,
                    [
                        generate_at_message(qq_id),
                        generate_text_message(
                            "你未完成入群验证，已达到最后一次警告，马上将被移出群聊！"
                        ),
                    ],
                )
                await asyncio.sleep(2)  # 稍作延迟
                await set_group_kick(self.websocket, gid, qq_id)

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

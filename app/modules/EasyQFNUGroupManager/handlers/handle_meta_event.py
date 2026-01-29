from .. import (
    MODULE_NAME,
    TIMEOUT_HOURS,
    REMIND_START_HOURS,
    KICK_NOTICE_MESSAGE,
    REMIND_MESSAGE_TEMPLATE,
)
from logger import logger
from datetime import datetime
from core.switchs import get_all_enabled_groups
from api.message import send_group_msg
from api.group import set_group_kick
from utils.generate import generate_at_message, generate_text_message
from .data_manager import DataManager
import asyncio


class MetaEventHandler:
    """
    元事件处理器/定时任务处理器
    元事件可利用心跳来实现定时任务
    """

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.post_type = msg.get("post_type", "")
        self.meta_event_type = msg.get("meta_event_type", "")

    async def handle(self):
        try:
            # 必要时可以这里可以引入群聊开关和私聊开关检测

            if self.post_type == "meta_event":
                if self.meta_event_type == "lifecycle":
                    await self.handle_lifecycle()
                elif self.meta_event_type == "heartbeat":
                    await self.handle_heartbeat()
                else:
                    logger.error(
                        f"[{MODULE_NAME}]收到未知元事件类型: {self.meta_event_type}"
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理元事件失败: {e}")

    async def handle_lifecycle(self):
        """
        处理生命周期
        """
        try:
            if self.meta_event_type == "connect":
                pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理生命周期失败: {e}")

    async def handle_heartbeat(self):
        """
        处理心跳
        每次心跳检测未验证用户：
        1. 入群超过REMIND_HOURS小时的用户发送提醒
        2. 入群超过TIMEOUT_HOURS小时的用户通告并踢出
        """
        try:
            # 先检查并提醒即将超时的用户
            await self._check_and_remind_unverified_users()
            # 再检查并踢出已超时的用户
            await self._check_and_kick_unverified_users()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理心跳失败: {e}")

    async def _check_and_remind_unverified_users(self):
        """
        检测并提醒入群超过整点小时数但仍未验证的用户
        每满一个整点小时都会提醒一次，直到被踢出
        所有待提醒用户按群分组，同一小时数的用户合并到同一条消息内艾特统一提醒
        """
        try:
            # 获取所有开启了本模块的群
            enabled_groups = get_all_enabled_groups(MODULE_NAME)
            if not enabled_groups:
                return

            with DataManager() as dm:
                # 获取所有待提醒的用户
                users_to_remind = dm.get_users_to_remind(
                    start_hour=REMIND_START_HOURS,
                    timeout_hours=TIMEOUT_HOURS
                )
                if not users_to_remind:
                    return

                # 按群和小时数分组 {group_id: {hour: [user_info, ...]}}
                groups_hours_users = {}
                for user in users_to_remind:
                    group_id = user["group_id"]
                    # 只处理开启了模块的群
                    if group_id not in enabled_groups:
                        continue

                    current_hour = user["current_hour"]
                    if group_id not in groups_hours_users:
                        groups_hours_users[group_id] = {}
                    if current_hour not in groups_hours_users[group_id]:
                        groups_hours_users[group_id][current_hour] = []
                    groups_hours_users[group_id][current_hour].append(user)

                # 对每个群的每个小时数进行提醒
                for group_id, hours_users in groups_hours_users.items():
                    for hour, users in hours_users.items():
                        await self._remind_users(dm, group_id, users, hour)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]检测待提醒用户失败: {e}")

    async def _remind_users(self, dm, group_id: str, users: list, hour: int):
        """
        提醒一个群内同一入群小时数的所有待验证用户
        合并到一条消息内艾特所有用户

        Args:
            dm: DataManager实例
            group_id: 群号
            users: 要提醒的用户信息列表 [{user_id, current_hour, ...}, ...]
            hour: 当前入群的整点小时数
        """
        try:
            if not users:
                return

            # 构建消息：艾特所有用户 + 提醒文本
            message_segments = []
            for user in users:
                message_segments.append(generate_at_message(user["user_id"]))
                message_segments.append(generate_text_message(" "))

            # 使用模板生成提醒消息
            remind_message = REMIND_MESSAGE_TEMPLATE.format(
                hours=hour,
                timeout=TIMEOUT_HOURS
            )
            message_segments.append(generate_text_message(f"\n{remind_message}"))

            # 发送提醒消息
            await send_group_msg(
                self.websocket,
                group_id,
                message_segments,
            )

            logger.info(
                f"[{MODULE_NAME}]群 {group_id} 提醒 {len(users)} 名入群满 {hour} 小时未验证用户"
            )

            # 更新每个用户的上次提醒小时数
            for user in users:
                dm.update_last_remind_hour(user["user_id"], group_id, hour)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]提醒用户失败: {e}")

    async def _check_and_kick_unverified_users(self):
        """
        检测并踢出超时未验证的用户
        所有未验证用户按群分组，合并到同一条消息内艾特，避免大量消息导致风控
        """
        try:
            # 获取所有开启了本模块的群
            enabled_groups = get_all_enabled_groups(MODULE_NAME)
            if not enabled_groups:
                return

            with DataManager() as dm:
                # 获取所有超时未验证的用户
                unverified_users = dm.get_unverified_users(timeout_hours=TIMEOUT_HOURS)
                if not unverified_users:
                    return

                # 按群分组
                groups_users = {}
                for user in unverified_users:
                    group_id = user["group_id"]
                    # 只处理开启了模块的群
                    if group_id not in enabled_groups:
                        continue

                    if group_id not in groups_users:
                        groups_users[group_id] = []
                    groups_users[group_id].append(user["user_id"])

                # 对每个群进行处理
                for group_id, user_ids in groups_users.items():
                    await self._notify_and_kick_users(dm, group_id, user_ids)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]检测未验证用户失败: {e}")

    async def _notify_and_kick_users(self, dm, group_id: str, user_ids: list):
        """
        通告并踢出一个群内的所有超时未验证用户
        合并到一条消息内艾特所有用户

        Args:
            dm: DataManager实例
            group_id: 群号
            user_ids: 要踢出的用户ID列表
        """
        try:
            if not user_ids:
                return

            # 构建消息：艾特所有用户 + 通告文本
            message_segments = []
            for user_id in user_ids:
                message_segments.append(generate_at_message(user_id))
                message_segments.append(generate_text_message(" "))

            message_segments.append(generate_text_message(f"\n{KICK_NOTICE_MESSAGE}"))

            # 发送通告消息
            await send_group_msg(
                self.websocket,
                group_id,
                message_segments,
            )

            logger.info(
                f"[{MODULE_NAME}]群 {group_id} 通告踢出 {len(user_ids)} 名未验证用户"
            )

            # 标记用户已通知
            dm.mark_users_notified(user_ids, group_id)

            # 等待一小段时间，让消息先发出
            await asyncio.sleep(2)

            # 逐个踢出用户
            for user_id in user_ids:
                try:
                    await set_group_kick(
                        self.websocket,
                        group_id,
                        user_id,
                        reject_add_request=False,  # 不拉黑，允许重新加群
                    )
                    # 踢出后删除数据库记录
                    dm.remove_user(user_id, group_id)
                    # 避免频繁操作导致风控
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(
                        f"[{MODULE_NAME}]踢出用户 {user_id} 从群 {group_id} 失败: {e}"
                    )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]通告并踢出用户失败: {e}")

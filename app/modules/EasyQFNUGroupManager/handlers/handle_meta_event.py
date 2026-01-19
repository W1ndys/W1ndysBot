from .. import (
    MODULE_NAME,
    TIMEOUT_HOURS,
    KICK_NOTICE_MESSAGE,
    IMMUNITY_START_HOUR,
    IMMUNITY_END_HOUR,
)
from logger import logger
from datetime import datetime, timedelta
from core.switchs import get_all_enabled_groups
from api.message import send_group_msg
from api.group import set_group_kick
from utils.generate import generate_at_message, generate_text_message
from .data_manager import DataManager
import asyncio


def calculate_effective_hours(join_timestamp: int) -> float:
    """
    计算从入群时间到现在的有效时间（小时），排除每天0-8点的免疫时间段

    Args:
        join_timestamp: 入群时间戳

    Returns:
        float: 有效时间（小时）
    """
    join_time = datetime.fromtimestamp(join_timestamp)
    now = datetime.now()

    if now <= join_time:
        return 0.0

    # 计算总经过的秒数
    total_seconds = (now - join_time).total_seconds()

    # 计算需要排除的免疫时间（秒）
    immunity_seconds = 0

    # 从入群时间开始，逐天检查免疫时间段
    current = join_time
    while current < now:
        # 当天的免疫时间段开始和结束
        day_start = current.replace(hour=0, minute=0, second=0, microsecond=0)
        immunity_start = day_start.replace(hour=IMMUNITY_START_HOUR)
        immunity_end = day_start.replace(hour=IMMUNITY_END_HOUR)

        # 计算与当前时间段的交集
        overlap_start = max(current, immunity_start)
        overlap_end = min(now, immunity_end)

        if overlap_start < overlap_end:
            immunity_seconds += (overlap_end - overlap_start).total_seconds()

        # 移动到下一天
        current = day_start + timedelta(days=1)

    # 有效时间 = 总时间 - 免疫时间
    effective_seconds = max(0, total_seconds - immunity_seconds)
    return effective_seconds / 3600


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
        每次心跳检测未验证用户，超时则通告并踢出
        """
        try:
            await self._check_and_kick_unverified_users()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理心跳失败: {e}")

    async def _check_and_kick_unverified_users(self):
        """
        检测并踢出超时未验证的用户
        所有未验证用户按群分组，合并到同一条消息内艾特，避免大量消息导致风控

        超时计算会排除每天0-8点的免疫时间段（管理员休息时间）
        """
        try:
            # 获取所有开启了本模块的群
            enabled_groups = get_all_enabled_groups(MODULE_NAME)
            if not enabled_groups:
                return

            with DataManager() as dm:
                # 获取所有未验证的用户（使用较长的时间确保获取到足够的候选用户）
                # 这里使用24小时是为了获取候选列表，实际超时判断在下面用有效时间计算
                unverified_users = dm.get_unverified_users(timeout_hours=1)
                if not unverified_users:
                    return

                # 按群分组，同时过滤真正超时的用户（排除0-8点免疫时间）
                groups_users = {}
                for user in unverified_users:
                    group_id = user["group_id"]
                    # 只处理开启了模块的群
                    if group_id not in enabled_groups:
                        continue

                    # 计算有效时间（排除0-8点免疫时间段）
                    effective_hours = calculate_effective_hours(user["join_time"])
                    if effective_hours < TIMEOUT_HOURS:
                        continue  # 有效时间未超时，跳过

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

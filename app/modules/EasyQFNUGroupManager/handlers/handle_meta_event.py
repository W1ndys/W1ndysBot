from .. import MODULE_NAME, TIMEOUT_HOURS, KICK_NOTICE_MESSAGE
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
        
        每天0点到8点为免疫时间段，不进行超时检测
        """
        try:
            # 检查是否在免疫时间段内（0点到8点）
            current_hour = datetime.now().hour
            if 0 <= current_hour < 8:
                return  # 在免疫时间段内，跳过检测
            
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

from .. import MODULE_NAME, FORWARD_GROUP_ID
import logger
from datetime import datetime
from core.switchs import is_group_switch_on
from core.get_group_list import get_group_member_info_by_id
from core.get_group_member_list import get_user_role_in_group
from ..utils.data_manager import DataManager
from api.message import send_group_msg
from api.group import set_group_kick
from utils.generate import generate_text_message, generate_at_message
import asyncio


class GroupNoticeHandler:
    """
    群组通知处理器
    """

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.notice_type = msg.get("notice_type")
        self.sub_type = msg.get("sub_type")
        self.user_id = str(msg.get("user_id"))
        self.group_id = str(msg.get("group_id"))
        self.operator_id = str(msg.get("operator_id"))

    async def handle_group_notice(self):
        """
        处理群聊通知
        """
        try:
            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 只处理群聊成员增加通知
            if self.notice_type == "group_increase":
                await self.handle_group_increase()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊通知失败: {e}")

    # 群聊成员增加处理

    async def handle_group_increase(self):
        """
        处理群聊成员增加通知
        """
        try:
            if self.group_id == FORWARD_GROUP_ID:
                # 处理Easy-QFNUJW模块进入中转群的事件
                await self.handle_group_increase_forward_group()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员增加通知失败: {e}")
            raise  # 增加错误抛出

    async def handle_group_increase_forward_group(self):
        """
        处理群聊成员增加 - 中转群通知
        """
        try:
            # 定义需要忽略的群号列表（字符串类型）
            IGNORE_GROUP_IDS = ["118976506"]

            enable_groups_list = self._get_enable_groups_list()
            if not enable_groups_list:
                logger.error(f"[{MODULE_NAME}]未获取到启用的教务群列表")
                raise ValueError("未获取到启用的教务群列表")
            # 过滤掉需要忽略的群
            filtered_enable_groups_list = [
                group_id
                for group_id in enable_groups_list
                if str(group_id) not in IGNORE_GROUP_IDS
            ]
            if not filtered_enable_groups_list:
                logger.error(f"[{MODULE_NAME}]启用的教务群列表全部被忽略或为空")
                raise ValueError("启用的教务群列表全部被忽略或为空")
            enable_groups_info_list = self._get_enable_groups_info_list(
                filtered_enable_groups_list
            )
            if not enable_groups_info_list:
                logger.error(f"[{MODULE_NAME}]未获取到启用群的详细信息")
                raise ValueError("未获取到启用群的详细信息")
            (
                welcoms_message,
                kick_delay,
            ) = self._build_welcome_message(enable_groups_info_list, self.user_id)
            await self._send_welcome_message(welcoms_message)

            if kick_delay > 0:
                # 暂停时间
                await asyncio.sleep(kick_delay)
                # 踢出中转群
                await set_group_kick(self.websocket, self.group_id, self.user_id)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员增加 - 中转群通知失败: {e}")
            raise  # 增加错误抛出

    def _get_enable_groups_list(self):
        """
        获取教务启用群列表
        """
        try:
            with DataManager() as data_manager:
                group_list = (
                    data_manager.get_enable_group_list()
                    .get("data", {})
                    .get("group_list", [])
                )
                if not isinstance(group_list, list):
                    logger.error(f"[{MODULE_NAME}]获取到的群列表不是列表类型")
                    raise TypeError("获取到的群列表不是列表类型")
                return group_list
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取教务启用群列表失败: {e}")
            raise

    def _get_enable_groups_info_list(self, enable_groups_list):
        """
        获取每个群的群名、当前人数和最大人数
        """
        enable_groups_info_list = []
        for group_id in enable_groups_list:
            try:
                group_member_info = get_group_member_info_by_id(group_id)
                if not group_member_info:
                    logger.error(f"[{MODULE_NAME}]未获取到群{group_id}的信息")
                    continue
                enable_groups_info_list.append(
                    {
                        "group_id": group_id,
                        "group_name": group_member_info.get("group_name"),
                        "member_count": group_member_info.get("member_count"),
                        "max_member_count": group_member_info.get("max_member_count"),
                    }
                )
            except Exception as e:
                logger.error(f"[{MODULE_NAME}]获取群{group_id}信息失败: {e}")
        return enable_groups_info_list

    def _build_welcome_message(self, enable_groups_info_list, user_id):
        """
        构建欢迎通知消息（不显示群名，人满的群不显示，仅显示优先最大人数多、其次剩余名额多的群）
        新增：可手动指定需要忽略的群号列表
        新增：检测用户是否已在任意一个启用群里
        """
        # 检查用户是否已在任意一个启用群里
        for group_info in enable_groups_info_list:
            group_id = group_info.get("group_id")
            role = get_user_role_in_group(group_id, user_id)
            if role:
                return (
                    f"你已经加入了群【{group_info.get('group_name')}】({group_id})，无需重复加群，你将在1分钟后被自动踢出。",
                    1 * 60,
                )

        # 手动指定需要忽略的群号列表
        ignore_group_ids = ["1037069786", "716239772"]

        try:
            # 过滤出未满的群，且不在忽略列表中的群
            available_groups = [
                group_info
                for group_info in enable_groups_info_list
                if group_info.get("member_count") < group_info.get("max_member_count")
                and str(group_info.get("group_id")) not in ignore_group_ids
            ]
            # 按照最大人数降序、剩余名额升序排序
            available_groups.sort(
                key=lambda x: (
                    -x.get("max_member_count", 0),  # 最大人数多的排前面
                    (
                        x.get("max_member_count", 0) - x.get("member_count", 0)
                    ),  # 剩余名额少的排前面（接近满员的群优先）
                )
            )

            # 只取排序后第一个群
            top_groups = available_groups[:1]

            if not top_groups:
                return (
                    "🎉欢迎来到Easy-QFNU！\n目前所有正式群都已满员，请等待管理员开新群。",
                    0,
                )

            welcoms_message = (
                "🎉欢迎来到Easy-QFNU！\n"
                "⚠️本群是【中转群】，你将在5分钟后被自动踢出。\n"
                "👉请加入下方任意一个正式群即可使用教务功能：\n\n"
            )
            for group_info in top_groups:
                # 只显示群号和人数，不显示群名
                welcoms_message += f"🔗群号：{group_info.get('group_id')} （{group_info.get('member_count')}/{group_info.get('max_member_count')}）\n\n"
            welcoms_message += (
                "⏳请尽快加入正式群，你将在5分钟后被踢出本群。如果群已满，请重进中转群获取新群\n"
                "✅如果你已经加入过Easy-QFNU的任何一个群，无需重复加群，等待被踢或自行退群即可~\n"
                "📢本群不会发布任何通知和使用说明，请加正式群获取服务。"
            )
            return welcoms_message, 5 * 60
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]构建欢迎通知消息失败: {e}")
            raise

    async def _send_welcome_message(self, welcoms_message):
        """
        发送欢迎通知消息
        """
        try:
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_at_message(self.user_id),
                    generate_text_message(f"({self.user_id})"),
                    generate_text_message(welcoms_message),
                ],
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]发送欢迎通知消息失败: {e}")

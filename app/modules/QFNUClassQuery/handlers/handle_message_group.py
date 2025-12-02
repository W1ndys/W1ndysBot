from .. import (
    MODULE_NAME,
    SWITCH_NAME,
    EMPTY_CLASSROOM_COMMAND,
    CLASS_SCHEDULE_COMMAND,
)
from core.menu_manager import MENU_COMMAND
from logger import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from utils.auth import is_system_admin
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime
from .data_manager import DataManager
from core.menu_manager import MenuManager
from ..core.api_client import QFNUClassApiClient


class GroupMessageHandler:
    """群消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.sub_type = msg.get("sub_type", "")  # 子类型，只有normal
        self.group_id = str(msg.get("group_id", ""))  # 群号
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.message = msg.get("message", {})  # 消息段数组
        self.raw_message = msg.get("raw_message", "")  # 原始消息
        self.sender = msg.get("sender", {})  # 发送者信息
        self.nickname = self.sender.get("nickname", "")  # 昵称
        self.card = self.sender.get("card", "")  # 群名片
        self.role = self.sender.get("role", "")  # 群身份

    async def _handle_switch_command(self):
        """
        处理群聊开关命令
        """
        if self.raw_message.lower() == SWITCH_NAME.lower():
            # 鉴权
            if not is_system_admin(self.user_id):
                logger.error(f"[{MODULE_NAME}]{self.user_id}无权限切换群聊开关")
                return True
            await handle_module_group_switch(
                MODULE_NAME,
                self.websocket,
                self.group_id,
                self.message_id,
            )
            return True
        return False

    async def _handle_menu_command(self):
        """
        处理菜单命令（无视开关状态）
        """
        if self.raw_message.lower() == f"{SWITCH_NAME}{MENU_COMMAND}".lower():
            menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(menu_text),
                ],
                note="del_msg=30",
            )
            return True
        return False

    async def handle(self):
        """
        处理群消息
        """
        try:
            # 处理群聊开关命令
            if await self._handle_switch_command():
                return

            # 处理菜单命令
            if await self._handle_menu_command():
                return

            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 检查是否包含空教室命令
            if EMPTY_CLASSROOM_COMMAND in self.raw_message:
                query_text = self.raw_message.replace(
                    EMPTY_CLASSROOM_COMMAND, ""
                ).strip()
                if not query_text:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                "请提供查询条件，例如：空教室 明天综合楼"
                            ),
                        ],
                    )
                    return

                result = await QFNUClassApiClient.query_free_classroom(query_text)
                if not result:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message("查询失败，请稍后重试"),
                        ],
                    )
                    return

                if result.get("code") == 200:
                    data = result.get("data", {})
                    if data.get("is_relevant"):
                        count = data.get("count", 0)
                        url = data.get("url", "")
                        params = data.get("query_params", {})
                        reply_text = (
                            f"✅ 查询成功\n"
                            f"📅 日期：{params.get('target_date')} ({params.get('weekday_cn')})\n"
                            f"🏫 教学楼：{params.get('building_name')}\n"
                            f"⏰ 节次：{params.get('start_lesson')}-{params.get('end_lesson')}\n"
                            f"📊 空闲教室：{count}间\n"
                            f"🔗 详情链接：{url}"
                        )
                    else:
                        reply_text = (
                            f"❓ 无法解析查询意图：{data.get('original_query')}"
                        )
                else:
                    reply_text = f"❌ 查询出错：{result.get('message')}"

                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(reply_text),
                    ],
                )
                return

            # 检查是否包含教室课表命令
            if CLASS_SCHEDULE_COMMAND in self.raw_message:
                query_text = self.raw_message.replace(
                    CLASS_SCHEDULE_COMMAND, ""
                ).strip()
                if not query_text:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                "请提供查询条件，例如：教室课 明天综合楼101"
                            ),
                        ],
                    )
                    return

                # 这里虽然任务描述只给了空教室的详细返回示例，但API文档提到了教室课表查询API
                # 假设返回结构类似或者直接返回结果，这里先做通用处理，后续根据实际返回调整
                # 根据任务描述 "检测到消息包含空教室命令或教室课命令就调用下面API查询"
                # 且API文档中给出了 /api/classroom-schedule

                result = await QFNUClassApiClient.query_classroom_schedule(query_text)
                if not result:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message("查询失败，请稍后重试"),
                        ],
                    )
                    return

                # 假设教室课表返回结构与空教室类似，或者直接展示message/data
                # 由于没有给出教室课表的具体响应示例，这里做一个通用的结果展示
                if result.get("code") == 200:
                    data = result.get("data", {})
                    # 如果有url则展示url，否则展示message
                    url = data.get("url")
                    if url:
                        reply_text = f"✅ 查询成功，详情请点击链接查看：\n{url}"
                    else:
                        # 尝试从data中获取一些信息，或者直接显示message
                        reply_text = f"✅ 查询结果：{result.get('message', '成功')}"
                        if (
                            isinstance(data, dict)
                            and "is_relevant" in data
                            and not data["is_relevant"]
                        ):
                            reply_text = (
                                f"❓ 无法解析查询意图：{data.get('original_query')}"
                            )
                else:
                    reply_text = f"❌ 查询出错：{result.get('message')}"

                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(reply_text),
                    ],
                )
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

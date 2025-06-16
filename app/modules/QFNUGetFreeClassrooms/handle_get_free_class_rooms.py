import logger
from api.message import send_group_msg
from api.generate import generate_reply_message, generate_text_message
from . import MODULE_NAME, GET_FREE_CLASS_ROOM_COMMAND
from .data_manager import DataManager
from .QFNULogin import LoginHandler
from .QFNUApi import QFNUApiManager


class GetFreeClassRoomsHandler:
    """获取空教室处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.user_id = str(msg.get("user_id"))
        self.group_id = str(msg.get("group_id"))
        self.message_id = msg.get("message_id")

    async def handle(self):
        """
        处理获取空教室请求
        示例命令：查空教室 格物楼B101 1-2 1
        参数说明：
        1. 教室全称：如格物楼B101，必填
        2. 节次范围：如1-2，可选，默认1-14
        3. 向后的天数：如1，可选，默认0
        """
        try:
            # 如果消息只有命令，则发送命令格式说明
            if self.msg == GET_FREE_CLASS_ROOM_COMMAND:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            f"获取空教室命令格式：{GET_FREE_CLASS_ROOM_COMMAND} 教室全称 节次范围 向后的天数\n"
                            f"示例：{GET_FREE_CLASS_ROOM_COMMAND} 格物楼B101 1-2 1\n"
                            "不要使用简称，常见错误：综合教学楼写成综合楼，JA101写成A楼，生物楼写错生科楼等"
                        ),
                    ],
                    note="del_msg=30",
                )
                return

            # 去除消息中的命令
            self.msg = self.msg.replace(GET_FREE_CLASS_ROOM_COMMAND, "").strip()

            # 分离参数，分离后第一个参数为教室全称，第二个参数为节次范围，第三个参数为向后的天数
            params = self.msg.split(" ")
            if len(params) < 1:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            f"获取空教室命令参数不足，请发送“{GET_FREE_CLASS_ROOM_COMMAND}”命令查看命令格式"
                        ),
                    ],
                    note="del_msg=30",
                )
                logger.error(f"[{MODULE_NAME}]获取空教室命令参数不足")
                return

            building_prefix = params[0]  # 教室全称
            week = params[1] if len(params) > 1 else "1-14"  # 节次范围
            days = params[2] if len(params) > 2 else "0"  # 向后的天数

            # 获取cookies
            with DataManager() as dm:
                credential = dm.get_credential()
                if not credential:
                    logger.error(f"[{MODULE_NAME}]未存储凭据，将自动登录")
                    login_handler = LoginHandler(credential[1], credential[2])
                    cookies = await login_handler.login()
                    logger.info(f"[{MODULE_NAME}]登录成功: {cookies}")
                    dm.update_cookies(cookies)
                else:
                    cookies = credential[3]

            # 获取空教室
            api_manager = QFNUApiManager(cookies)
            api_result = await api_manager.get_classroom_schedule(
                xnxqh=credential[0],
                week=int(week.split("-")[0]),
                day=int(days),
                start_period=week.split("-")[0],
                end_period=week.split("-")[1] if "-" in week else week,
                building_name=building_prefix,
            )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理获取空教室请求失败: {e}")

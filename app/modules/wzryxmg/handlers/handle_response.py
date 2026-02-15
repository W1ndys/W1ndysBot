import re
from .. import MODULE_NAME, pending_get_msg
from ..handlers.data_manager import DataManager
from logger import logger
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_reply_message


# 小马糕消息正则（用于解析get_msg返回的内容）
XMG_PATTERN = re.compile(
    r'王者荣耀【(.+?)】我的小马糕今天(\d+)块，复制链接来我的市集出售，马年上分大吉！'
)


class ResponseHandler:
    """响应处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", "")

    async def handle(self):
        """处理响应"""
        try:
            # 检查是否为get_msg响应（删除功能）
            if "wzryxmg_get_" in self.echo:
                await self._handle_get_msg_response()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

    async def _handle_get_msg_response(self):
        """处理get_msg响应，用于删除小马糕记录"""
        # 提取echo_str部分（格式: key=xxx_gid=xxx_uid=xxx_mid=xxx）
        parts = self.echo.split("wzryxmg_get_")
        if len(parts) < 2:
            return

        echo_str = parts[1]

        if echo_str not in pending_get_msg:
            logger.warning(f"[{MODULE_NAME}]未找到pending记录: {echo_str}")
            return

        # 获取原始请求信息
        request_info = pending_get_msg[echo_str]
        group_id = request_info["group_id"]
        user_id = request_info["user_id"]
        delete_msg_id = request_info["delete_msg_id"]

        # 获取消息内容（get_msg返回的数据结构）
        # data 中包含 message 字段（消息段数组）
        message_data = self.data.get("message", [])

        # 提取文本内容（消息段数组中找type=text的）
        raw_message = ""
        if isinstance(message_data, list):
            for segment in message_data:
                if segment.get("type") == "text":
                    raw_message = segment.get("data", {}).get("text", "")
                    break
        elif isinstance(message_data, dict):
            # 有时可能是单个消息段对象
            if message_data.get("type") == "text":
                raw_message = message_data.get("data", {}).get("text", "")

        # 从消息内容中解析小马糕
        xmg_info = self._parse_xmg_message(raw_message)

        if not xmg_info:
            await send_group_msg(
                self.websocket,
                group_id,
                [
                    generate_reply_message(delete_msg_id),
                    generate_text_message("无法识别该消息中的小马糕信息，可能不是小马糕消息"),
                ]
            )
            del pending_get_msg[echo_str]
            return

        # 根据小马糕代码删除记录（全库范围）
        with DataManager() as dm:
            deleted = dm.delete_by_xmg_code(xmg_info["code"])

            if deleted:
                # 删除成功后，查询全库下一个最高价格的小马糕
                next_highest = dm.get_global_highest_price_xmg()

                # 先发送删除成功消息
                await send_group_msg(
                    self.websocket,
                    group_id,
                    [
                        generate_reply_message(delete_msg_id),
                        generate_text_message(f"已删除小马糕【{xmg_info['code']}】（{xmg_info['price']}块）的记录"),
                    ]
                )

                # 如果有下一个最高价格的小马糕，单独发送便于复制
                if next_highest:
                    await send_group_msg(
                        self.websocket,
                        group_id,
                        generate_text_message(next_highest['full_message'])
                    )

                logger.info(f"[{MODULE_NAME}]用户{user_id}删除了小马糕记录，代码：{xmg_info['code']}，价格：{xmg_info['price']}")
            else:
                await send_group_msg(
                    self.websocket,
                    group_id,
                    [
                        generate_reply_message(delete_msg_id),
                        generate_text_message("该小马糕记录已不存在或已被删除"),
                    ]
                )

        # 清理pending记录
        del pending_get_msg[echo_str]

    def _parse_xmg_message(self, raw_message: str):
        """
        从小马糕消息中解析出代码和价格

        Args:
            raw_message: 原始消息内容

        Returns:
            dict: {"code": "小马糕代码", "price": 价格} 或 None
        """
        match = XMG_PATTERN.search(raw_message)
        if match:
            return {
                "code": match.group(1),
                "price": int(match.group(2))
            }
        return None

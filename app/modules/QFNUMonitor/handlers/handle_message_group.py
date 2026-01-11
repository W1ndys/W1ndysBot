"""
QFNUMonitor 群消息处理器
实现对 qfnu.edu.cn 链接的自动摘要回复
"""

import re
from .. import MODULE_NAME, SWITCH_NAME
from core.menu_manager import MENU_COMMAND
from logger import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from utils.auth import is_system_admin
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime
from .data_manager import DataManager
from core.menu_manager import MenuManager
from ..core.QFNUClient import QFNUClient
from ..core.SiliconFlowAPI import SiliconFlowAPI


class GroupMessageHandler:
    """群消息处理器"""

    # 曲师大相关域名正则
    QFNU_URL_PATTERN = re.compile(
        r"https?://[a-zA-Z0-9\-\.]*qfnu\.edu\.cn[^\s<>\"\']+"
    )

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

    async def _handle_qfnu_url(self):
        """
        处理消息中的曲师大链接，自动回复摘要
        """
        # 检测消息中的曲师大链接
        urls = self.QFNU_URL_PATTERN.findall(self.raw_message)
        if not urls:
            return False

        logger.info(f"[{MODULE_NAME}] 检测到曲师大链接: {urls}")

        # 检查 API 是否可用
        summary_api = SiliconFlowAPI()
        if not summary_api.is_available():
            logger.warning(f"[{MODULE_NAME}] 硅基流动 API 不可用，跳过摘要生成")
            return False

        # 初始化数据管理器和客户端
        data_manager = DataManager()
        client = QFNUClient()

        processed = False
        # 发一个群消息提示处理中
        await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message("🤖 正在为检测到的曲师大链接生成摘要，请稍候..."),
                ],
            )
        for url in urls[:3]:  # 最多处理3个链接
            try:
                # 检查缓存
                cached_summary = data_manager.get_cached_summary(url)
                if cached_summary:
                    logger.info(f"[{MODULE_NAME}] 使用缓存的摘要: {url}")
                    await self._send_summary_reply(url, cached_summary)
                    processed = True
                    continue

                # 获取页面内容
                content = await client.get_announcement_content(url)
                if not content:
                    logger.warning(f"[{MODULE_NAME}] 无法获取页面内容: {url}")
                    continue

                # 生成摘要
                summary = await summary_api.summarize_url_content(
                    title="",  # 可以从页面获取标题
                    content=content,
                    url=url,
                )

                if summary:
                    # 缓存摘要
                    data_manager.cache_summary(url, "", summary)
                    # 发送摘要回复
                    await self._send_summary_reply(url, summary)
                    processed = True
                else:
                    logger.warning(f"[{MODULE_NAME}] 生成摘要失败: {url}")

            except Exception as e:
                logger.error(f"[{MODULE_NAME}] 处理链接 {url} 失败: {e}")

        data_manager.close()
        return processed

    async def _send_summary_reply(self, url: str, summary: str):
        """
        发送摘要回复

        Args:
            url: 链接地址
            summary: 摘要内容
        """
        message_lines = [
            "🤖 智能摘要",
            "",
            f"📝 {summary}",
            "",
            f"🔗 {url}",
        ]
        message = "\n".join(message_lines)

        await send_group_msg(
            self.websocket,
            self.group_id,
            [
                generate_reply_message(self.message_id),
                generate_text_message(message),
            ],
        )
        logger.info(f"[{MODULE_NAME}] 发送摘要回复到群 {self.group_id}")

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

            # 处理曲师大链接
            if await self._handle_qfnu_url():
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

from .. import MODULE_NAME, SWITCH_NAME
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from core.auth import is_system_admin, is_group_admin
from api.message import send_group_msg, delete_msg, send_private_msg
from api.group import set_group_ban
from utils.generate import (
    generate_text_message,
    generate_reply_message,
    generate_at_message,
)
from datetime import datetime
from core.menu_manager import MenuManager
from ..core.qr_detector import QRDetector
import re
import html
import urllib.parse
from config import OWNER_ID


class GroupMessageHandler:
    """群消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.sub_type = msg.get("sub_type", "")
        self.group_id = str(msg.get("group_id", ""))
        self.message_id = str(msg.get("message_id", ""))
        self.user_id = str(msg.get("user_id", ""))
        self.message = msg.get("message", {})
        self.raw_message = msg.get("raw_message", "")
        self.sender = msg.get("sender", {})
        self.nickname = self.sender.get("nickname", "")
        self.card = self.sender.get("card", "")
        self.role = self.sender.get("role", "")
        self.url = ""
        # 初始化二维码检测器
        self.qr_detector = QRDetector()

    async def handle(self):
        """处理群消息"""
        try:
            # 处理开关命令
            if self.raw_message.lower() == SWITCH_NAME.lower():
                if not is_system_admin(self.user_id):
                    logger.error(f"[{MODULE_NAME}]{self.user_id}无权限切换群聊开关")
                    return
                await handle_module_group_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.group_id,
                    self.message_id,
                )
                return

            # 处理菜单命令
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
                return

            # 检查开关状态
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 忽略系统管理员和群主群管理员
            if is_system_admin(self.user_id) or is_group_admin(self.role):
                return

            # 检测视频和图片中的二维码
            await self._handle_media_qr_detection()

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

    async def _handle_media_qr_detection(self):
        """处理媒体文件的二维码检测"""
        media_url = self._extract_media_url()
        if not media_url:
            return

        media_type, url = media_url
        logger.info(f"[{MODULE_NAME}]{media_type}链接: {url}")

        # 根据媒体类型调用相应的检测方法
        if media_type == "video":
            result = await self.qr_detector.detect_video_from_url(url)
        elif media_type == "image":
            result = await self.qr_detector.detect_image_from_url(url)
        else:
            return

        # 处理检测结果
        if result["success"] and result["has_qr_code"]:
            await self._handle_qr_detected(media_type)

    def _extract_media_url(self):
        """
        从消息中提取媒体URL

        Returns:
            tuple: (media_type, url) 或 None
        """
        # 检测视频
        if self.raw_message.startswith("[CQ:video,file="):
            pattern = r"url=(.*?),file_size="
            match = re.search(pattern, self.raw_message)
            if match:
                url = self._decode_url(match.group(1))
                self.url = url
                return ("video", url)

        # 检测图片
        elif self.raw_message.startswith("[CQ:image,file="):
            pattern = r"url=(.*?),file_size="
            match = re.search(pattern, self.raw_message)
            if match:
                url = self._decode_url(match.group(1))
                self.url = url
                return ("image", url)

        return None

    def _decode_url(self, url):
        """
        解码URL

        Args:
            url (str): 编码的URL

        Returns:
            str: 解码后的URL
        """
        # URL解码处理
        url = html.unescape(url)  # 处理 &amp; 等HTML实体
        url = urllib.parse.unquote(url)  # 处理URL编码
        return url

    async def _handle_qr_detected(self, media_type):
        """
        处理检测到二维码的情况

        Args:
            media_type (str): 媒体类型 ("video" 或 "image")
        """
        # 发送警告消息
        await send_group_msg(
            self.websocket,
            self.group_id,
            [
                generate_at_message(self.user_id),
                generate_text_message(
                    f"({self.user_id})禁止发送包含二维码的{media_type == 'video' and '视频' or '图片'}"
                ),
            ],
            note="del_msg=30",
        )

        # 禁言用户
        await set_group_ban(
            self.websocket,
            self.group_id,
            self.user_id,
            60 * 60 * 24 * 30,  # 禁言30天
        )

        # 撤回消息
        await delete_msg(self.websocket, self.message_id)

        # 上报给系统管理员
        await send_private_msg(
            self.websocket,
            OWNER_ID,
            [
                generate_text_message(
                    f"二维码警告提醒\n"
                    f"group_id={self.group_id}\n"
                    f"user_id={self.user_id}\n"
                    f"nickname={self.nickname}\n"
                    f"时间={self.formatted_time}\n"
                    f"media_type={media_type}\n"
                    f"url={self.url}"
                ),
            ],
            note="del_msg=30",
        )

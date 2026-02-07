import re
import uuid
import time
import asyncio
from datetime import datetime
from .. import MODULE_NAME, SWITCH_NAME, pending_get_msg
from ..handlers.data_manager import DataManager
from logger import logger
from core.switchs import is_group_switch_on, handle_module_group_switch, get_all_enabled_groups
from utils.auth import is_system_admin
from api.message import send_group_msg, get_msg
from utils.generate import generate_text_message, generate_reply_message
from core.menu_manager import MenuManager, MENU_COMMAND
from config import OWNER_ID


# 高价推送阈值
HIGH_PRICE_THRESHOLD = 800


# 小马糕消息正则表达式
XMG_PATTERN = re.compile(
    r'王者荣耀【(.+?)】我的小马糕今天(\d+)块，复制链接来我的市集出售，马年上分大吉！'
)


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

    async def _handle_switch_command(self):
        """
        处理群聊开关命令（仅owner可操作）
        """
        if self.raw_message.lower() == SWITCH_NAME.lower():
            # 仅允许owner控制开关
            if self.user_id != OWNER_ID:
                logger.error(f"[{MODULE_NAME}]{self.user_id}无权限切换群聊开关，仅owner({OWNER_ID})可操作")
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("仅机器人主人可控制此开关"),
                    ],
                    note="del_msg=10",
                )
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

    async def _handle_delete(self) -> bool:
        """
        处理删除小马糕逻辑
        返回True表示已处理
        
        支持两种方式：
        1. 消息包含"删除" + 引用任意消息 → 解析引用消息中的小马糕代码删除
        2. 消息包含"删除" + 消息中包含小马糕代码 → 直接解析当前消息中的代码删除
        """
        # 检查消息是否包含"删除"
        if "删除" not in self.raw_message:
            return False

        # 尝试从当前消息中解析小马糕代码
        xmg_info = self._parse_xmg_message(self.raw_message)
        
        if xmg_info:
            # 方式2：当前消息包含小马糕代码，直接删除
            return await self._do_delete(xmg_info["code"], xmg_info["price"])

        # 方式1：检查是否有引用消息
        message_segments = self.msg.get("message", [])
        reply_msg_id = None
        for segment in message_segments:
            if segment.get("type") == "reply":
                reply_msg_id = str(segment.get("data", {}).get("id", ""))
                break

        if not reply_msg_id:
            # 既没有小马糕代码，也没有引用消息，不处理
            return False

        # 使用echo机制调用get_msg获取被引用消息的内容
        key = uuid.uuid4().hex[:8]
        # echo格式: key={uuid}_gid={group_id}_uid={user_id}_mid={reply_msg_id}
        echo_str = f"key={key}_gid={self.group_id}_uid={self.user_id}_mid={reply_msg_id}"

        # 存储到pending，记录删除请求信息
        pending_get_msg[echo_str] = {
            "group_id": self.group_id,
            "user_id": self.user_id,
            "message_id": reply_msg_id,  # 被引用的消息ID
            "delete_msg_id": self.message_id,  # "删除"消息ID，用于回复
            "timestamp": time.time()
        }

        # 调用get_msg获取被引用消息的内容
        await get_msg(
            self.websocket,
            reply_msg_id,
            note=f"wzryxmg_get_{echo_str}"
        )

        logger.info(f"[{MODULE_NAME}]用户{self.user_id}请求删除小马糕，已发送get_msg请求，echo: {echo_str}")
        return True

    async def _do_delete(self, xmg_code: str, price: int = 0) -> bool:
        """
        执行删除操作（全库范围）
        
        Args:
            xmg_code: 小马糕代码
            price: 价格（用于显示，可选）
        
        Returns:
            bool: 是否成功处理
        """
        with DataManager() as dm:
            deleted = dm.delete_by_xmg_code(xmg_code)

            if deleted:
                price_text = f"（{price}块）" if price > 0 else ""
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(f"已删除小马糕【{xmg_code}】{price_text}的记录"),
                    ]
                )
                logger.info(f"[{MODULE_NAME}]用户{self.user_id}删除了小马糕记录，代码：{xmg_code}")
            else:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("未找到该小马糕记录，可能已被删除或从未存储"),
                    ]
                )
        return True

    async def _handle_high_price_query(self) -> bool:
        """
        处理高价小马糕查询（全库查询）
        返回True表示已处理
        """
        # 必须包含"高价小马糕"才触发查询
        if "高价小马糕" not in self.raw_message:
            return False
        
        # 如果消息匹配小马糕存储格式，不触发查询（交给存储逻辑处理）
        if XMG_PATTERN.match(self.raw_message):
            return False

        # 先清理过期数据
        with DataManager() as dm:
            expired_count = dm.delete_expired_records()
            if expired_count > 0:
                logger.info(f"[{MODULE_NAME}]清理了{expired_count}条过期的小马糕记录")

            # 查询全库当天最高价（所有群）
            record = dm.get_global_highest_price_xmg()

            if not record:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("今天还没有人分享小马糕哦~"),
                    ]
                )
                logger.info(f"[{MODULE_NAME}]用户{self.user_id}查询高价小马糕，无记录")
                return True

            # 构造消息
            message_content = record["full_message"]
            hint = "\n\n若该小马糕无额度，可回复本条消息删除该条数据"

            # 直接发送高价小马糕消息
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(message_content + hint),
                ]
            )
            logger.info(f"[{MODULE_NAME}]用户{self.user_id}查询高价小马糕，返回价格：{record['price']}，代码：{self._extract_xmg_code(record['full_message'])}")
        return True

    async def _handle_xmg_message(self, silent: bool = False):
        """
        处理小马糕消息收集
        
        Args:
            silent: 是否静默模式（不发送提示）
        """
        match = XMG_PATTERN.match(self.raw_message)
        if not match:
            return

        # 提取信息
        xmg_code = match.group(1)  # 小马糕代码
        price = int(match.group(2))  # 价格

        # 存储到数据库（所有群都存储）
        with DataManager() as dm:
            success = dm.add_xmg(
                group_id=self.group_id,
                user_id=self.user_id,
                nickname=self.nickname,
                full_message=self.raw_message,
                price=price
            )

            if success:
                logger.info(f"[{MODULE_NAME}]已存储{self.nickname}的小马糕，代码：{xmg_code}，价格：{price}，群组：{self.group_id}")
                
                # 非静默模式下发送群提示
                if not silent:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(f"已记录你的{xmg_code}小马糕（{price}块）"),
                        ],
                        note="del_msg=30",
                    )
                
                # 高价小马糕推送：价格 >= 800时，推送到所有已开启功能的群
                if price >= HIGH_PRICE_THRESHOLD:
                    await self._push_high_price_xmg(xmg_code, price)
            else:
                logger.debug(f"[{MODULE_NAME}]小马糕已存在，代码：{xmg_code}，价格：{price}，群组：{self.group_id}")

    def _extract_xmg_code(self, full_message: str) -> str:
        """
        从小马糕消息中提取代码

        Args:
            full_message: 完整的小马糕消息

        Returns:
            小马糕代码，如"东方不败1JGNNX"
        """
        match = XMG_PATTERN.search(full_message)
        if match:
            return match.group(1)
        return ""

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

    async def _push_high_price_xmg(self, xmg_code: str, price: int):
        """
        推送高价小马糕到所有已开启功能的群
        
        Args:
            xmg_code: 小马糕代码
            price: 价格
        """
        try:
            # 获取所有已开启功能的群
            enabled_groups = get_all_enabled_groups(MODULE_NAME)
            
            if not enabled_groups:
                logger.debug(f"[{MODULE_NAME}]没有开启功能的群，跳过高价推送")
                return
            
            # 构造推送消息
            push_message = (
                f"🎉 发现高价小马糕！\n"
                f"代码：{xmg_code}\n"
                f"价格：{price}块\n"
                f"来自群：{self.group_id}\n"
                f"\n{self.raw_message}"
            )
            
            # 推送到所有已开启的群（排除当前群，避免重复）
            push_tasks = []
            for group_id in enabled_groups:
                if str(group_id) == self.group_id:
                    continue  # 跳过当前群
                push_tasks.append(
                    send_group_msg(
                        self.websocket,
                        group_id,
                        generate_text_message(push_message),
                    )
                )
            
            if push_tasks:
                # 并发发送，不阻塞
                asyncio.create_task(self._send_push_messages(push_tasks))
                logger.info(f"[{MODULE_NAME}]检测到高价小马糕（{price}块），正在推送到{len(push_tasks)}个群")
            
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]推送高价小马糕失败: {e}")
    
    async def _send_push_messages(self, tasks):
        """
        批量发送推送消息（后台执行，不阻塞主流程）
        """
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]批量发送推送消息失败: {e}")

    async def handle(self):
        """
        处理群消息
        """
        try:
            # 处理群聊开关命令（无视开关状态）
            if await self._handle_switch_command():
                return

            # 处理菜单命令（无视开关状态）
            if await self._handle_menu_command():
                return

            # 【静默收集】所有群的小马糕消息（无论开关是否开启）
            # 但只有开启功能的群才会收到提示
            is_switch_on = is_group_switch_on(self.group_id, MODULE_NAME)
            await self._handle_xmg_message(silent=not is_switch_on)

            # 如果没开启群聊开关，后续功能不处理
            if not is_switch_on:
                return

            # 检查是否为删除操作（优先级最高）
            if await self._handle_delete():
                return

            # 检查是否为高价查询
            if await self._handle_high_price_query():
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

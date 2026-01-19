import asyncio
from datetime import datetime
from logger import logger
from utils.auth import is_group_admin, is_system_admin
from api.message import send_group_msg, delete_msg, send_private_msg
from utils.generate import generate_text_message, generate_reply_message, generate_at_message
from core.switchs import is_group_switch_on, handle_module_group_switch
from core.menu_manager import MenuManager
from .. import (
    MODULE_NAME,
    SWITCH_NAME,
    SET_SENTIMENT_THRESHOLD_COMMAND
)
from .data_manager import SentimentDataManager
from .sentiment_analyzer import SentimentAnalyzer


class SentimentMessageHandler:
    """
    舆情监控消息处理器
    """

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.group_id = str(msg.get("group_id", ""))
        self.message_id = str(msg.get("message_id", ""))
        self.user_id = str(msg.get("user_id", ""))
        self.message = msg.get("message", {})
        self.raw_message = msg.get("raw_message", "")
        self.sender = msg.get("sender", {})
        self.nickname = self.sender.get("nickname", "")
        self.card = self.sender.get("card", "")
        self.role = self.sender.get("role", "")
        
        # 初始化数据管理器和情绪分析器
        self.data_manager = SentimentDataManager(self.group_id)
        self.analyzer = SentimentAnalyzer()
        
        # 判断是否在私聊环境
        self.is_private = self.group_id == "0"

    async def handle_set_sentiment_threshold(self):
        """
        设置情绪判断阈值
        """
        try:
            # 权限检查
            if self.is_private:
                if not is_system_admin(self.user_id):
                    return
                target_group_id = None
                scope = "全局"
            else:
                if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                    return
                target_group_id = self.group_id
                scope = f"群{self.group_id}"

            # 解析阈值参数
            content = self.raw_message.lstrip(SET_SENTIMENT_THRESHOLD_COMMAND).strip()
            try:
                threshold = float(content)
                if not (0 <= threshold <= 1):
                    raise ValueError("阈值必须在0到1之间")
            except ValueError as e:
                error_msg = f"参数错误: {str(e)}，请提供0到1之间的数值"
                if self.is_private:
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [generate_text_message(error_msg)]
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(error_msg)
                        ],
                        note="del_msg=10"
                    )
                return

            # 设置阈值
            self.data_manager.set_threshold(threshold, target_group_id)
            
            # 发送响应消息
            response_msg = f"已在{scope}设置情绪判断阈值为 {threshold}"
            if self.is_private:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [generate_text_message(response_msg)]
                )
            else:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(response_msg)
                    ],
                    note="del_msg=10"
                )
                
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]设置情绪判断阈值失败: {e}")

    async def handle_sentiment_analysis(self):
        """
        执行情绪分析并处理负面情绪消息
        """
        try:
            # 检查是否启用了舆情监控
            if not self.data_manager.is_enabled(self.group_id):
                return
                
            # 管理员不受监控
            if is_group_admin(self.role) or is_system_admin(self.user_id):
                return

            # 获取用户名用于日志记录
            user_name = self.card if self.card else self.nickname

            # 分析消息情绪
            result = await self.analyzer.analyze_sentiment(
                self.raw_message, 
                self.group_id, 
                self.user_id, 
                user_name
            )
            
            # 如果是负面情绪，执行相应操作
            if result["is_negative"]:
                logger.info(f"[{MODULE_NAME}]检测到负面情绪消息，群号: {self.group_id}, 用户: {self.user_id}, 置信度: {result['confidence']}")
                
                # 删除消息 (立即删除，不等待)
                await delete_msg(self.websocket, self.message_id)
                
                # 通知用户 (15秒后撤回)
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_at_message(self.user_id),
                        generate_text_message(f"({user_name}) 您的消息含有不当情绪表达，已被系统自动撤回")
                    ],
                    note="del_msg=15"
                )
                
                # 记录日志 (实际15秒后撤回)
                logger.warning(
                    f"[{MODULE_NAME}]已撤回负面情绪消息 - "
                    f"群号: {self.group_id}, 用户: {self.user_id} ({user_name}), "
                    f"消息: {self.raw_message[:50]}..., 置信度: {result['confidence']:.2f} (15秒后撤回)"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]执行情绪分析失败: {e}")
            
        return False

    async def handle(self):
        """
        统一处理入口
        """
        try:
            # 处理开关命令
            if self.raw_message.lower() == SWITCH_NAME.lower():
                if not is_system_admin(self.user_id) and not is_group_admin(self.role):
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
            if self.raw_message.lower() == f"{SWITCH_NAME}menu".lower():
                menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(menu_text),
                    ],
                    note="del_msg=30"
                )
                return

            # 检查开关状态
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 处理设置情绪阈值命令
            if self.raw_message.startswith(SET_SENTIMENT_THRESHOLD_COMMAND):
                await self.handle_set_sentiment_threshold()
                return

            # 处理情绪分析 (对所有消息进行分析)
            await self.handle_sentiment_analysis()
            
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理消息失败: {e}")
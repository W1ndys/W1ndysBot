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

    def _format_question_result(self, question_data: tuple) -> str:
        """
        格式化题目结果为回复文本

        Args:
            question_data: 题目数据元组
                (id, type, question, optionA, optionB, optionC, optionD, optionAnswer)

        Returns:
            格式化后的文本
        """
        _, q_type, question, opt_a, opt_b, opt_c, opt_d, answer = question_data

        # 选项标记：正确答案用✅，错误答案用❌
        options = {"A": opt_a, "B": opt_b, "C": opt_c, "D": opt_d}
        option_lines = []
        for key, value in options.items():
            if value:  # 只显示非空选项
                if key == answer:
                    option_lines.append(f"✅ {key}. {value}")
                else:
                    option_lines.append(f"❌ {key}. {value}")

        result = f"【{q_type}】{question}\n" + "\n".join(option_lines)
        return result

    async def _handle_question_query(self):
        """
        处理题目查询
        """
        # 消息内容作为搜索关键词
        keyword = self.raw_message.strip()

        # 忽略过短的消息（避免误触发）
        if len(keyword) < 2:
            return False

        with DataManager() as dm:
            results = dm.search_questions(keyword, limit=10)

            if not results:
                return False

            # 选择匹配长度最高的结果（题目与关键词重叠字符数最多）
            best_match = max(results, key=lambda x: len(set(keyword) & set(x[2])))

            # 格式化结果并添加署名
            reply_text = self._format_question_result(best_match)
            reply_text += "\n默认只会返回1个，若未找到请使用更长的关键词\n技术支持：微信公众号《卷卷爱吃曲奇饼干》"

            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(reply_text),
                ],
            )
            logger.info(
                f"[{MODULE_NAME}]群{self.group_id}用户{self.user_id}查询题目: {keyword}"
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

            # 处理题目查询
            await self._handle_question_query()

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

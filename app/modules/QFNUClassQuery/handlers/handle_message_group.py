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
import re


# 教学楼名称映射（支持多种输入方式）
BUILDING_ALIASES = {
    "1号楼": "1号教学楼",
    "1号": "1号教学楼",
    "1教": "1号教学楼",
    "一号楼": "1号教学楼",
    "一教": "1号教学楼",
    "1号教学楼": "1号教学楼",
    "2号楼": "2号教学楼",
    "2号": "2号教学楼",
    "2教": "2号教学楼",
    "二号楼": "2号教学楼",
    "二教": "2号教学楼",
    "2号教学楼": "2号教学楼",
    "3号楼": "3号教学楼",
    "3号": "3号教学楼",
    "3教": "3号教学楼",
    "三号楼": "3号教学楼",
    "三教": "3号教学楼",
    "3号教学楼": "3号教学楼",
    "综合楼": "综合实验楼",
    "综合": "综合实验楼",
    "综合实验楼": "综合实验楼",
    "图书馆": "图书馆",
}


def parse_empty_classroom_query(text: str) -> dict:
    """
    解析空教室查询文本

    格式：空教室 教学楼 节次起始 日期偏移（空格分割）
    节次和日期偏移允许为空，默认为1-11节，偏移0

    格式示例：
    - "空教室 1号楼" -> 1号教学楼，1-11节，今天
    - "空教室 1号楼 1-4" -> 1号教学楼，1-4节，今天
    - "空教室 综合楼 5-8 1" -> 综合实验楼，5-8节，明天
    - "空教室 2号楼 1-2 0" -> 2号教学楼，1-2节，今天

    :param text: 用户输入的查询文本
    :return: 解析结果字典，包含 building, start_section, end_section, date_offset
             如果解析失败，返回 error 字段
    """
    result = {
        "building": None,
        "start_section": 1,  # 默认1节
        "end_section": 11,  # 默认11节
        "date_offset": 0,  # 默认今天
        "error": None,
    }

    # 移除命令前缀
    text = text.replace(EMPTY_CLASSROOM_COMMAND, "").strip()

    if not text:
        result["error"] = "请输入查询参数，格式：空教室 教学楼 节次 日期偏移\n例如：空教室 1号楼 1-4 1\n节次和日期偏移可省略，默认1-11节、今天"
        return result

    # 按空格分割参数
    parts = text.split()

    # 第一部分：教学楼
    if len(parts) >= 1:
        building_text = parts[0].strip()
        # 解析教学楼（按长度降序匹配，避免部分匹配问题）
        sorted_aliases = sorted(BUILDING_ALIASES.keys(), key=len, reverse=True)
        for alias in sorted_aliases:
            if alias in building_text:
                result["building"] = BUILDING_ALIASES[alias]
                break

    if not result["building"]:
        result["error"] = "请指定教学楼名称，支持：1号楼/2号楼/3号楼/综合楼 等\n格式：空教室 教学楼 节次 日期偏移"
        return result

    # 第二部分：节次范围（如果有）
    if len(parts) >= 2:
        section_text = parts[1].strip()
        section_pattern = r"(\d+)\s*[-~到至]\s*(\d+)"
        match = re.search(section_pattern, section_text)
        if match:
            result["start_section"] = int(match.group(1))
            result["end_section"] = int(match.group(2))
        else:
            # 尝试匹配单节次
            single_pattern = r"(\d+)"
            match = re.search(single_pattern, section_text)
            if match:
                result["start_section"] = int(match.group(1))
                result["end_section"] = int(match.group(1))

    # 第三部分：日期偏移（如果有）
    if len(parts) >= 3:
        offset_text = parts[2].strip()
        if offset_text:
            try:
                result["date_offset"] = int(offset_text)
            except ValueError:
                result["error"] = "日期偏移必须是整数，如 0=今天，1=明天，-1=昨天"
                return result

    # 验证节次范围
    if result["start_section"] < 1 or result["end_section"] > 13:
        result["error"] = "节次范围应在 1-13 之间"
        return result

    if result["start_section"] > result["end_section"]:
        result["error"] = "开始节次不能大于结束节次"
        return result

    return result


def format_classroom_result(data: dict) -> str:
    """
    格式化空教室查询结果

    :param data: API 返回的数据
    :return: 格式化后的文本
    """
    query_info = data.get("query_info", {})
    classrooms = data.get("classrooms", [])
    total = data.get("total", 0)
    cache_info = data.get("cache_info", {})

    lines = []
    lines.append(f"📍 {query_info.get('building', '未知')}")
    lines.append(f"📅 {query_info.get('date', '')} {query_info.get('weekday', '')}")
    lines.append(f"📚 第{query_info.get('week', '?')}周 {query_info.get('section', '')}")
    lines.append("")

    if total > 0:
        lines.append(f"🏫 共找到 {total} 间空教室：")
        # 对教室号进行排序
        sorted_classrooms = sorted(classrooms, key=lambda x: (len(x), x))
        lines.append("、".join(sorted_classrooms))
    else:
        lines.append("😔 该时段没有空教室")

    if cache_info.get("from_cache"):
        lines.append(f"\n(缓存数据，更新于 {cache_info.get('cached_at', '未知')})")

    return "\n".join(lines)


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

    async def _handle_empty_classroom_command(self):
        """
        处理空教室查询命令
        """
        if EMPTY_CLASSROOM_COMMAND not in self.raw_message:
            return False

        # 解析用户输入
        parsed = parse_empty_classroom_query(self.raw_message)

        if parsed.get("error"):
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(parsed["error"]),
                ],
            )
            return True

        # 调用 API 查询
        try:
            result = await QFNUClassApiClient.query_empty_classroom(
                building=parsed["building"],
                start_section=parsed["start_section"],
                end_section=parsed["end_section"],
                date_offset=parsed["date_offset"],
            )

            # 检查 API 返回结果
            if result.get("success") is False:
                error_msg = result.get("error", "查询失败，请稍后重试")
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(f"❌ {error_msg}"),
                    ],
                )
                return True

            # 检查 API 返回的 code
            if result.get("code") != 200:
                error_msg = result.get("msg", "查询失败，请稍后重试")
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(f"❌ {error_msg}"),
                    ],
                )
                return True

            # 格式化并返回结果
            data = result.get("data", {})
            response_text = format_classroom_result(data)
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(response_text),
                ],
            )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]查询空教室失败: {e}")
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message("❌ 查询失败，请稍后重试"),
                ],
            )

        return True

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
            if await self._handle_empty_classroom_command():
                return

            # 检查是否包含教室课表命令
            if CLASS_SCHEDULE_COMMAND in self.raw_message:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            "教室课表功能正在开发中，敬请期待"
                        ),
                    ],
                )
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

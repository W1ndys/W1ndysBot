from .. import MODULE_NAME, SWITCH_NAME, BASE_COMMAND
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

    async def _handle_gpa_percentile_command(self):
        """
        处理绩点百分比查询命令

        格式：绩点百分比 班级名称 学期 目标绩点
        示例：绩点百分比 22网安 2024-2025-1 3.91
        示例：绩点百分比 24电子信息 all 3.64
        """
        raw = self.raw_message.strip()

        # 检查是否以绩点百分比开头
        if not raw.startswith(BASE_COMMAND):
            return False

        # 解析命令参数
        parts = raw.split()

        # 检查参数数量
        if len(parts) < 4:
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(
                        f"❌ 参数不足\n"
                        f"用法：{BASE_COMMAND} 班级名称 学期 目标绩点\n"
                        f"示例：{BASE_COMMAND} 22网安 2024-2025-1 3.91\n"
                        f"示例：{BASE_COMMAND} 24电子信息 all 3.64\n"
                        f"学期格式：xxxx-xxxx-x 或 all（代表全部学期）"
                    ),
                ],
                note="del_msg=30",
            )
            return True

        # 提取参数
        # parts[0] = "绩点百分比"
        # parts[1] = 班级名称（可能包含空格，但这里我们假设没有空格）
        # parts[2] = 学期
        # parts[3] = 目标绩点

        class_name_input = parts[1]
        term_input = parts[2]
        target_gpa_input = parts[3]

        # 验证学期格式
        if term_input != "all":
            # 检查格式 xxxx-xxxx-x
            import re

            if not re.match(r"^\d{4}-\d{4}-\d$", term_input):
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            f"❌ 学期格式错误\n"
                            f"学期格式应为 xxxx-xxxx-x 或 all\n"
                            f"例如：2024-2025-1 或 all"
                        ),
                    ],
                    note="del_msg=30",
                )
                return True

        # 验证目标绩点为数字
        try:
            target_gpa = float(target_gpa_input)
            if target_gpa < 0 or target_gpa > 5:
                raise ValueError("绩点范围应在 0-5 之间")
        except ValueError as e:
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(
                        f"❌ 目标绩点格式错误\n"
                        f"绩点应为 0-5 之间的数字\n"
                        f"错误信息：{e}"
                    ),
                ],
                note="del_msg=30",
            )
            return True

        # 查询数据库
        try:
            with DataManager() as dm:
                # 模糊匹配班级名称
                matched_classes = dm.find_class_by_fuzzy_name(class_name_input)

                if not matched_classes:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"❌ 未找到班级：{class_name_input}\n"
                                f"请检查班级名称是否是教务系统内标准的班级名称，支持子串查询无需使用完整名字，或尝试使用更简短的名称（如：22网安、01中文、24计1）"
                            ),
                        ],
                        note="del_msg=30",
                    )
                    return True

                # 查询所有匹配班级的百分位数据
                results = []
                for class_name in matched_classes:
                    # 检查学期是否有效
                    available_terms = dm.get_available_terms(class_name)
                    if term_input != "all" and term_input not in available_terms:
                        continue

                    # 查询百分位
                    result = dm.calculate_gpa_percentile(
                        class_name, term_input, target_gpa
                    )
                    if result:
                        results.append(result)

                if not results:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"❌ 未找到符合条件的班级数据\n" f"学期：{term_input}"
                            ),
                        ],
                        note="del_msg=30",
                    )
                    return True

                # 构建回复消息
                term_display = "全部学期" if term_input == "all" else term_input

                reply_text = (
                    f"📊 绩点百分位查询结果\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"学期：{term_display} | 目标绩点：{target_gpa}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"班级-位居比例\n"
                )

                # 添加每个班级的结果
                for result in results:
                    reply_text += (
                        f"【{result['class_name']}】-【{result['rank_percent']}%】\n"
                    )

                reply_text += (
                    f"━━━━━━━━━━━━━━━\n"
                    f"💡 提示：位居比例表示该绩点位于班级前百分之多少的位置（数值越小排名越靠前）\n"
                    f"结果基于正态分布的统计学估算模型生成，可参考性85%以上，仅供学业规划参考，不代表官方数据"
                )

                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(reply_text),
                    ],
                    note="del_msg=120",
                )
                return True

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]查询绩点百分位失败: {e}")
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(f"❌ 查询失败：{str(e)}"),
                ],
                note="del_msg=30",
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

            # 处理绩点百分比查询命令
            if await self._handle_gpa_percentile_command():
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

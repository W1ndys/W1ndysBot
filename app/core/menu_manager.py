import importlib
import os
import logger
from typing import Dict, List, Optional
from utils.generate import generate_reply_message, generate_text_message
from api.message import send_group_msg, send_private_msg

# 菜单命令
MENU_COMMAND = "menu"


class MenuManager:
    """菜单管理器 - 用于收集和展示所有模块的菜单信息"""

    @staticmethod
    def get_all_modules() -> List[str]:
        """获取所有模块名称"""
        modules_dir = os.path.join(os.path.dirname(__file__), "..", "modules")
        modules = []
        for item in os.listdir(modules_dir):
            if os.path.isdir(os.path.join(modules_dir, item)) and not item.startswith(
                "_"
            ):
                modules.append(item)
        return modules

    @staticmethod
    def get_module_menu_info(module_name: str) -> Optional[Dict]:
        """获取单个模块的菜单信息"""
        try:
            module = importlib.import_module(f"modules.{module_name}")
            menu_info = {
                "name": getattr(module, "MODULE_NAME", module_name),
                "commands": getattr(module, "COMMANDS", {}),
                "description": getattr(module, "MODULE_DESCRIPTION", "暂无描述"),
                "switch_name": getattr(module, "SWITCH_NAME", ""),
            }
            return menu_info
        except Exception as e:
            logger.error(f"获取模块 {module_name} 菜单信息失败: {e}")
            return None

    @staticmethod
    def get_module_commands_text(module_name: str) -> str:
        """
        获取单个模块的可用命令及其解释，返回格式化文本
        """
        try:
            module = importlib.import_module(f"modules.{module_name}")
            commands = getattr(module, "COMMANDS", {})
            if not commands:
                return "暂无可用命令。"
            text = ""
            for cmd, desc in commands.items():
                text += f"{cmd}: {desc}\n\n"
            return text
        except Exception as e:
            logger.error(f"获取模块 {module_name} 命令信息失败: {e}")
            return "获取命令信息失败。"

    @staticmethod
    def generate_menu_text() -> str:
        """生成完整的菜单文本"""
        menu_text = "📋 功能菜单\n\n"
        # 获取所有模块并按字母顺序排序
        modules = sorted(MenuManager.get_all_modules())
        for module_name in modules:
            menu_info = MenuManager.get_module_menu_info(module_name)
            if menu_info:
                menu_text += f"【{menu_info['name']}】：{menu_info['description']}\n"
                menu_text += f"开关: {menu_info['switch_name']}\n"
                menu_text += "\n"
        menu_text += "发送开关命令+menu，可以查看该模块的所有子命令\n"
        menu_text += "框架作者：http://github.com/W1ndys\n"
        menu_text += "卷卷的交流小窝：489237389\n"
        return menu_text


async def handle_events(websocket, message):
    """
    统一处理 menu 命令，支持群聊和私聊
    """
    try:

        # 只处理文本消息
        if message.get("post_type") != "message":
            return
        raw_message = message.get("raw_message", "").lower()
        if raw_message != MENU_COMMAND:
            return
        # 判断消息类型
        message_type = message.get("message_type", "")

        reply_message = generate_reply_message(message.get("message_id", ""))
        menu_text = MenuManager.generate_menu_text()
        text_message = generate_text_message(menu_text)
        if message_type == "group":
            group_id = str(message.get("group_id", ""))
            await send_group_msg(
                websocket,
                group_id,
                [reply_message, text_message],
                note="del_msg=30",
            )
        elif message_type == "private" and message.get("sub_type") == "friend":
            user_id = str(message.get("user_id", ""))
            await send_private_msg(
                websocket,
                user_id,
                [reply_message, text_message],
                note="del_msg=30",
            )
    except Exception as e:
        logger.error(f"[MenuManager]处理全局菜单命令失败: {e}")

"""
开关系统模块
提供统一的开关管理接口
"""

from .switch_manager import SwitchManager
from .command_handler import SwitchCommandHandler
from .migration import SwitchMigration
from .database import db


# 兼容性函数，保持原有API不变
def is_group_switch_on(group_id, module_name):
    """判断群聊开关是否开启"""
    return SwitchManager.is_group_switch_on(group_id, module_name)


def is_private_switch_on(module_name):
    """判断私聊开关是否开启"""
    return SwitchManager.is_private_switch_on(module_name)


def toggle_group_switch(group_id, module_name):
    """切换群聊开关"""
    return SwitchManager.toggle_group_switch(group_id, module_name)


def toggle_private_switch(module_name):
    """切换私聊开关"""
    return SwitchManager.toggle_private_switch(module_name)


def load_group_all_switch(group_id):
    """获取某群组所有模块的开关（保持原有函数名）"""
    return SwitchManager.get_group_all_switches(group_id)


def get_all_enabled_groups(module_name):
    """获取某模块所有已开启的群聊列表"""
    return SwitchManager.get_all_enabled_groups(module_name)


def copy_group_switches(source_group_id, target_group_id):
    """复制群组开关设置"""
    return SwitchManager.copy_group_switches(source_group_id, target_group_id)


async def handle_module_private_switch(module_name, websocket, user_id, message_id):
    """处理模块私聊开关命令"""
    return await SwitchCommandHandler.handle_module_private_switch(
        module_name, websocket, user_id, message_id
    )


async def handle_module_group_switch(module_name, websocket, group_id, message_id):
    """处理模块群聊开关命令"""
    return await SwitchCommandHandler.handle_module_group_switch(
        module_name, websocket, group_id, message_id
    )


async def handle_events(websocket, message):
    """处理开关相关事件"""
    return await SwitchCommandHandler.handle_events(websocket, message)


# 执行自动升级
try:
    success, message = SwitchMigration.upgrade_to_sqlite()
    if success:
        print(f"开关系统自动升级成功: {message}")
    else:
        print(f"开关系统自动升级跳过: {message}")
except Exception as e:
    print(f"开关系统自动升级失败: {e}")


__all__ = [
    "SwitchManager",
    "SwitchCommandHandler",
    "SwitchMigration",
    "is_group_switch_on",
    "is_private_switch_on",
    "toggle_group_switch",
    "toggle_private_switch",
    "load_group_all_switch",
    "get_all_enabled_groups",
    "copy_group_switches",
    "handle_module_private_switch",
    "handle_module_group_switch",
    "handle_events",
]

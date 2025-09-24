"""
开关系统入口文件
重构后的开关管理系统，拆分为多个模块以提高可维护性：
- config.py: 配置常量
- database.py: 数据库操作
- switch_manager.py: 开关管理核心逻辑
- migration.py: 数据迁移
- command_handler.py: 命令处理器

为了保持向后兼容性，此文件提供原有的API接口。
"""

# 导入新的模块化开关系统
from .switch import (
    SwitchManager,
    SwitchCommandHandler,
    SwitchMigration,
)


# 为了完全向后兼容，提供原有API但使用新的实现
def is_group_switch_on(group_id, MODULE_NAME):
    """判断群聊开关是否开启，默认关闭"""
    return SwitchManager.is_group_switch_on(group_id, MODULE_NAME)


def is_private_switch_on(MODULE_NAME):
    """判断私聊开关是否开启，默认关闭"""
    return SwitchManager.is_private_switch_on(MODULE_NAME)


def toggle_group_switch(group_id, MODULE_NAME):
    """切换群聊开关"""
    return SwitchManager.toggle_group_switch(group_id, MODULE_NAME)


def toggle_private_switch(MODULE_NAME):
    """切换私聊开关"""
    return SwitchManager.toggle_private_switch(MODULE_NAME)


def load_group_all_switch(group_id):
    """获取某群组所有模块的开关"""
    return SwitchManager.get_group_all_switches(group_id)


def get_all_enabled_groups(MODULE_NAME):
    """获取某模块所有已开启的群聊列表"""
    return SwitchManager.get_all_enabled_groups(MODULE_NAME)


def copy_group_switches(source_group_id, target_group_id):
    """复制群组开关设置"""
    return SwitchManager.copy_group_switches(source_group_id, target_group_id)


def clean_invalid_group_switches(valid_group_ids):
    """清理不在有效群列表中的群开关数据"""
    return SwitchManager.clean_invalid_group_switches(valid_group_ids)


async def handle_module_private_switch(MODULE_NAME, websocket, user_id, message_id):
    """处理模块私聊开关命令"""
    return await SwitchCommandHandler.handle_module_private_switch(
        MODULE_NAME, websocket, user_id, message_id
    )


async def handle_module_group_switch(MODULE_NAME, websocket, group_id, message_id):
    """处理模块群聊开关命令"""
    return await SwitchCommandHandler.handle_module_group_switch(
        MODULE_NAME, websocket, group_id, message_id
    )


async def handle_events(websocket, message):
    """处理开关相关事件"""
    return await SwitchCommandHandler.handle_events(websocket, message)


# 导出所有公共接口
__all__ = [
    "is_group_switch_on",
    "is_private_switch_on",
    "toggle_group_switch",
    "toggle_private_switch",
    "load_group_all_switch",
    "get_all_enabled_groups",
    "copy_group_switches",
    "clean_invalid_group_switches",
    "handle_module_private_switch",
    "handle_module_group_switch",
    "handle_events",
    "SwitchManager",
    "SwitchCommandHandler",
    "SwitchMigration",
]

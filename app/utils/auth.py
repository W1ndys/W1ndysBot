"""
权限认证
"""

from config import OWNER_ID


def is_system_admin(user_id: str) -> bool:
    """
    判断是否为系统管理员
    参数:
        user_id: str 用户ID
    """
    return user_id == OWNER_ID


def is_group_admin(role: str) -> bool:
    """
    判断是否为群主或管理员
    参数:
        role: str 用户身份
    """
    return role in ["owner", "admin"]

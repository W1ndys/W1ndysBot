"""
权限认证
"""

from config import OWNER_ID


def is_system_owner(user_id: str) -> bool:
    """
    判断是否为系统管理员
    """
    return user_id == OWNER_ID


def is_group_admin(role: str) -> bool:
    """
    判断是否为群主或管理员
    """
    return role in ["owner", "admin"]

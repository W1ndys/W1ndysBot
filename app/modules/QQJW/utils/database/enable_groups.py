import sqlite3
import os
from datetime import datetime, timezone, timedelta
from ... import MODULE_NAME
from logger import logger


class EnableGroupsDatabase:
    """
    CREATE TABLE IF NOT EXISTS enable_groups (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id     INTEGER UNIQUE NOT NULL,
        is_active    INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
        created_at   TEXT
    );
    """

    def __init__(self):
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"data.db")
        self.table_name = "enable_groups"
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def _get_beijing_time(self):
        """获取北京时间（东八区）"""
        beijing_tz = timezone(timedelta(hours=8))
        return datetime.now(beijing_tz).strftime("%Y-%m-%d %H:%M:%S")

    def add_enable_group(self, group_id):
        """
        添加启用群
        优化逻辑：如果不存在则添加，如果存在则将 is_active 设为 1
        """
        try:
            beijing_time = self._get_beijing_time()
            # 查询该群是否已存在
            self.cursor.execute(
                f"SELECT id, is_active FROM {self.table_name} WHERE group_id = ?",
                (group_id,),
            )
            result = self.cursor.fetchone()
            if result:
                # 已存在，判断是否已启用
                if result[1] == 1:
                    # 已经是启用状态
                    return {
                        "success": False,
                        "message": "群组已经是启用状态",
                        "code": 400,
                        "data": {"group_id": group_id, "is_active": 1},
                    }
                else:
                    # 存在但未启用，更新为启用
                    self.cursor.execute(
                        f"UPDATE {self.table_name} SET is_active = 1 WHERE group_id = ?",
                        (group_id,),
                    )
                    self.conn.commit()
                    return {
                        "success": True,
                        "message": "群组启用成功",
                        "code": 200,
                        "data": {"group_id": group_id, "is_active": 1},
                    }
            else:
                # 不存在，插入新记录
                self.cursor.execute(
                    f"INSERT INTO {self.table_name} (group_id, created_at) VALUES (?, ?)",
                    (group_id, beijing_time),
                )
                self.conn.commit()
                return {
                    "success": True,
                    "message": "群组添加并启用成功",
                    "code": 201,
                    "data": {
                        "group_id": group_id,
                        "is_active": 1,
                        "created_at": beijing_time,
                    },
                }
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]启用群操作失败: {e}")
            return {
                "success": False,
                "message": f"操作失败: {str(e)}",
                "code": 500,
                "data": None,
            }

    def get_enable_group_list(self):
        """获取启用群列表，返回群号列表"""
        try:
            self.cursor.execute(
                f"SELECT group_id FROM {self.table_name} WHERE is_active = 1"
            )
            group_list = [item[0] for item in self.cursor.fetchall()]
            return {
                "success": True,
                "message": "获取启用群列表成功",
                "code": 200,
                "data": {"group_list": group_list, "count": len(group_list)},
            }
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取启用群列表失败: {e}")
            return {
                "success": False,
                "message": f"获取失败: {str(e)}",
                "code": 500,
                "data": None,
            }

    def disable_enable_group(self, group_id):
        """禁用启用群（将 is_active 字段设为 0，而不是删除记录）"""
        try:
            # 首先检查群组是否存在以及当前状态
            self.cursor.execute(
                f"SELECT is_active FROM {self.table_name} WHERE group_id = ?",
                (group_id,),
            )
            result = self.cursor.fetchone()

            if not result:
                # 群组不存在
                return {
                    "success": False,
                    "message": "群组不存在",
                    "code": 404,
                    "data": None,
                }

            if result[0] == 0:
                # 群组已经被禁用
                return {
                    "success": False,
                    "message": "群组已经被禁用",
                    "code": 400,
                    "data": {"group_id": group_id, "is_active": 0},
                }

            # 群组存在且当前是启用状态，执行禁用操作
            self.cursor.execute(
                f"UPDATE {self.table_name} SET is_active = 0 WHERE group_id = ?",
                (group_id,),
            )
            self.conn.commit()
            return {
                "success": True,
                "message": "群组禁用成功",
                "code": 200,
                "data": {"group_id": group_id, "is_active": 0},
            }

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]禁用启用群失败: {e}")
            return {
                "success": False,
                "message": f"操作失败: {str(e)}",
                "code": 500,
                "data": None,
            }

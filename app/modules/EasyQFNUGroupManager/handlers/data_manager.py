import sqlite3
import os
from datetime import datetime
from .. import MODULE_NAME, DATA_DIR
from logger import logger


class DataManager:
    """
    数据库管理器，使用with上下文管理
    自动处理数据库目录、文件和表结构的创建
    """

    def __init__(self):
        self.db_path = os.path.join(DATA_DIR, f"{MODULE_NAME}.db")
        self._ensure_db_exists()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
        self.cursor = self.conn.cursor()
        self._ensure_table_exists()

    def _ensure_db_exists(self):
        """确保数据库目录和文件存在"""
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(self.db_path):
            # 创建空数据库文件
            conn = sqlite3.connect(self.db_path)
            conn.close()
            logger.info(f"[{MODULE_NAME}]创建数据库文件: {self.db_path}")

    def _ensure_table_exists(self):
        """确保表结构存在，如果不存在则创建"""
        # 创建用户验证表
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS user_verification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                group_id TEXT NOT NULL,
                join_time INTEGER NOT NULL,
                verified INTEGER DEFAULT 0,
                verify_time INTEGER DEFAULT NULL,
                notified INTEGER DEFAULT 0,
                UNIQUE(user_id, group_id)
            )"""
        )
        self.conn.commit()
        logger.debug(f"[{MODULE_NAME}]表结构检查完成")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
            logger.error(f"[{MODULE_NAME}]数据库操作异常: {exc_val}")
        else:
            self.conn.commit()
        self.conn.close()

    # ============ 用户验证相关操作 ============

    def add_user(self, user_id: str, group_id: str, join_time: int) -> bool:
        """
        添加入群用户记录

        Args:
            user_id: QQ号
            group_id: 群号
            join_time: 入群时间戳

        Returns:
            bool: 是否成功添加
        """
        try:
            self.cursor.execute(
                """INSERT OR REPLACE INTO user_verification
                   (user_id, group_id, join_time, verified, verify_time, notified)
                   VALUES (?, ?, ?, 0, NULL, 0)""",
                (user_id, group_id, join_time),
            )
            self.conn.commit()
            logger.info(f"[{MODULE_NAME}]添加用户记录: {user_id} 群: {group_id}")
            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加用户记录失败: {e}")
            return False

    def verify_user(self, user_id: str, group_id: str) -> bool:
        """
        验证用户通过

        Args:
            user_id: QQ号
            group_id: 群号

        Returns:
            bool: 是否成功验证
        """
        try:
            verify_time = int(datetime.now().timestamp())
            self.cursor.execute(
                """UPDATE user_verification
                   SET verified = 1, verify_time = ?
                   WHERE user_id = ? AND group_id = ? AND verified = 0""",
                (verify_time, user_id, group_id),
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                logger.info(f"[{MODULE_NAME}]用户验证通过: {user_id} 群: {group_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]验证用户失败: {e}")
            return False

    def get_unverified_users(self, timeout_hours: int = 6) -> list:
        """
        获取超时未验证的用户列表

        Args:
            timeout_hours: 超时小时数，默认6小时

        Returns:
            list: 未验证用户列表 [{user_id, group_id, join_time}, ...]
        """
        try:
            current_time = int(datetime.now().timestamp())
            timeout_seconds = timeout_hours * 3600
            cutoff_time = current_time - timeout_seconds

            self.cursor.execute(
                """SELECT user_id, group_id, join_time
                   FROM user_verification
                   WHERE verified = 0 AND notified = 0 AND join_time <= ?""",
                (cutoff_time,),
            )
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取未验证用户失败: {e}")
            return []

    def mark_users_notified(self, user_ids: list, group_id: str) -> bool:
        """
        标记用户已通知（即将被踢）

        Args:
            user_ids: QQ号列表
            group_id: 群号

        Returns:
            bool: 是否成功
        """
        try:
            placeholders = ",".join("?" * len(user_ids))
            self.cursor.execute(
                f"""UPDATE user_verification
                   SET notified = 1
                   WHERE user_id IN ({placeholders}) AND group_id = ?""",
                (*user_ids, group_id),
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]标记用户已通知失败: {e}")
            return False

    def remove_user(self, user_id: str, group_id: str) -> bool:
        """
        删除用户记录（用户离群或被踢后）

        Args:
            user_id: QQ号
            group_id: 群号

        Returns:
            bool: 是否成功
        """
        try:
            self.cursor.execute(
                """DELETE FROM user_verification
                   WHERE user_id = ? AND group_id = ?""",
                (user_id, group_id),
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                logger.info(f"[{MODULE_NAME}]删除用户记录: {user_id} 群: {group_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]删除用户记录失败: {e}")
            return False

    def is_user_verified(self, user_id: str, group_id: str) -> bool:
        """
        检查用户是否已验证

        Args:
            user_id: QQ号
            group_id: 群号

        Returns:
            bool: 是否已验证
        """
        try:
            self.cursor.execute(
                """SELECT verified FROM user_verification
                   WHERE user_id = ? AND group_id = ?""",
                (user_id, group_id),
            )
            row = self.cursor.fetchone()
            if row:
                return row["verified"] == 1
            return True  # 如果没有记录，视为已验证（老用户）
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]检查用户验证状态失败: {e}")
            return True

    def get_user_info(self, user_id: str, group_id: str) -> dict:
        """
        获取用户信息

        Args:
            user_id: QQ号
            group_id: 群号

        Returns:
            dict: 用户信息或None
        """
        try:
            self.cursor.execute(
                """SELECT * FROM user_verification
                   WHERE user_id = ? AND group_id = ?""",
                (user_id, group_id),
            )
            row = self.cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取用户信息失败: {e}")
            return None

    def get_pending_users_by_group(self, group_id: str) -> list:
        """
        获取指定群内所有待验证用户列表

        Args:
            group_id: 群号

        Returns:
            list: 未验证用户列表 [{user_id, join_time}, ...]
        """
        try:
            self.cursor.execute(
                """SELECT user_id, join_time
                   FROM user_verification
                   WHERE group_id = ? AND verified = 0
                   ORDER BY join_time DESC""",
                (group_id,),
            )
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取群待验证用户失败: {e}")
            return []

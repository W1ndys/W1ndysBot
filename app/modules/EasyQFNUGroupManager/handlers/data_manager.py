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
                last_remind_hour INTEGER DEFAULT 0,
                UNIQUE(user_id, group_id)
            )"""
        )
        self.conn.commit()

        # 检查并添加/迁移列（兼容旧数据库）
        self.cursor.execute("PRAGMA table_info(user_verification)")
        columns = [col[1] for col in self.cursor.fetchall()]

        # 如果存在旧的 reminded 列，先迁移数据
        if "reminded" in columns and "last_remind_hour" not in columns:
            self.cursor.execute(
                "ALTER TABLE user_verification ADD COLUMN last_remind_hour INTEGER DEFAULT 0"
            )
            # 将旧的 reminded=1 的记录迁移为 last_remind_hour=1
            self.cursor.execute(
                "UPDATE user_verification SET last_remind_hour = reminded WHERE reminded > 0"
            )
            self.conn.commit()
            logger.info(f"[{MODULE_NAME}]数据库表迁移 reminded 到 last_remind_hour")
        elif "last_remind_hour" not in columns:
            self.cursor.execute(
                "ALTER TABLE user_verification ADD COLUMN last_remind_hour INTEGER DEFAULT 0"
            )
            self.conn.commit()
            logger.info(f"[{MODULE_NAME}]数据库表添加 last_remind_hour 列")

        # 创建黑名单表
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS user_blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                group_id TEXT NOT NULL,
                blacklisted_time INTEGER NOT NULL,
                reason TEXT DEFAULT NULL,
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
        如果用户已有记录且已通过验证，则只更新入群时间，保留验证状态
        如果用户未通过验证或无记录，则创建新的未验证记录

        Args:
            user_id: QQ号
            group_id: 群号
            join_time: 入群时间戳

        Returns:
            bool: 是否成功添加
        """
        try:
            # 先检查用户是否已有记录
            self.cursor.execute(
                """SELECT verified, verify_time FROM user_verification
                   WHERE user_id = ? AND group_id = ?""",
                (user_id, group_id),
            )
            row = self.cursor.fetchone()

            if row and row["verified"] == 1:
                # 用户已通过验证，只更新入群时间，保留验证状态
                self.cursor.execute(
                    """UPDATE user_verification
                       SET join_time = ?
                       WHERE user_id = ? AND group_id = ?""",
                    (join_time, user_id, group_id),
                )
                logger.info(
                    f"[{MODULE_NAME}]更新已验证用户入群时间: {user_id} 群: {group_id}"
                )
            else:
                # 用户未验证或无记录，创建/覆盖为未验证状态
                self.cursor.execute(
                    """INSERT OR REPLACE INTO user_verification
                       (user_id, group_id, join_time, verified, verify_time, notified, last_remind_hour)
                       VALUES (?, ?, ?, 0, NULL, 0, 0)""",
                    (user_id, group_id, join_time),
                )
                logger.info(f"[{MODULE_NAME}]添加用户记录: {user_id} 群: {group_id}")

            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加用户记录失败: {e}")
            return False

    def verify_user(self, user_id: str, group_id: str) -> str:
        """
        验证用户通过

        Args:
            user_id: QQ号
            group_id: 群号

        Returns:
            str: 验证结果状态
                - "success": 验证成功
                - "already_verified": 已验证过
                - "not_found": 记录不存在
                - "error": 操作失败
        """
        try:
            # 先检查用户记录是否存在
            self.cursor.execute(
                """SELECT verified FROM user_verification
                   WHERE user_id = ? AND group_id = ?""",
                (user_id, group_id),
            )
            row = self.cursor.fetchone()

            if row is None:
                logger.info(f"[{MODULE_NAME}]用户记录不存在: {user_id} 群: {group_id}")
                return "not_found"

            if row["verified"] == 1:
                logger.info(f"[{MODULE_NAME}]用户已验证过: {user_id} 群: {group_id}")
                return "already_verified"

            # 执行验证
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
                return "success"
            return "error"
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]验证用户失败: {e}")
            return "error"

    def add_and_verify_user(self, user_id: str, group_id: str) -> str:
        """
        添加用户记录并直接设为已验证状态（用于无记录用户直接通过）

        Args:
            user_id: QQ号
            group_id: 群号

        Returns:
            str: 操作结果状态
                - "success": 添加并验证成功
                - "error": 操作失败
        """
        try:
            current_time = int(datetime.now().timestamp())
            self.cursor.execute(
                """INSERT OR REPLACE INTO user_verification
                   (user_id, group_id, join_time, verified, verify_time, notified, last_remind_hour)
                   VALUES (?, ?, ?, 1, ?, 1, 999)""",
                (user_id, group_id, current_time, current_time),
            )
            self.conn.commit()
            logger.info(f"[{MODULE_NAME}]添加并验证用户: {user_id} 群: {group_id}")
            return "success"
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加并验证用户失败: {e}")
            return "error"

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

    def get_users_to_remind(self, start_hour: float = 0.5, timeout_hours: int = 1) -> list:
        """
        获取需要提醒的用户列表
        当用户入群满半小时间隔且大于上次提醒间隔数时，需要提醒

        Args:
            start_hour: 开始提醒的小时数，默认0.5小时（半小时）
            timeout_hours: 超时踢出的小时数，用于过滤已超时用户

        Returns:
            list: 待提醒用户列表 [{user_id, group_id, join_time, last_remind_hour, current_interval}, ...]
        """
        try:
            current_time = int(datetime.now().timestamp())
            # 计算开始提醒的时间截止点
            start_cutoff_time = current_time - int(start_hour * 3600)
            # 计算超时踢出的时间截止点（不提醒即将被踢的用户）
            timeout_cutoff_time = current_time - timeout_hours * 3600

            self.cursor.execute(
                """SELECT user_id, group_id, join_time, last_remind_hour
                   FROM user_verification
                   WHERE verified = 0 AND notified = 0
                   AND join_time <= ? AND join_time > ?""",
                (start_cutoff_time, timeout_cutoff_time),
            )
            rows = self.cursor.fetchall()

            # 筛选出当前半小时间隔数大于上次提醒间隔数的用户
            users_to_remind = []
            for row in rows:
                row_dict = dict(row)
                # 计算入群已满的半小时间隔数（1=半小时，2=1小时，以此类推）
                elapsed_seconds = current_time - row_dict["join_time"]
                current_interval = elapsed_seconds // 1800  # 1800秒=半小时
                # 如果当前间隔数大于上次提醒的间隔数，需要提醒
                if current_interval > row_dict["last_remind_hour"]:
                    row_dict["current_interval"] = current_interval
                    users_to_remind.append(row_dict)

            return users_to_remind
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取待提醒用户失败: {e}")
            return []

    def update_last_remind_hour(self, user_id: str, group_id: str, hour: int) -> bool:
        """
        更新用户上次提醒的小时数

        Args:
            user_id: QQ号
            group_id: 群号
            hour: 当前入群的整点小时数

        Returns:
            bool: 是否成功
        """
        try:
            self.cursor.execute(
                """UPDATE user_verification
                   SET last_remind_hour = ?
                   WHERE user_id = ? AND group_id = ?""",
                (hour, user_id, group_id),
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]更新用户提醒小时数失败: {e}")
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

    def get_all_recorded_user_ids(self, group_id: str) -> set:
        """
        获取指定群内所有已记录的用户ID集合

        Args:
            group_id: 群号

        Returns:
            set: 已记录的用户ID集合
        """
        try:
            self.cursor.execute(
                """SELECT user_id FROM user_verification WHERE group_id = ?""",
                (group_id,),
            )
            rows = self.cursor.fetchall()
            return {row["user_id"] for row in rows}
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取群已记录用户失败: {e}")
            return set()

    # ============ 黑名单相关操作 ============

    def add_blacklist(self, user_id: str, group_id: str, reason: str = None) -> bool:
        """
        添加黑名单记录

        Args:
            user_id: QQ号
            group_id: 群号
            reason: 拉黑原因

        Returns:
            bool: 是否成功
        """
        try:
            current_time = int(datetime.now().timestamp())
            self.cursor.execute(
                """INSERT OR REPLACE INTO user_blacklist
                   (user_id, group_id, blacklisted_time, reason)
                   VALUES (?, ?, ?, ?)""",
                (user_id, group_id, current_time, reason),
            )
            self.conn.commit()
            logger.info(f"[{MODULE_NAME}]添加黑名单: {user_id} 群: {group_id}")
            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加黑名单失败: {e}")
            return False

    def is_blacklisted(self, user_id: str, group_id: str) -> bool:
        """
        检查用户是否在黑名单中

        Args:
            user_id: QQ号
            group_id: 群号

        Returns:
            bool: 是否在黑名单中
        """
        try:
            self.cursor.execute(
                """SELECT id FROM user_blacklist
                   WHERE user_id = ? AND group_id = ?""",
                (user_id, group_id),
            )
            return self.cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]检查黑名单失败: {e}")
            return False

    def remove_blacklist(self, user_id: str, group_id: str) -> bool:
        """
        移除黑名单记录

        Args:
            user_id: QQ号
            group_id: 群号

        Returns:
            bool: 是否成功
        """
        try:
            self.cursor.execute(
                """DELETE FROM user_blacklist
                   WHERE user_id = ? AND group_id = ?""",
                (user_id, group_id),
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                logger.info(f"[{MODULE_NAME}]移除黑名单: {user_id} 群: {group_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]移除黑名单失败: {e}")
            return False

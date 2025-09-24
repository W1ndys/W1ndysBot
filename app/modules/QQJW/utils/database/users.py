import sqlite3
import os
from datetime import datetime, timezone, timedelta
from ... import MODULE_NAME
from logger import logger
from config import OWNER_ID


class UserDatabase:

    def __init__(self):
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"data.db")
        self.table_name = "users"
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_table()

    def _init_table(self):
        """
        初始化 users 表，如果不存在则创建
        """
        try:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id                               INTEGER PRIMARY KEY AUTOINCREMENT,
                    qq_id                            TEXT    UNIQUE NOT NULL,
                    student_id                       TEXT    UNIQUE,
                    enable_grade_notification        INTEGER NOT NULL DEFAULT 0 CHECK(enable_grade_notification IN (0, 1)),
                    enable_exam_reminder             INTEGER NOT NULL DEFAULT 0 CHECK(enable_exam_reminder IN (0, 1)),
                    enable_daily_schedule_reminder   INTEGER NOT NULL DEFAULT 0 CHECK(enable_daily_schedule_reminder IN (0, 1)),
                    session_cookie                   TEXT,
                    user_role                        INTEGER NOT NULL DEFAULT 0,
                    status                           INTEGER NOT NULL DEFAULT 1 CHECK(status IN (0, 1)),
                    created_at                       TEXT,
                    updated_at                       TEXT,
                    FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE SET NULL ON UPDATE CASCADE
                );
                """
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]初始化users表失败: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def _get_beijing_time(self):
        """获取北京时间（东八区）"""
        beijing_tz = timezone(timedelta(hours=8))
        return datetime.now(beijing_tz).strftime("%Y-%m-%d %H:%M:%S")

    def bind_user_account(self, qq_id, student_id, session_cookie):
        """
        绑定用户账号，如果已存在则刷新 session_cookie
        """
        try:
            beijing_time = self._get_beijing_time()

            # 检查该学号是否已被其他QQ号绑定
            self.cursor.execute(
                f"SELECT qq_id FROM {self.table_name} WHERE student_id = ? AND qq_id != ?",
                (student_id, qq_id),
            )
            existing_user = self.cursor.fetchone()
            if existing_user:
                return {
                    "success": False,
                    "message": f"绑定失败，该学号已被其他用户绑定，如果是被恶意绑定，请使用能证明学生身份的材料联系开发者处理(QQ号：{OWNER_ID})",
                    "code": 409,
                    "data": None,
                }

            # 检查该QQ号当前的绑定情况
            self.cursor.execute(
                f"SELECT student_id FROM {self.table_name} WHERE qq_id = ?",
                (qq_id,),
            )
            current_binding = self.cursor.fetchone()

            if current_binding:
                current_student_id = current_binding[0]
                # 如果当前绑定的学号为None，视为未绑定
                if current_student_id is None:
                    # 更新记录，绑定新学号
                    self.cursor.execute(
                        f"UPDATE {self.table_name} SET student_id = ?, session_cookie = ?, updated_at = ? WHERE qq_id = ?",
                        (student_id, session_cookie, beijing_time, qq_id),
                    )
                    self.conn.commit()
                    return {
                        "success": True,
                        "message": "用户账号绑定成功",
                        "code": 200,
                        "data": {
                            "qq_id": qq_id,
                            "student_id": student_id,
                            "action": "updated",
                        },
                    }
                elif current_student_id == student_id:
                    # 相同绑定，更新 session_cookie
                    self.cursor.execute(
                        f"UPDATE {self.table_name} SET session_cookie = ?, updated_at = ? WHERE qq_id = ?",
                        (session_cookie, beijing_time, qq_id),
                    )
                    self.conn.commit()
                    return {
                        "success": True,
                        "message": "用户账号信息更新成功",
                        "code": 200,
                        "data": {
                            "qq_id": qq_id,
                            "student_id": student_id,
                            "action": "updated",
                        },
                    }
                else:
                    # QQ号已绑定其他学号，不允许重新绑定
                    return {
                        "success": False,
                        "message": f"绑定失败，该QQ号已绑定其他学号({current_student_id})，一个QQ号只能绑定一个学号",
                        "code": 409,
                        "data": None,
                    }
            else:
                # QQ号未绑定任何学号，插入新记录
                self.cursor.execute(
                    f"INSERT INTO {self.table_name} (qq_id, student_id, session_cookie, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (qq_id, student_id, session_cookie, beijing_time, beijing_time),
                )
                self.conn.commit()
                return {
                    "success": True,
                    "message": "用户账号绑定成功",
                    "code": 201,
                    "data": {
                        "qq_id": qq_id,
                        "student_id": student_id,
                        "action": "created",
                    },
                }
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]绑定用户账号失败: {e}")
            return {
                "success": False,
                "message": f"绑定用户账号失败: {str(e)}",
                "code": 500,
                "data": None,
            }

    def get_user_session_cookie_and_student_id(self, qq_id):
        """获取用户session_cookie"""
        try:
            self.cursor.execute(
                f"SELECT session_cookie, student_id FROM {self.table_name} WHERE qq_id = ?",
                (qq_id,),
            )
            result = self.cursor.fetchone()
            if result:
                return {
                    "success": True,
                    "message": "获取用户session_cookie成功",
                    "code": 200,
                    "data": {
                        "qq_id": qq_id,
                        "session_cookie": result[0],
                        "student_id": result[1],
                    },
                }
            else:
                return {
                    "success": False,
                    "message": "用户不存在或未绑定账号",
                    "code": 404,
                    "data": None,
                }
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取用户session_cookie失败: {e}")
            return {
                "success": False,
                "message": f"获取用户session_cookie失败: {str(e)}",
                "code": 500,
                "data": None,
            }

    def clear_user_session_cookie(self, qq_id):
        """清空用户session_cookie，保留其他绑定信息"""
        try:
            # 检查用户是否存在
            self.cursor.execute(
                f"SELECT qq_id, student_id FROM {self.table_name} WHERE qq_id = ?",
                (qq_id,),
            )
            result = self.cursor.fetchone()
            if not result:
                return {
                    "success": False,
                    "message": "用户不存在或未绑定账号",
                    "code": 404,
                    "data": None,
                }

            # 清空session_cookie，更新时间
            beijing_time = self._get_beijing_time()
            self.cursor.execute(
                f"UPDATE {self.table_name} SET session_cookie = NULL, updated_at = ? WHERE qq_id = ?",
                (beijing_time, qq_id),
            )
            self.conn.commit()

            return {
                "success": True,
                "message": "退出登录成功，登录凭证已清空",
                "code": 200,
                "data": {
                    "qq_id": qq_id,
                    "student_id": result[1],
                    "action": "logout",
                },
            }
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]清空用户session_cookie失败: {e}")
            return {
                "success": False,
                "message": f"退出登录失败: {str(e)}",
                "code": 500,
                "data": None,
            }

import sqlite3
import os
from datetime import datetime, timezone, timedelta
from ... import MODULE_NAME
from logger import logger


class AdminAcountDatabase:
    """
    CREATE TABLE IF NOT EXISTS admin_acount (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        account      TEXT    UNIQUE NOT NULL,  -- 账号
        password     TEXT    NOT NULL,         -- 密码
        cookie       TEXT    NOT NULL          -- cookie
    );
    """

    def __init__(self):
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"data.db")
        self.table_name = "admin_acount"
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_table()

    def _init_table(self):
        """
        初始化 admin_acount 表，如果不存在则创建
        表结构：
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        account      TEXT    UNIQUE NOT NULL,  -- 账号
        password     TEXT    NOT NULL,         -- 密码
        cookie       TEXT    NOT NULL          -- cookie
        """
        try:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS admin_acount (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    account      TEXT    UNIQUE NOT NULL,
                    password     TEXT    NOT NULL,
                    cookie       TEXT    NOT NULL
                );
                """
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]初始化admin_acount表失败: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def store_account_password(self, account, password):
        """
        存储账号密码（只保存一组，如果已存在则更新）

        Args:
            account (str): 账号
            password (str): 密码

        Returns:
            dict: {
                "code": int,        # 状态码 200成功，500失败
                "message": str,     # 返回信息
                "data": dict        # 返回数据
            }
        """
        try:
            # 检查是否已有记录
            self.cursor.execute("SELECT COUNT(*) FROM admin_acount")
            count = self.cursor.fetchone()[0]

            operation = "update" if count > 0 else "insert"

            if count > 0:
                # 如果已有记录，更新第一条记录
                self.cursor.execute(
                    "UPDATE admin_acount SET account = ?, password = ? WHERE id = (SELECT MIN(id) FROM admin_acount)",
                    (account, password),
                )
            else:
                # 如果没有记录，插入新记录（cookie先设为空字符串）
                self.cursor.execute(
                    "INSERT INTO admin_acount (account, password, cookie) VALUES (?, ?, ?)",
                    (account, password, ""),
                )

            self.conn.commit()
            logger.info(f"[{MODULE_NAME}]成功存储账号密码")

            return {
                "code": 200,
                "message": "账号密码存储成功",
                "data": {"account": account, "operation": operation},
            }

        except Exception as e:
            error_msg = f"存储账号密码失败: {str(e)}"
            logger.error(f"[{MODULE_NAME}]{error_msg}")
            return {"code": 500, "message": error_msg, "data": None}

    def get_admin_cookie(self):
        """
        获取cookie

        Returns:
            dict: {
                "code": int,        # 状态码 200成功，404未找到，500失败
                "message": str,     # 返回信息
                "data": dict        # 返回数据
            }
        """
        try:
            self.cursor.execute("SELECT cookie FROM admin_acount ORDER BY id LIMIT 1")
            result = self.cursor.fetchone()

            if result:
                cookie = result[0]
                if cookie:
                    logger.info(f"[{MODULE_NAME}]成功获取cookie")
                    return {
                        "code": 200,
                        "message": "成功获取cookie",
                        "data": {"cookie": cookie},
                    }
                else:
                    logger.warning(f"[{MODULE_NAME}]cookie为空")
                    return {"code": 404, "message": "cookie为空", "data": None}
            else:
                logger.warning(f"[{MODULE_NAME}]未找到管理员账号记录")
                return {"code": 404, "message": "未找到管理员账号记录", "data": None}

        except Exception as e:
            error_msg = f"获取cookie失败: {str(e)}"
            logger.error(f"[{MODULE_NAME}]{error_msg}")
            return {"code": 500, "message": error_msg, "data": None}

    def store_admin_cookie(self, cookie):
        """
        存储cookie（更新已存在的记录）

        Args:
            cookie (str): cookie字符串

        Returns:
            dict: {
                "code": int,        # 状态码 200成功，404未找到账号，500失败
                "message": str,     # 返回信息
                "data": dict        # 返回数据
            }
        """
        try:
            # 检查是否已有记录
            self.cursor.execute("SELECT COUNT(*) FROM admin_acount")
            count = self.cursor.fetchone()[0]

            if count > 0:
                # 更新第一条记录的cookie
                self.cursor.execute(
                    "UPDATE admin_acount SET cookie = ? WHERE id = (SELECT MIN(id) FROM admin_acount)",
                    (cookie,),
                )
                self.conn.commit()
                logger.info(f"[{MODULE_NAME}]成功存储cookie")

                return {
                    "code": 200,
                    "message": "cookie存储成功",
                    "data": {"cookie_length": len(cookie) if cookie else 0},
                }
            else:
                logger.warning(f"[{MODULE_NAME}]未找到管理员账号记录，无法存储cookie")
                return {
                    "code": 404,
                    "message": "未找到管理员账号记录，无法存储cookie",
                    "data": None,
                }

        except Exception as e:
            error_msg = f"存储cookie失败: {str(e)}"
            logger.error(f"[{MODULE_NAME}]{error_msg}")
            return {"code": 500, "message": error_msg, "data": None}

    def get_admin_account_password(self):
        """
        获取账号密码

        Returns:
            dict: {
                "code": int,        # 状态码 200成功，404未找到，500失败
                "message": str,     # 返回信息
                "data": dict        # 返回数据
            }
        """
        try:
            self.cursor.execute(
                "SELECT account, password FROM admin_acount ORDER BY id LIMIT 1"
            )
            result = self.cursor.fetchone()

            if result:
                account, password = result
                logger.info(f"[{MODULE_NAME}]成功获取高级登录账号密码")
                return {
                    "code": 200,
                    "message": "成功获取高级登录账号密码",
                    "data": {"account": account, "password": password},
                }
            else:
                logger.warning(f"[{MODULE_NAME}]未找到高级登录账号记录")
                return {"code": 404, "message": "未找到高级登录账号记录", "data": None}

        except Exception as e:
            error_msg = f"获取高级登录账号密码失败: {str(e)}"
            logger.error(f"[{MODULE_NAME}]{error_msg}")
            return {"code": 500, "message": error_msg, "data": None}

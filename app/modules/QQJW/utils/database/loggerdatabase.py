import os
import sqlite3
from datetime import datetime, timezone, timedelta
from ... import MODULE_NAME
from logger import logger


class LoggerDatabase:
    def __init__(self):
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"data.db")
        self.table_name = "logger"
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_table()

    def _init_table(self):
        """
        初始化 logger 表，如果不存在则创建，该表用于记录用户操作日志
        """
        try:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS logger (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    qq_id        TEXT,
                    operation    TEXT,
                    created_at   TEXT
                );
                """
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]初始化logger表失败: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def _get_beijing_time(self):
        """获取北京时间（东八区）"""
        beijing_tz = timezone(timedelta(hours=8))
        return datetime.now(beijing_tz).strftime("%Y-%m-%d %H:%M:%S")

    def add_logger(self, qq_id, operation):
        """
        添加日志
        """
        try:
            beijing_time = self._get_beijing_time()
            self.cursor.execute(
                f"INSERT INTO {self.table_name} (qq_id, operation, created_at) VALUES (?, ?, ?)",
                (qq_id, operation, beijing_time),
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加日志失败: {e}")

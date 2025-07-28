import sqlite3
import os
from datetime import datetime
from ... import MODULE_NAME


class DatabaseBase:
    """数据库基础类，提供通用的数据库连接和操作方法"""

    def __init__(self, year=None):
        """初始化数据库连接"""
        self.data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(self.data_dir, exist_ok=True)

        # 按年份命名数据库文件：sar_年份.db
        # 如果未指定年份，使用当前年份
        self.year = year if year is not None else datetime.now().year
        db_filename = f"sar_{self.year}.db"
        self.db_path = os.path.join(self.data_dir, db_filename)

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def create_table(self, table_name, table_schema):
        """创建表的通用方法"""
        try:
            self.cursor.execute(table_schema)
            self.conn.commit()
            return {"code": 200, "message": f"表 {table_name} 创建成功"}
        except Exception as e:
            return {"code": 500, "message": f"创建表 {table_name} 失败: {str(e)}"}

    def execute_query(self, query, params=None):
        """执行查询的通用方法"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"查询执行失败: {str(e)}")

    def execute_update(self, query, params=None):
        """执行更新的通用方法"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            raise Exception(f"更新执行失败: {str(e)}")

    def get_current_time(self):
        """获取当前时间戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_current_date(self):
        """获取当前日期"""
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def get_type_name(user_type):
        """获取类型名称"""
        return "阳光" if user_type == 0 else "雨露"

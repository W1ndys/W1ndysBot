import sqlite3


class DataManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """建表函数，如果表不存在则创建"""
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS""")

    # 其他函数

import sqlite3
import os
from . import MODULE_NAME


class DataManager:
    def __init__(self, group_id):
        data_dir = os.path.join("data", MODULE_NAME, group_id)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"words.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """建表函数，如果表不存在则创建"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS data_table (
                word TEXT PRIMARY KEY,
                weight INTEGER NOT NULL
            )
            """
        )
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def add_word(self, word, weight):
        """添加敏感词及权值，若已存在则更新权值"""
        self.cursor.execute(
            "INSERT INTO data_table (word, weight) VALUES (?, ?) ON CONFLICT(word) DO UPDATE SET weight=excluded.weight",
            (word, weight),
        )
        self.conn.commit()

    def get_words(self):
        """获取所有敏感词及权值"""
        self.cursor.execute("SELECT word, weight FROM data_table")
        return self.cursor.fetchall()

    def update_word(self, word, new_weight):
        """更新敏感词的权值"""
        self.cursor.execute(
            "UPDATE data_table SET weight=? WHERE word=?", (new_weight, word)
        )
        self.conn.commit()

    def delete_word(self, word):
        """删除敏感词"""
        self.cursor.execute("DELETE FROM data_table WHERE word=?", (word,))
        self.conn.commit()

    def calc_message_weight(self, message):
        """计算消息的违禁程度（所有命中违禁词的权值求和）"""
        self.cursor.execute("SELECT word, weight FROM data_table")
        return sum(weight for word, weight in self.cursor.fetchall() if word in message)


if __name__ == "__main__":
    with DataManager("1234567890") as dm:
        print("添加敏感词 'test'，权值 10")
        dm.add_word("test", 10)
        print("当前敏感词列表：", dm.get_words())
        print("将敏感词 'test' 的权值更新为 20")
        dm.update_word("test", 20)
        print("更新后敏感词列表：", dm.get_words())
        print("删除敏感词 'test'")
        dm.delete_word("test")
        print("删除后敏感词列表：", dm.get_words())
        print("计算消息 'test' 的违禁程度：", dm.calc_message_weight("test"))

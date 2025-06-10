import sqlite3
import os
from . import MODULE_NAME


class DataManager:
    def __init__(self, group_id):
        self.data_dir = os.path.join("data", MODULE_NAME, group_id)
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, "data.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """建表函数，如果表不存在则创建，并兼容旧表结构升级"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ban_words (
                word TEXT PRIMARY KEY,
                weight INTEGER NOT NULL
            )
            """
        )
        # 检查并升级旧表结构，添加update_time字段
        self.cursor.execute("PRAGMA table_info(ban_words)")
        columns = [row[1] for row in self.cursor.fetchall()]
        if "update_time" not in columns:
            self.cursor.execute(
                "ALTER TABLE ban_words ADD COLUMN update_time TIMESTAMP"
            )
        # 新增用户状态表
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_status (
                user_id TEXT PRIMARY KEY,
                status TEXT NOT NULL
            )
            """
        )
        # 检查并升级旧user_status表结构，添加update_time字段
        self.cursor.execute("PRAGMA table_info(user_status)")
        columns = [row[1] for row in self.cursor.fetchall()]
        if "update_time" not in columns:
            self.cursor.execute(
                "ALTER TABLE user_status ADD COLUMN update_time TIMESTAMP"
            )
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def add_word(self, word, weight=10):
        """添加敏感词及权值，若已存在则更新权值和时间"""
        self.cursor.execute(
            "INSERT INTO ban_words (word, weight, update_time) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(word) DO UPDATE SET weight=excluded.weight, update_time=CURRENT_TIMESTAMP",
            (word, weight),
        )
        self.conn.commit()
        return True

    def get_words(self):
        """获取所有敏感词及权值"""
        self.cursor.execute("SELECT word, weight FROM ban_words")
        return self.cursor.fetchall()

    def update_word(self, word, new_weight):
        """更新敏感词的权值"""
        self.cursor.execute(
            "UPDATE ban_words SET weight=? WHERE word=?", (new_weight, word)
        )
        self.conn.commit()
        return True

    def delete_word(self, word):
        """删除敏感词"""
        self.cursor.execute("DELETE FROM ban_words WHERE word=?", (word,))
        self.conn.commit()
        return True

    def calc_message_weight(self, message):
        """计算消息的违禁程度（所有命中违禁词的权值求和）"""
        self.cursor.execute("SELECT word, weight FROM ban_words")
        return sum(weight for word, weight in self.cursor.fetchall() if word in message)

    # 用户状态相关操作
    def set_user_status(self, user_id, status):
        """设置某用户状态，若已存在则更新"""
        self.cursor.execute(
            "INSERT INTO user_status (user_id, status, update_time) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(user_id) DO UPDATE SET status=excluded.status, update_time=CURRENT_TIMESTAMP",
            (user_id, status),
        )
        self.conn.commit()
        return True

    def get_user_status(self, user_id):
        """获取某用户状态"""
        self.cursor.execute(
            "SELECT status FROM user_status WHERE user_id=?", (user_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def delete_user_status(self, user_id):
        """删除某用户状态"""
        self.cursor.execute("DELETE FROM user_status WHERE user_id=?", (user_id,))
        self.conn.commit()
        return True

    def get_all_user_status(self):
        """获取所有用户状态"""
        self.cursor.execute("SELECT user_id, status, update_time FROM user_status")
        return self.cursor.fetchall()


if __name__ == "__main__":
    group_id = "1046961227"
    with DataManager(group_id) as dm:
        while True:
            case = input(
                "请输入操作: \n1. 添加敏感词\n2. 获取所有敏感词\n3. 更新敏感词权值\n4. 删除敏感词\n5. 检验文本总权值\n6. 退出\n"
            )
            if case == "1":
                word = input("请输入敏感词: ")
                weight = input("请输入权值: ")
                dm.add_word(word, int(weight))
            elif case == "2":
                words = dm.get_words()
                for word, weight in words:
                    print(f"{word}: {weight}")
            elif case == "3":
                word = input("请输入敏感词: ")
                weight = input("请输入权值: ")
                dm.update_word(word, int(weight))
            elif case == "4":
                word = input("请输入敏感词: ")
                dm.delete_word(word)
            elif case == "5":
                text = input("请输入要检验的文本: ")
                total_weight = dm.calc_message_weight(text)
                print(f"文本总权值为: {total_weight}")
            elif case == "6":
                break

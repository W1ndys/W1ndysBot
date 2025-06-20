import sqlite3
import os
import random
from datetime import datetime
from . import MODULE_NAME


class DataManager:
    def __init__(self, group_id):
        """
        初始化数据管理器
        :param group_id: 群号
        """
        self.group_id = group_id
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"data.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """建表函数，如果表不存在则创建"""
        table_name = f"`{self.group_id}_data`"
        # 添加shuffle_index字段用于洗牌算法
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            random_count INTEGER DEFAULT 0,
            added_by TEXT NOT NULL,
            add_time TEXT NOT NULL,
            shuffle_index INTEGER DEFAULT 0
        )"""
        )

        # 创建洗牌状态表，记录当前洗牌轮次和位置
        shuffle_table = f"`{self.group_id}_shuffle_state`"
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {shuffle_table} (
            id INTEGER PRIMARY KEY,
            current_round INTEGER DEFAULT 0,
            current_position INTEGER DEFAULT 0,
            total_count INTEGER DEFAULT 0
        )"""
        )

        # 确保洗牌状态表有初始记录
        self.cursor.execute(f"SELECT COUNT(*) FROM {shuffle_table}")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(
                f"INSERT INTO {shuffle_table} (id, current_round, current_position, total_count) VALUES (1, 0, 0, 0)"
            )

        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def add_data(self, message, added_by):
        """
        添加一条数据
        :param message: 消息内容
        :param added_by: 添加者（用户ID）
        :return: 新插入数据的ID
        """
        table_name = f"`{self.group_id}_data`"
        add_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            f"""INSERT INTO {table_name} (message, random_count, added_by, add_time, shuffle_index) 
                              VALUES (?, 0, ?, ?, 0)""",
            (message, added_by, add_time),
        )
        new_id = self.cursor.lastrowid
        self.conn.commit()

        # 重新初始化洗牌
        self._reset_shuffle()
        return new_id

    def _reset_shuffle(self):
        """重置洗牌状态，当有新数据添加或删除时调用"""
        table_name = f"`{self.group_id}_data`"
        shuffle_table = f"`{self.group_id}_shuffle_state`"

        # 获取当前数据总数
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = self.cursor.fetchone()[0]

        if total_count == 0:
            return

        # 获取所有数据ID
        self.cursor.execute(f"SELECT id FROM {table_name} ORDER BY id")
        all_ids = [row[0] for row in self.cursor.fetchall()]

        # Fisher-Yates洗牌算法
        random.shuffle(all_ids)

        # 更新shuffle_index
        for index, data_id in enumerate(all_ids):
            self.cursor.execute(
                f"UPDATE {table_name} SET shuffle_index = ? WHERE id = ?",
                (index, data_id),
            )

        # 重置洗牌状态
        self.cursor.execute(
            f"UPDATE {shuffle_table} SET current_round = current_round + 1, current_position = 0, total_count = ?",
            (total_count,),
        )

        self.conn.commit()

    def get_random_data(self):
        """
        获取该群随机一条数据，使用洗牌算法确保平均分布
        :return: 随机数据的完整信息 (id, message, random_count, added_by, add_time)
        """
        table_name = f"`{self.group_id}_data`"
        shuffle_table = f"`{self.group_id}_shuffle_state`"

        # 获取当前洗牌状态
        self.cursor.execute(
            f"SELECT current_round, current_position, total_count FROM {shuffle_table} WHERE id = 1"
        )
        shuffle_state = self.cursor.fetchone()

        if not shuffle_state:
            return None

        current_round, current_position, total_count = shuffle_state

        # 检查是否有数据
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        actual_count = self.cursor.fetchone()[0]

        if actual_count == 0:
            return None

        # 如果数据数量发生变化或者是第一次，重新洗牌
        if actual_count != total_count or total_count == 0:
            self._reset_shuffle()
            current_position = 0

        # 如果当前轮次已经结束，开始新一轮洗牌
        if current_position >= actual_count:
            self._reset_shuffle()
            current_position = 0

        # 根据shuffle_index获取当前位置的数据
        self.cursor.execute(
            f"SELECT id, message, random_count, added_by, add_time FROM {table_name} WHERE shuffle_index = ?",
            (current_position,),
        )
        selected_data = self.cursor.fetchone()

        if not selected_data:
            # 如果找不到对应位置的数据，重新洗牌
            self._reset_shuffle()
            self.cursor.execute(
                f"SELECT id, message, random_count, added_by, add_time FROM {table_name} WHERE shuffle_index = 0"
            )
            selected_data = self.cursor.fetchone()
            current_position = 0

        if selected_data:
            data_id = selected_data[0]

            # 更新该条数据的random_count
            self.cursor.execute(
                f"UPDATE {table_name} SET random_count = random_count + 1 WHERE id = ?",
                (data_id,),
            )

            # 更新洗牌位置
            self.cursor.execute(
                f"UPDATE {shuffle_table} SET current_position = ? WHERE id = 1",
                (current_position + 1,),
            )

            self.conn.commit()

            # 返回更新后的数据
            self.cursor.execute(
                f"SELECT id, message, random_count, added_by, add_time FROM {table_name} WHERE id = ?",
                (data_id,),
            )
            return self.cursor.fetchone()

        return None

    def delete_data_by_id(self, data_id):
        """
        根据id删除一条数据
        :param data_id: 数据ID
        :return: 是否删除成功
        """
        table_name = f"`{self.group_id}_data`"
        self.cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (data_id,))
        deleted = self.cursor.rowcount > 0

        if deleted:
            # 重新初始化洗牌
            self._reset_shuffle()

        return deleted

    def get_all_data(self):
        """
        获取该群所有数据（用于管理）
        :return: 所有数据列表
        """
        table_name = f"`{self.group_id}_data`"
        self.cursor.execute(
            f"SELECT id, message, random_count, added_by, add_time FROM {table_name} ORDER BY id"
        )
        return self.cursor.fetchall()

    def get_data_count(self):
        """
        获取该群数据总数
        :return: 数据总数
        """
        table_name = f"`{self.group_id}_data`"
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return self.cursor.fetchone()[0]

    def get_shuffle_status(self):
        """
        获取当前洗牌状态（用于调试）
        :return: (当前轮次, 当前位置, 总数据量)
        """
        shuffle_table = f"`{self.group_id}_shuffle_state`"
        self.cursor.execute(
            f"SELECT current_round, current_position, total_count FROM {shuffle_table} WHERE id = 1"
        )
        return self.cursor.fetchone()

    def data_exists(self, data_id):
        """
        检查数据是否存在
        :param data_id: 数据ID
        :return: 是否存在
        """
        table_name = f"`{self.group_id}_data`"
        self.cursor.execute(
            f"SELECT COUNT(*) FROM {table_name} WHERE id = ?", (data_id,)
        )
        return self.cursor.fetchone()[0] > 0

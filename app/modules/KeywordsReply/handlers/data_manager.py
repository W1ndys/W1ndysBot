import sqlite3
import os
from logger import logger
from .. import MODULE_NAME


class DataManager:
    def __init__(self):
        """
        初始化数据管理器，创建数据库连接和游标，并确保数据表存在。
        """
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"data.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """
        建表函数，如果表不存在则创建
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keywords_reply (
                group_id TEXT,
                keyword TEXT,
                reply TEXT NOT NULL,
                adder_qq TEXT,
                add_time TEXT,
                PRIMARY KEY (group_id, keyword)
            )
            """
        )
        self.conn.commit()

    def __enter__(self):
        """
        进入上下文管理器时返回自身
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文管理器时关闭数据库连接
        """
        self.conn.close()

    def add_keyword(self, group_id, keyword, reply, adder_qq, add_time):
        """
        添加或更新关键词及回复内容，若关键词已存在则覆盖。

        参数说明:
            group_id (str): 群号
            keyword (str): 关键词
            reply (str): 回复内容
            adder_qq (str): 添加者QQ号
            add_time (str): 添加时间
        """
        self.cursor.execute(
            "REPLACE INTO keywords_reply (group_id, keyword, reply, adder_qq, add_time) VALUES (?, ?, ?, ?, ?)",
            (group_id, keyword, reply, adder_qq, add_time),
        )
        self.conn.commit()
        logger.info(
            f"[{MODULE_NAME}] 添加关键词「{keyword}」成功！\n"
            f"添加者：{adder_qq}\n"
            f"添加时间：{add_time}\n"
            f"💬 回复内容：{reply}"
        )

    def delete_keyword(self, group_id, keyword):
        """
        根据群号和关键词删除对应记录

        参数说明:
            group_id (str): 群号
            keyword (str): 关键词
        """
        self.cursor.execute(
            "DELETE FROM keywords_reply WHERE group_id = ? AND keyword = ?",
            (group_id, keyword),
        )
        self.conn.commit()
        logger.info(
            f"[{MODULE_NAME}] 删除关键词「{keyword}」成功！（群号：{group_id}）"
        )

    def get_reply(self, group_id, keyword):
        """
        根据群号和关键词返回回复内容，找不到返回None

        参数说明:
            group_id (str): 群号
            keyword (str): 关键词

        返回:
            str or None: 对应的回复内容，若无则为None
        """
        self.cursor.execute(
            "SELECT reply FROM keywords_reply WHERE group_id = ? AND keyword = ?",
            (group_id, keyword),
        )
        result = self.cursor.fetchone()
        if result:
            logger.info(
                f"[{MODULE_NAME}] 查询关键词「{keyword}」成功，返回回复内容。（群号：{group_id}）"
            )
        return result[0] if result else None

    def clear_keywords(self, group_id):
        """
        清空指定群的所有关键词

        参数说明:
            group_id (str): 群号
        """
        self.cursor.execute(
            "DELETE FROM keywords_reply WHERE group_id = ?", (group_id,)
        )
        self.conn.commit()
        logger.info(f"[{MODULE_NAME}] 已清空群号为「{group_id}」的所有关键词。")

    def get_all_keywords(self, group_id):
        """
        查看指定群的所有关键词，返回关键词列表

        参数说明:
            group_id (str): 群号

        返回:
            list[str]: 该群所有关键词的列表
        """
        self.cursor.execute(
            "SELECT keyword FROM keywords_reply WHERE group_id = ?", (group_id,)
        )
        keywords = [row[0] for row in self.cursor.fetchall()]
        logger.info(
            f"[{MODULE_NAME}] 查询群号为「{group_id}」的所有关键词，共{len(keywords)}个。"
        )
        return keywords

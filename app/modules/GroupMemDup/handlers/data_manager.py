import sqlite3
import os
from .. import MODULE_NAME


class DataManager:
    def __init__(self):
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"data.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """建表函数，如果表不存在则创建"""
        # 创建群组表，存储组名和群号的关系
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS group_associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                group_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(group_name, group_id)
            )
        """
        )

        # 创建索引以提高查询性能
        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_group_name ON group_associations(group_name)
        """
        )
        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_group_id ON group_associations(group_id)
        """
        )

        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def create_group_association(self, group_name, group_ids):
        """
        创建群组关联，将若干群号绑定为一组

        Args:
            group_name (str): 组名
            group_ids (list): 群号列表

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # 检查组名是否已存在
            if self.group_name_exists(group_name):
                return False, f"组名 '{group_name}' 已存在"

            # 添加所有群号到指定组（群号可以在多个组中）
            added_count = 0
            for group_id in group_ids:
                try:
                    self.cursor.execute(
                        "INSERT INTO group_associations (group_name, group_id) VALUES (?, ?)",
                        (group_name, str(group_id)),
                    )
                    added_count += 1
                except sqlite3.IntegrityError:
                    # 该群号已经在该组中，跳过
                    continue

            self.conn.commit()
            return True, f"成功创建组 '{group_name}'，添加了 {added_count} 个群"

        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"数据库错误：{str(e)}"

    def add_groups_to_association(self, group_name, group_ids):
        """
        向指定组添加群号

        Args:
            group_name (str): 组名
            group_ids (list): 要添加的群号列表

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # 检查组名是否存在
            if not self.group_name_exists(group_name):
                return False, f"组名 '{group_name}' 不存在"

            # 添加群号到指定组
            added_count = 0
            already_exists = 0

            for group_id in group_ids:
                try:
                    self.cursor.execute(
                        "INSERT INTO group_associations (group_name, group_id) VALUES (?, ?)",
                        (group_name, str(group_id)),
                    )
                    added_count += 1
                except sqlite3.IntegrityError:
                    # 该群号已经在该组中
                    already_exists += 1
                    continue

            self.conn.commit()

            message = f"成功向组 '{group_name}' 添加 {added_count} 个群"
            if already_exists > 0:
                message += f"，{already_exists} 个群号已存在于该组中"

            return True, message

        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"数据库错误：{str(e)}"

    def remove_groups_from_association(self, group_name, group_ids):
        """
        从指定组删除群号

        Args:
            group_name (str): 组名
            group_ids (list): 要删除的群号列表

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # 检查组名是否存在
            if not self.group_name_exists(group_name):
                return False, f"组名 '{group_name}' 不存在"

            # 删除群号
            removed_count = 0
            not_in_group = 0

            for group_id in group_ids:
                self.cursor.execute(
                    "DELETE FROM group_associations WHERE group_name = ? AND group_id = ?",
                    (group_name, str(group_id)),
                )
                if self.cursor.rowcount > 0:
                    removed_count += 1
                else:
                    not_in_group += 1

            self.conn.commit()

            message = f"成功从组 '{group_name}' 删除 {removed_count} 个群"
            if not_in_group > 0:
                message += f"，{not_in_group} 个群号不在该组中"

            return True, message

        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"数据库错误：{str(e)}"

    def delete_group_association(self, group_name):
        """
        删除整个组及其所有数据

        Args:
            group_name (str): 组名

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # 检查组名是否存在
            if not self.group_name_exists(group_name):
                return False, f"组名 '{group_name}' 不存在"

            # 获取该组的群数量
            self.cursor.execute(
                "SELECT COUNT(*) FROM group_associations WHERE group_name = ?",
                (group_name,),
            )
            count = self.cursor.fetchone()[0]

            # 删除该组的所有记录
            self.cursor.execute(
                "DELETE FROM group_associations WHERE group_name = ?", (group_name,)
            )

            self.conn.commit()
            return True, f"成功删除组 '{group_name}' 及其 {count} 个群"

        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"数据库错误：{str(e)}"

    def get_associated_groups(self, group_id):
        """
        根据群号获取同组的其他群号（来自所有包含该群号的组）

        Args:
            group_id (str/int): 群号

        Returns:
            dict: {组名: [同组的其他群号列表]}
        """
        try:
            # 先找到该群号所在的所有组
            group_names = self.get_group_names_by_group_id(group_id)
            if not group_names:
                return {}

            result = {}
            for group_name in group_names:
                # 获取该组的其他群号
                self.cursor.execute(
                    "SELECT group_id FROM group_associations WHERE group_name = ? AND group_id != ?",
                    (group_name, str(group_id)),
                )
                other_groups = [row[0] for row in self.cursor.fetchall()]
                result[group_name] = other_groups

            return result

        except sqlite3.Error:
            return {}

    def get_all_associated_groups(self, group_id):
        """
        根据群号获取所有同组的其他群号（合并所有组的结果）

        Args:
            group_id (str/int): 群号

        Returns:
            list: 所有同组的其他群号列表（去重）
        """
        try:
            # 先找到该群号所在的所有组
            group_names = self.get_group_names_by_group_id(group_id)
            if not group_names:
                return []

            all_groups = set()
            for group_name in group_names:
                # 获取该组的其他群号
                self.cursor.execute(
                    "SELECT group_id FROM group_associations WHERE group_name = ? AND group_id != ?",
                    (group_name, str(group_id)),
                )
                other_groups = [row[0] for row in self.cursor.fetchall()]
                all_groups.update(other_groups)

            return list(all_groups)

        except sqlite3.Error:
            return []

    def get_group_names_by_group_id(self, group_id):
        """
        根据群号获取所属的组名列表

        Args:
            group_id (str/int): 群号

        Returns:
            list: 组名列表
        """
        try:
            self.cursor.execute(
                "SELECT group_name FROM group_associations WHERE group_id = ?",
                (str(group_id),),
            )
            results = self.cursor.fetchall()
            return [row[0] for row in results]

        except sqlite3.Error:
            return []

    def group_name_exists(self, group_name):
        """
        检查组名是否存在

        Args:
            group_name (str): 组名

        Returns:
            bool: 是否存在
        """
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM group_associations WHERE group_name = ?",
                (group_name,),
            )
            return self.cursor.fetchone()[0] > 0

        except sqlite3.Error:
            return False

    def is_group_in_association(self, group_name, group_id):
        """
        检查群号是否在指定组中

        Args:
            group_name (str): 组名
            group_id (str/int): 群号

        Returns:
            bool: 是否在组中
        """
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM group_associations WHERE group_name = ? AND group_id = ?",
                (group_name, str(group_id)),
            )
            return self.cursor.fetchone()[0] > 0

        except sqlite3.Error:
            return False

    def get_all_groups(self):
        """
        获取所有组的信息

        Returns:
            dict: {组名: [群号列表]}
        """
        try:
            self.cursor.execute(
                "SELECT group_name, group_id FROM group_associations ORDER BY group_name, group_id"
            )
            results = self.cursor.fetchall()

            groups = {}
            for group_name, group_id in results:
                if group_name not in groups:
                    groups[group_name] = []
                groups[group_name].append(group_id)

            return groups

        except sqlite3.Error:
            return {}

    def get_group_info(self, group_name):
        """
        获取指定组的信息

        Args:
            group_name (str): 组名

        Returns:
            list: 该组的群号列表
        """
        try:
            self.cursor.execute(
                "SELECT group_id FROM group_associations WHERE group_name = ? ORDER BY group_id",
                (group_name,),
            )
            results = self.cursor.fetchall()
            return [row[0] for row in results]

        except sqlite3.Error:
            return []

    def get_group_statistics(self):
        """
        获取统计信息

        Returns:
            dict: 统计信息
        """
        try:
            # 总组数
            self.cursor.execute(
                "SELECT COUNT(DISTINCT group_name) FROM group_associations"
            )
            total_groups = self.cursor.fetchone()[0]

            # 总群数（去重）
            self.cursor.execute(
                "SELECT COUNT(DISTINCT group_id) FROM group_associations"
            )
            total_unique_groups = self.cursor.fetchone()[0]

            # 总关联数
            self.cursor.execute("SELECT COUNT(*) FROM group_associations")
            total_associations = self.cursor.fetchone()[0]

            return {
                "total_groups": total_groups,
                "total_unique_groups": total_unique_groups,
                "total_associations": total_associations,
            }

        except sqlite3.Error:
            return {}

    def get_all_group_names(self):
        """
        获取所有群组名字

        Returns:
            list: 所有群组名字列表
        """
        try:
            self.cursor.execute(
                "SELECT DISTINCT group_name FROM group_associations ORDER BY group_name"
            )
            results = self.cursor.fetchall()
            return [row[0] for row in results]

        except sqlite3.Error:
            return []

    def get_groups_in_association(self, group_name):
        """
        获取指定群组下的所有群号

        Args:
            group_name (str): 群组名

        Returns:
            list: 该群组下的所有群号列表，如果群组不存在则返回空列表
        """
        return self.get_group_info(group_name)

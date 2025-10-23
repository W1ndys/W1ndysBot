"""
数据迁移模块
负责从JSON文件格式迁移到SQLite数据库
"""

import os
import json
from logger import logger
from .database import db
from .config import DATA_ROOT_DIR


class SwitchMigration:
    """数据迁移管理器"""

    @staticmethod
    def migrate_from_json_to_sqlite():
        """
        从JSON文件迁移到SQLite数据库（无损升级）
        扫描所有模块的switch.json文件并导入到SQLite数据库中

        Returns:
            tuple: (迁移成功的模块数量, 迁移失败的数量)
        """
        logger.info("开始执行从JSON到SQLite的数据迁移...")
        migrated_count = 0
        error_count = 0

        try:
            # 准备批量操作列表
            operations = []

            # 遍历数据目录下的所有模块
            for module_name in os.listdir(DATA_ROOT_DIR):
                module_dir = os.path.join(DATA_ROOT_DIR, module_name)

                # 跳过非目录文件和Core目录
                if not os.path.isdir(module_dir) or module_name == "Core":
                    continue

                switch_file = os.path.join(module_dir, "switch.json")

                # 检查switch.json文件是否存在
                if not os.path.exists(switch_file):
                    continue

                try:
                    # 读取JSON文件
                    with open(switch_file, "r", encoding="utf-8") as f:
                        switch_data = json.load(f)

                    # 迁移群聊开关
                    if "group" in switch_data and switch_data["group"]:
                        for group_id, status in switch_data["group"].items():
                            operations.append(
                                (
                                    "INSERT OR REPLACE INTO module_switches (module_name, switch_type, group_id, status) VALUES (?, 'group', ?, ?)",
                                    (module_name, str(group_id), int(status)),
                                )
                            )

                    # 迁移私聊开关
                    if "private" in switch_data:
                        operations.append(
                            (
                                "INSERT OR REPLACE INTO module_switches (module_name, switch_type, group_id, status) VALUES (?, 'private', NULL, ?)",
                                (module_name, int(switch_data["private"])),
                            )
                        )

                    migrated_count += 1
                    logger.info(f"准备迁移模块 {module_name} 的开关数据")

                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"读取模块 {module_name} 的switch.json失败: {e}")
                    error_count += 1

            # 批量执行所有迁移操作
            if operations:
                success = db.execute_batch(operations)
                if success:
                    logger.info(
                        f"数据迁移完成：成功迁移 {migrated_count} 个模块，失败 {error_count} 个"
                    )
                else:
                    logger.error("批量迁移操作失败")
                    error_count += migrated_count
                    migrated_count = 0

            return migrated_count, error_count

        except Exception as e:
            logger.error(f"数据迁移过程中发生异常: {e}")
            return 0, 1

    @staticmethod
    def backup_json_files():
        """
        备份现有的JSON开关文件
        将所有switch.json文件重命名为switch.json.backup

        Returns:
            int: 备份成功的文件数量
        """
        logger.info("开始备份JSON开关文件...")
        backup_count = 0

        try:
            # 遍历数据目录下的所有模块
            for module_name in os.listdir(DATA_ROOT_DIR):
                module_dir = os.path.join(DATA_ROOT_DIR, module_name)

                # 跳过非目录文件和Core目录
                if not os.path.isdir(module_dir) or module_name == "Core":
                    continue

                switch_file = os.path.join(module_dir, "switch.json")
                backup_file = os.path.join(module_dir, "switch.json.backup")

                # 如果switch.json存在且备份文件不存在，则进行备份
                if os.path.exists(switch_file) and not os.path.exists(backup_file):
                    try:
                        os.rename(switch_file, backup_file)
                        backup_count += 1
                        logger.info(f"已备份模块 {module_name} 的开关文件")
                    except Exception as e:
                        logger.error(f"备份模块 {module_name} 开关文件失败: {e}")

            logger.info(f"备份完成：成功备份 {backup_count} 个开关文件")
            return backup_count

        except Exception as e:
            logger.error(f"备份过程中发生异常: {e}")
            return 0

    @staticmethod
    def check_migration_needed():
        """
        检查是否需要执行迁移

        Returns:
            tuple: (是否需要迁移, 数据库中的记录数量)
        """
        try:
            result = db.execute_query(
                "SELECT COUNT(*) FROM module_switches", fetch_one=True
            )
            record_count = result[0] if result else 0

            return record_count == 0, record_count
        except Exception as e:
            logger.error(f"检查迁移状态失败: {e}")
            return True, 0

    @staticmethod
    def upgrade_to_sqlite():
        """
        完整的升级流程：检查是否需要升级，执行迁移，备份旧文件

        Returns:
            tuple: (是否成功, 消息描述)
        """
        # 检查是否已经迁移过
        need_migration, record_count = SwitchMigration.check_migration_needed()

        if not need_migration:
            message = f"数据库中已有 {record_count} 条记录，跳过升级"
            logger.info(message)
            return True, message

        # 执行数据迁移
        migrated_count, error_count = SwitchMigration.migrate_from_json_to_sqlite()

        if migrated_count > 0:
            # 备份原始JSON文件
            backup_count = SwitchMigration.backup_json_files()

            message = f"升级完成：迁移了 {migrated_count} 个模块，备份了 {backup_count} 个文件"
            if error_count > 0:
                message += f"，{error_count} 个模块迁移失败"

            logger.info(message)
            return True, message
        else:
            message = "未找到需要迁移的数据"
            return False, message

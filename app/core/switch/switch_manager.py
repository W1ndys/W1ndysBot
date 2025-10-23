"""
开关管理核心模块
负责开关状态的查询、切换和管理逻辑
"""

from logger import logger
from .database import db


class SwitchManager:
    """开关管理器"""

    @staticmethod
    def is_group_switch_on(group_id, module_name):
        """
        判断群聊开关是否开启，默认关闭

        Args:
            group_id: 群号
            module_name: 模块名称

        Returns:
            bool: True表示开启，False表示关闭
        """
        try:
            result = db.execute_query(
                "SELECT status FROM module_switches WHERE module_name = ? AND switch_type = 'group' AND group_id = ?",
                (module_name, str(group_id)),
                fetch_one=True,
            )
            return bool(result[0]) if result else False
        except Exception as e:
            logger.error(f"[{module_name}]查询群聊开关状态失败: {e}")
            return False

    @staticmethod
    def is_private_switch_on(module_name):
        """
        判断私聊开关是否开启，默认关闭

        Args:
            module_name: 模块名称

        Returns:
            bool: True表示开启，False表示关闭
        """
        try:
            result = db.execute_query(
                "SELECT status FROM module_switches WHERE module_name = ? AND switch_type = 'private'",
                (module_name,),
                fetch_one=True,
            )
            return bool(result[0]) if result else False
        except Exception as e:
            logger.error(f"[{module_name}]查询私聊开关状态失败: {e}")
            return False

    @staticmethod
    def toggle_group_switch(group_id, module_name):
        """
        切换群聊开关

        Args:
            group_id: 群号
            module_name: 模块名称

        Returns:
            bool: 切换后的状态
        """
        try:
            switch_status = SwitchManager._toggle_switch(
                switch_type="group", module_name=module_name, group_id=group_id
            )
            logger.info(f"[{module_name}]群聊开关已切换为【{switch_status}】")
            return switch_status
        except Exception as e:
            logger.error(f"[{module_name}]切换群聊开关失败: {e}")
            return False

    @staticmethod
    def toggle_private_switch(module_name):
        """
        切换私聊开关

        Args:
            module_name: 模块名称

        Returns:
            bool: 切换后的状态
        """
        try:
            switch_status = SwitchManager._toggle_switch(
                switch_type="private", module_name=module_name
            )
            logger.info(f"[{module_name}]私聊开关已切换为【{switch_status}】")
            return switch_status
        except Exception as e:
            logger.error(f"[{module_name}]切换私聊开关失败: {e}")
            return False

    @staticmethod
    def _toggle_switch(switch_type, module_name, group_id="0"):
        """
        切换某模块的开关（内部方法）

        Args:
            switch_type: 开关类型，group或private
            module_name: 模块名称
            group_id: 群号，仅当switch_type为group时有效

        Returns:
            bool: 切换后的状态
        """
        try:
            if switch_type == "group":
                return SwitchManager._toggle_group_switch_internal(
                    module_name, group_id
                )
            elif switch_type == "private":
                return SwitchManager._toggle_private_switch_internal(module_name)
            else:
                raise ValueError(f"不支持的开关类型: {switch_type}")
        except Exception as e:
            logger.error(f"[{module_name}]切换开关失败: {e}")
            return False

    @staticmethod
    def _toggle_group_switch_internal(module_name, group_id):
        """群聊开关切换内部实现"""
        # 查询当前状态
        result = db.execute_query(
            "SELECT status FROM module_switches WHERE module_name = ? AND switch_type = 'group' AND group_id = ?",
            (module_name, str(group_id)),
            fetch_one=True,
        )

        if result:
            # 如果记录存在，切换状态
            new_status = 0 if result[0] else 1
            db.execute_update(
                "UPDATE module_switches SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE module_name = ? AND switch_type = 'group' AND group_id = ?",
                (new_status, module_name, str(group_id)),
            )
        else:
            # 如果记录不存在，创建新记录，默认开启
            new_status = 1
            db.execute_update(
                "INSERT INTO module_switches (module_name, switch_type, group_id, status) VALUES (?, 'group', ?, ?)",
                (module_name, str(group_id), new_status),
            )

        return bool(new_status)

    @staticmethod
    def _toggle_private_switch_internal(module_name):
        """私聊开关切换内部实现"""
        # 查询当前状态
        result = db.execute_query(
            "SELECT status FROM module_switches WHERE module_name = ? AND switch_type = 'private'",
            (module_name,),
            fetch_one=True,
        )

        if result:
            # 如果记录存在，切换状态
            new_status = 0 if result[0] else 1
            db.execute_update(
                "UPDATE module_switches SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE module_name = ? AND switch_type = 'private'",
                (new_status, module_name),
            )
        else:
            # 如果记录不存在，创建新记录，默认开启
            new_status = 1
            db.execute_update(
                "INSERT INTO module_switches (module_name, switch_type, group_id, status) VALUES (?, 'private', NULL, ?)",
                (module_name, new_status),
            )

        return bool(new_status)

    @staticmethod
    def get_group_all_switches(group_id):
        """
        获取某群组所有模块的开关

        Args:
            group_id: 群号

        Returns:
            dict: 格式为 {group_id: {module_name1: True, module_name2: False}}
        """
        try:
            results = db.execute_query(
                "SELECT module_name, status FROM module_switches WHERE switch_type = 'group' AND group_id = ?",
                (str(group_id),),
                fetch_all=True,
            )

            switch = {group_id: {}}
            for module_name, status in results or []:
                switch[group_id][module_name] = bool(status)

            return switch
        except Exception as e:
            logger.error(f"获取群组 {group_id} 所有模块开关失败: {e}")
            return {group_id: {}}

    @staticmethod
    def get_all_enabled_groups(module_name):
        """
        获取某模块所有已开启的群聊列表

        Args:
            module_name: 模块名称

        Returns:
            list: 开启的群号列表
        """
        try:
            results = db.execute_query(
                "SELECT group_id FROM module_switches WHERE module_name = ? AND switch_type = 'group' AND status = 1",
                (module_name,),
                fetch_all=True,
            )

            return [row[0] for row in results or []]
        except Exception as e:
            logger.error(f"[{module_name}]获取已开启群聊列表失败: {e}")
            return []

    @staticmethod
    def get_enabled_modules_in_group(group_id):
        """
        获取某群组中已开启的模块列表

        Args:
            group_id: 群号

        Returns:
            list: 已开启的模块名称列表
        """
        try:
            results = db.execute_query(
                "SELECT module_name FROM module_switches WHERE switch_type = 'group' AND group_id = ? AND status = 1",
                (str(group_id),),
                fetch_all=True,
            )

            return [row[0] for row in results or []]
        except Exception as e:
            logger.error(f"查询群组 {group_id} 已开启模块失败: {e}")
            return []

    @staticmethod
    def copy_group_switches(source_group_id, target_group_id):
        """
        复制源群组的开关数据到目标群组
        只覆盖源群存在的模块配置，源群没有的开关配置目标群保持不变

        Args:
            source_group_id: 源群号
            target_group_id: 目标群号

        Returns:
            tuple: (是否成功, 复制的模块列表, 保持不变的模块列表)
        """
        try:
            # 获取源群组的所有开关数据
            source_switches = db.execute_query(
                "SELECT module_name, status FROM module_switches WHERE switch_type = 'group' AND group_id = ?",
                (str(source_group_id),),
                fetch_all=True,
            )

            if not source_switches:
                return False, [], []

            # 获取目标群组现有的模块列表和状态
            target_existing_data = (
                db.execute_query(
                    "SELECT module_name, status FROM module_switches WHERE switch_type = 'group' AND group_id = ?",
                    (str(target_group_id),),
                    fetch_all=True,
                )
                or []
            )

            target_existing_modules = {row[0] for row in target_existing_data}
            target_modules_status = {row[0]: row[1] for row in target_existing_data}

            copied_modules = []
            source_module_names = set()

            # 准备批量操作
            operations = []

            # 复制每个模块的开关状态
            for module_name, status in source_switches:
                source_module_names.add(module_name)

                # 检查目标群是否已有该模块配置
                if module_name in target_existing_modules:
                    # 更新现有记录
                    operations.append(
                        (
                            "UPDATE module_switches SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE module_name = ? AND switch_type = 'group' AND group_id = ?",
                            (status, module_name, str(target_group_id)),
                        )
                    )
                else:
                    # 插入新记录
                    operations.append(
                        (
                            "INSERT INTO module_switches (module_name, switch_type, group_id, status, created_at, updated_at) VALUES (?, 'group', ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                            (module_name, str(target_group_id), status),
                        )
                    )

                # 记录复制的模块信息
                status_text = "开启" if status else "关闭"
                copied_modules.append(f"【{module_name}】- {status_text}")

            # 执行批量操作
            success = db.execute_batch(operations)

            if not success:
                return False, [], []

            # 计算保持不变的模块
            unchanged_module_names = target_existing_modules - source_module_names
            unchanged_modules = []
            for module_name in unchanged_module_names:
                status = target_modules_status.get(module_name, 0)
                status_text = "开启" if status else "关闭"
                unchanged_modules.append(f"【{module_name}】- {status_text}")

            logger.info(
                f"成功从群 {source_group_id} 复制 {len(copied_modules)} 个模块开关到群 {target_group_id}，"
                f"{len(unchanged_modules)} 个模块保持原有配置"
            )
            return True, copied_modules, unchanged_modules

        except Exception as e:
            logger.error(f"复制群开关数据失败: {e}")
            return False, [], []

    @staticmethod
    def clean_invalid_group_switches(valid_group_ids):
        """
        清理不在有效群列表中的群开关数据

        Args:
            valid_group_ids: 有效的群号列表（字符串格式）

        Returns:
            tuple: (cleaned_count, error_count, cleaned_groups)
                   清理的记录数量、出错数量、被清理的群号列表
        """
        try:
            if not valid_group_ids:
                logger.warning("[Switch]有效群列表为空，跳过清理群开关数据")
                return 0, 0, []

            # 获取所有群开关数据中的群号
            results = db.execute_query(
                "SELECT DISTINCT group_id FROM module_switches WHERE switch_type = 'group' AND group_id IS NOT NULL",
                fetch_all=True,
            )

            if not results:
                logger.info("[Switch]数据库中没有群开关数据，无需清理")
                return 0, 0, []

            stored_group_ids = [row[0] for row in results]

            # 找出不在有效群列表中的群号
            groups_to_clean = []
            for stored_group_id in stored_group_ids:
                if stored_group_id not in valid_group_ids:
                    groups_to_clean.append(stored_group_id)

            if not groups_to_clean:
                logger.info("[Switch]所有群开关数据都对应有效群，无需清理")
                return 0, 0, []

            # 删除无效群的开关数据
            cleaned_count = 0
            error_count = 0
            cleaned_groups = []

            for group_id in groups_to_clean:
                try:
                    # 先查询该群有多少条开关记录
                    count_result = db.execute_query(
                        "SELECT COUNT(*) FROM module_switches WHERE switch_type = 'group' AND group_id = ?",
                        (group_id,),
                        fetch_one=True,
                    )
                    record_count = count_result[0] if count_result else 0

                    if record_count > 0:
                        # 删除该群的所有开关记录
                        affected_rows = db.execute_update(
                            "DELETE FROM module_switches WHERE switch_type = 'group' AND group_id = ?",
                            (group_id,),
                        )

                        if affected_rows > 0:
                            cleaned_count += affected_rows
                            cleaned_groups.append(group_id)
                            logger.info(
                                f"[Switch]已清理群 {group_id} 的 {affected_rows} 条开关记录"
                            )
                        else:
                            logger.warning(f"[Switch]群 {group_id} 的开关记录删除失败")
                            error_count += 1
                    else:
                        logger.warning(f"[Switch]群 {group_id} 没有开关记录")

                except Exception as e:
                    error_count += 1
                    logger.error(f"[Switch]清理群 {group_id} 的开关记录失败: {e}")

            if cleaned_count > 0:
                logger.info(
                    f"[Switch]群开关数据清理完成，清理了 {len(cleaned_groups)} 个群的 {cleaned_count} 条记录"
                )
            if error_count > 0:
                logger.error(f"[Switch]群开关数据清理过程中出现 {error_count} 个错误")

            return cleaned_count, error_count, cleaned_groups

        except Exception as e:
            logger.error(f"[Switch]清理群开关数据失败: {e}")
            return 0, 1, []

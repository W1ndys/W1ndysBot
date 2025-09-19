"""
开关存储
每个模块的开关群记录和数据都存储在data/module_name目录下
开关文件为switch.json，存储结构为：
//群聊开关
{
    "group": {
        "群号1": True,
        "群号2": False
    },
    "private": True
}
"""

import os
import json
import sqlite3
import threading
from datetime import datetime
import logger
from utils.generate import generate_reply_message, generate_text_message
from api.message import send_private_msg, send_group_msg
from utils.auth import is_system_admin, is_group_admin

SWITCH_COMMAND = "switch"

# 数据根目录
DATA_ROOT_DIR = "data"

# 数据库文件路径
DATABASE_PATH = os.path.join(DATA_ROOT_DIR, "Core", "switches.db")

# 线程锁，确保数据库操作线程安全
db_lock = threading.Lock()

# 确保数据目录存在
os.makedirs(DATA_ROOT_DIR, exist_ok=True)


def init_database():
    """
    初始化数据库，创建必要的表
    """
    with db_lock:
        try:
            # 确保Core目录存在
            os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # 创建模块开关表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS module_switches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_name TEXT NOT NULL,
                    switch_type TEXT NOT NULL CHECK (switch_type IN ('group', 'private')),
                    group_id TEXT,
                    status INTEGER NOT NULL CHECK (status IN (0, 1)),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (module_name, switch_type, group_id)
                )
            """
            )

            # 创建索引以优化查询性能
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_module_group 
                ON module_switches(module_name, group_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_module_type 
                ON module_switches(module_name, switch_type)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_group_id 
                ON module_switches(group_id)
            """
            )

            conn.commit()
            conn.close()
            logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")


def get_db_connection():
    """
    获取数据库连接
    """
    return sqlite3.connect(DATABASE_PATH)


# 初始化数据库
init_database()


# 是否开启群聊开关
def is_group_switch_on(group_id, MODULE_NAME):
    """
    判断群聊开关是否开启，默认关闭
    group_id: 群号
    MODULE_NAME: 模块名称
    返回值:
    True: 开启
    False: 关闭
    """
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT status FROM module_switches WHERE module_name = ? AND switch_type = 'group' AND group_id = ?",
                (MODULE_NAME, str(group_id)),
            )
            result = cursor.fetchone()
            conn.close()
            return bool(result[0]) if result else False
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]查询群聊开关状态失败: {e}")
            return False


# 是否开启私聊开关
def is_private_switch_on(MODULE_NAME):
    """
    判断私聊开关是否开启，默认关闭
    MODULE_NAME: 模块名称
    返回值:
    True: 开启
    False: 关闭
    """
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT status FROM module_switches WHERE module_name = ? AND switch_type = 'private'",
                (MODULE_NAME,),
            )
            result = cursor.fetchone()
            conn.close()
            return bool(result[0]) if result else False
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]查询私聊开关状态失败: {e}")
            return False


# 切换群聊开关
def toggle_group_switch(group_id, MODULE_NAME):
    try:
        switch_status = toggle_switch(
            switch_type="group", group_id=group_id, MODULE_NAME=MODULE_NAME
        )
        logger.info(f"[{MODULE_NAME}]群聊开关已切换为【{switch_status}】")
        return switch_status
    except Exception as e:
        logger.error(f"[{MODULE_NAME}]切换群聊开关失败: {e}")
        return False


# 切换私聊开关
def toggle_private_switch(MODULE_NAME):
    try:
        switch_status = toggle_switch(switch_type="private", MODULE_NAME=MODULE_NAME)
        logger.info(f"[{MODULE_NAME}]私聊开关已切换为【{switch_status}】")
        return switch_status
    except Exception as e:
        logger.error(f"[{MODULE_NAME}]切换私聊开关失败: {e}")
        return False


def migrate_from_json_to_sqlite():
    """
    从JSON文件迁移到SQLite数据库（无损升级）
    扫描所有模块的switch.json文件并导入到SQLite数据库中
    """
    logger.info("开始执行从JSON到SQLite的数据迁移...")
    migrated_count = 0
    error_count = 0

    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

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
                            try:
                                cursor.execute(
                                    "INSERT OR REPLACE INTO module_switches (module_name, switch_type, group_id, status) VALUES (?, 'group', ?, ?)",
                                    (module_name, str(group_id), int(status)),
                                )
                            except Exception as e:
                                logger.error(
                                    f"迁移模块 {module_name} 群聊 {group_id} 开关失败: {e}"
                                )
                                error_count += 1

                    # 迁移私聊开关
                    if "private" in switch_data:
                        try:
                            cursor.execute(
                                "INSERT OR REPLACE INTO module_switches (module_name, switch_type, group_id, status) VALUES (?, 'private', NULL, ?)",
                                (module_name, int(switch_data["private"])),
                            )
                        except Exception as e:
                            logger.error(f"迁移模块 {module_name} 私聊开关失败: {e}")
                            error_count += 1

                    migrated_count += 1
                    logger.info(f"成功迁移模块 {module_name} 的开关数据")

                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"读取模块 {module_name} 的switch.json失败: {e}")
                    error_count += 1

            conn.commit()
            conn.close()

            logger.info(
                f"数据迁移完成：成功迁移 {migrated_count} 个模块，失败 {error_count} 个"
            )
            return migrated_count, error_count

        except Exception as e:
            logger.error(f"数据迁移过程中发生异常: {e}")
            return 0, 1


def backup_json_files():
    """
    备份现有的JSON开关文件
    将所有switch.json文件重命名为switch.json.backup
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


def upgrade_to_sqlite():
    """
    完整的升级流程：检查是否需要升级，执行迁移，备份旧文件
    """
    # 检查是否已经迁移过（数据库中是否有数据）
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM module_switches")
            record_count = cursor.fetchone()[0]
            conn.close()

            if record_count > 0:
                logger.info(f"数据库中已有 {record_count} 条记录，跳过升级")
                return True, "数据库中已有数据，无需升级"

        except Exception as e:
            logger.error(f"检查数据库状态失败: {e}")
            return False, f"检查数据库状态失败: {e}"

    # 执行数据迁移
    migrated_count, error_count = migrate_from_json_to_sqlite()

    if migrated_count > 0:
        # 备份原始JSON文件
        backup_count = backup_json_files()

        message = (
            f"升级完成：迁移了 {migrated_count} 个模块，备份了 {backup_count} 个文件"
        )
        if error_count > 0:
            message += f"，{error_count} 个模块迁移失败"

        logger.info(message)
        return True, message
    else:
        return False, "未找到需要迁移的数据"


def toggle_switch(switch_type, MODULE_NAME, group_id="0"):
    """
    切换某模块的开关
    switch_type: 开关类型，group或private
    group_id: 群号，仅当switch_type为group时有效
    MODULE_NAME: 模块名称
    """
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if switch_type == "group":
                # 查询当前状态
                cursor.execute(
                    "SELECT status FROM module_switches WHERE module_name = ? AND switch_type = 'group' AND group_id = ?",
                    (MODULE_NAME, str(group_id)),
                )
                result = cursor.fetchone()

                if result:
                    # 如果记录存在，切换状态
                    new_status = 0 if result[0] else 1
                    cursor.execute(
                        "UPDATE module_switches SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE module_name = ? AND switch_type = 'group' AND group_id = ?",
                        (new_status, MODULE_NAME, str(group_id)),
                    )
                else:
                    # 如果记录不存在，创建新记录，默认开启
                    new_status = 1
                    cursor.execute(
                        "INSERT INTO module_switches (module_name, switch_type, group_id, status) VALUES (?, 'group', ?, ?)",
                        (MODULE_NAME, str(group_id), new_status),
                    )
                result = bool(new_status)

            elif switch_type == "private":
                # 查询当前状态
                cursor.execute(
                    "SELECT status FROM module_switches WHERE module_name = ? AND switch_type = 'private'",
                    (MODULE_NAME,),
                )
                db_result = cursor.fetchone()

                if db_result:
                    # 如果记录存在，切换状态
                    new_status = 0 if db_result[0] else 1
                    cursor.execute(
                        "UPDATE module_switches SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE module_name = ? AND switch_type = 'private'",
                        (new_status, MODULE_NAME),
                    )
                else:
                    # 如果记录不存在，创建新记录，默认开启
                    new_status = 1
                    cursor.execute(
                        "INSERT INTO module_switches (module_name, switch_type, group_id, status) VALUES (?, 'private', NULL, ?)",
                        (MODULE_NAME, new_status),
                    )
                result = bool(new_status)

            conn.commit()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]切换开关失败: {e}")
            return False


def load_group_all_switch(group_id):
    """
    获取某群组所有模块的开关
    返回格式为：
    {
        "group_id": {
            "module_name1": True,
            "module_name2": False
        }
    }
    """
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT module_name, status FROM module_switches WHERE switch_type = 'group' AND group_id = ?",
                (str(group_id),),
            )
            results = cursor.fetchall()
            conn.close()

            switch = {group_id: {}}
            for module_name, status in results:
                switch[group_id][module_name] = bool(status)

            return switch
        except Exception as e:
            logger.error(f"获取群组 {group_id} 所有模块开关失败: {e}")
            return {group_id: {}}


def get_all_enabled_groups(MODULE_NAME):
    """
    获取某模块所有已开启的群聊列表
    MODULE_NAME: 模块名称
    返回值: 开启的群号列表
    """
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT group_id FROM module_switches WHERE module_name = ? AND switch_type = 'group' AND status = 1",
                (MODULE_NAME,),
            )
            results = cursor.fetchall()
            conn.close()

            return [row[0] for row in results]
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取已开启群聊列表失败: {e}")
            return []


async def handle_module_private_switch(MODULE_NAME, websocket, user_id, message_id):
    """
    处理模块私聊开关命令
    """
    try:
        switch_status = toggle_private_switch(MODULE_NAME)
        switch_status = "开启" if switch_status else "关闭"
        reply_message = generate_reply_message(message_id)
        text_message = generate_text_message(
            f"[{MODULE_NAME}]私聊开关已切换为【{switch_status}】"
        )
        await send_private_msg(
            websocket,
            user_id,
            [reply_message, text_message],
            note="del_msg=10",
        )
    except Exception as e:
        logger.error(f"[{MODULE_NAME}]处理模块私聊开关命令失败: {e}")


async def handle_module_group_switch(MODULE_NAME, websocket, group_id, message_id):
    """
    处理模块群聊开关命令
    """
    try:
        switch_status = toggle_group_switch(group_id, MODULE_NAME)
        switch_status = "开启" if switch_status else "关闭"
        reply_message = generate_reply_message(message_id)
        text_message = generate_text_message(
            f"[{MODULE_NAME}]群聊开关已切换为【{switch_status}】"
        )
        await send_group_msg(
            websocket,
            group_id,
            [reply_message, text_message],
            note="del_msg=10",
        )
        return switch_status
    except Exception as e:
        logger.error(f"[{MODULE_NAME}]处理模块群聊开关命令失败: {e}")


async def handle_events(websocket, message):
    """
    统一处理 switch 命令，支持群聊
    用来扫描本群已开启的模块
    """
    try:
        # 只处理文本消息
        if message.get("post_type") != "message":
            return
        raw_message = message.get("raw_message", "").lower()
        if raw_message != SWITCH_COMMAND:
            return

        # 获取基本信息
        user_id = str(message.get("user_id", ""))
        message_type = message.get("message_type", "")
        role = message.get("sender", {}).get("role", "")

        # 鉴权 - 根据消息类型进行不同的权限检查
        if message_type == "group":
            group_id = str(message.get("group_id", ""))
            # 群聊中需要是系统管理员或群管理员
            if not is_system_admin(user_id) and not is_group_admin(role):
                return

        message_id = message.get("message_id", "")
        reply_message = generate_reply_message(message_id)

        if message_type == "group":
            # 扫描本群已开启的模块
            enabled_modules = []
            with db_lock:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT module_name FROM module_switches WHERE switch_type = 'group' AND group_id = ? AND status = 1",
                        (str(group_id),),
                    )
                    results = cursor.fetchall()
                    conn.close()
                    enabled_modules = [row[0] for row in results]
                except Exception as e:
                    logger.error(f"查询群组 {group_id} 已开启模块失败: {e}")
                    enabled_modules = []

            if enabled_modules:
                switch_text = f"本群（{group_id}）已开启的模块：\n"
                for i, module_name in enumerate(enabled_modules, 1):
                    switch_text += f"{i}. 【{module_name}】\n"
                switch_text += f"\n共计 {len(enabled_modules)} 个模块"
            else:
                switch_text = f"本群（{group_id}）暂未开启任何模块"

            text_message = generate_text_message(switch_text)
            await send_group_msg(
                websocket,
                group_id,
                [reply_message, text_message],
                note="del_msg=30",
            )

    except Exception as e:
        logger.error(f"[SwitchManager]处理开关查询命令失败: {e}")


# 自动执行从JSON到SQLite的升级
try:
    success, message = upgrade_to_sqlite()
    if success:
        logger.info(f"自动升级成功: {message}")
    else:
        logger.info(f"自动升级跳过: {message}")
except Exception as e:
    logger.error(f"自动升级失败: {e}")

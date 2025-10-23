from logger import logger
from config import OWNER_ID
from api.group import get_group_list
from api.message import send_private_msg
import os
import json
import time
from . import switchs

DATA_DIR = os.path.join("data", "Core", "get_group_list.json")
MEMBER_DATA_DIR = os.path.join("data", "Core", "group_member_list")

# 全局变量，记录上次请求时间
last_request_time = 0
REQUEST_INTERVAL = 300  # 5分钟，单位：秒


def save_group_list_to_file(item):
    """
    保存群列表信息到文件，确保文件夹存在
    """
    dir_path = os.path.dirname(DATA_DIR)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(DATA_DIR, "w", encoding="utf-8") as f:
        json.dump(item, f, ensure_ascii=False, indent=2)


def get_group_name_by_id(group_id):
    """
    根据群号获取群名

    Args:
        group_id (str或int): 群号

    Returns:
        str: 群名称，如果找不到则返回None
    """
    try:
        # 确保群号是字符串格式
        group_id = str(group_id)

        # 检查文件是否存在
        if not os.path.exists(DATA_DIR):
            logger.warning(f"[Core]群列表文件不存在: {DATA_DIR}")
            return None

        # 读取群列表文件
        with open(DATA_DIR, "r", encoding="utf-8") as f:
            group_list = json.load(f)

        # 查找匹配的群号
        for group in group_list:
            if str(group.get("group_id")) == group_id:
                return group.get("group_name")

        logger.warning(f"[Core]未找到群号 {group_id} 对应的群名")
        return None

    except Exception as e:
        logger.error(f"[Core]获取群名失败: {e}")
        return None


def get_all_group_ids():
    """
    获取所有群号

    Returns:
        list: 群号列表，如果获取失败则返回空列表
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(DATA_DIR):
            logger.warning(f"[Core]群列表文件不存在: {DATA_DIR}")
            return []

        # 读取群列表文件
        with open(DATA_DIR, "r", encoding="utf-8") as f:
            group_list = json.load(f)

        # 提取所有群号
        group_ids = [
            str(group.get("group_id")) for group in group_list if group.get("group_id")
        ]

        logger.info(f"[Core]获取到 {len(group_ids)} 个群号, 群号列表: {group_ids}")
        return group_ids

    except Exception as e:
        logger.error(f"[Core]获取所有群号失败: {e}")
        return []


def get_group_member_info_by_id(group_id):
    """
    根据群号获取该群的成员信息（当前人数、最大人数和群名）

    Args:
        group_id (str或int): 群号

    Returns:
        dict: 包含成员信息的字典，格式：
              {
                  "member_count": int,      # 当前群成员数量
                  "max_member_count": int,  # 群最大成员数量限制
                  "group_name": str         # 群名称
              }
              如果找不到则返回None
    """
    try:
        # 确保群号是字符串格式
        group_id = str(group_id)

        # 检查文件是否存在
        if not os.path.exists(DATA_DIR):
            logger.warning(f"[Core]群列表文件不存在: {DATA_DIR}")
            return None

        # 读取群列表文件
        with open(DATA_DIR, "r", encoding="utf-8") as f:
            group_list = json.load(f)

        # 查找匹配的群号
        for group in group_list:
            if str(group.get("group_id")) == group_id:
                member_info = {
                    "member_count": group.get("member_count", 0),
                    "max_member_count": group.get("max_member_count", 0),
                    "group_name": group.get("group_name", ""),
                }
                logger.info(
                    f"[Core]获取群 {group_id} 成员信息: 当前人数 {member_info['member_count']}, 最大人数 {member_info['max_member_count']}, 群名 {member_info['group_name']}"
                )
                return member_info

        logger.warning(f"[Core]未找到群号 {group_id} 对应的成员信息")
        return None

    except Exception as e:
        logger.error(f"[Core]获取群成员信息失败: {e}")
        return None


def clean_old_group_member_data():
    """
    清理不在当前群列表中的群成员数据文件

    检查 group_member_list 目录中的所有文件，如果对应的群号不在当前群列表中，
    则删除该群的成员数据文件（说明机器人已经不在该群了）

    Returns:
        tuple: (cleaned_count, error_count) 清理的文件数量和出错的文件数量
    """
    try:
        # 获取当前所有群号
        current_group_ids = get_all_group_ids()
        if not current_group_ids:
            logger.warning("[Core]当前群列表为空，跳过清理群成员数据")
            return 0, 0

        # 检查群成员数据目录是否存在
        if not os.path.exists(MEMBER_DATA_DIR):
            logger.info("[Core]群成员数据目录不存在，无需清理")
            return 0, 0

        # 获取所有群成员数据文件
        member_data_files = []
        try:
            member_data_files = [
                f for f in os.listdir(MEMBER_DATA_DIR) if f.endswith(".json")
            ]
        except Exception as e:
            logger.error(f"[Core]读取群成员数据目录失败: {e}")
            return 0, 1

        if not member_data_files:
            logger.info("[Core]群成员数据目录为空，无需清理")
            return 0, 0

        # 提取群号（去掉.json后缀）
        stored_group_ids = [f.replace(".json", "") for f in member_data_files]

        # 找出不在当前群列表中的群号
        groups_to_clean = []
        for stored_group_id in stored_group_ids:
            if stored_group_id not in current_group_ids:
                groups_to_clean.append(stored_group_id)

        if not groups_to_clean:
            logger.info("[Core]所有群成员数据都对应当前群列表，无需清理")
            return 0, 0

        # 删除不在群列表中的群成员数据文件
        cleaned_count = 0
        error_count = 0

        for group_id in groups_to_clean:
            try:
                file_path = os.path.join(MEMBER_DATA_DIR, f"{group_id}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned_count += 1
                    logger.info(f"[Core]已清理群 {group_id} 的成员数据文件")
                else:
                    logger.warning(
                        f"[Core]群 {group_id} 的成员数据文件不存在: {file_path}"
                    )
            except Exception as e:
                error_count += 1
                logger.error(f"[Core]清理群 {group_id} 的成员数据文件失败: {e}")

        if cleaned_count > 0:
            logger.info(
                f"[Core]群成员数据清理完成，清理了 {cleaned_count} 个群的数据文件"
            )
        if error_count > 0:
            logger.error(f"[Core]群成员数据清理过程中出现 {error_count} 个错误")

        return cleaned_count, error_count

    except Exception as e:
        logger.error(f"[Core]清理群成员数据失败: {e}")
        return 0, 1


async def handle_events(websocket, msg):
    """
    处理回应事件
    响应示例:
    {
        "status": "ok",            // 状态，"ok"表示成功
        "retcode": 0,              // 返回码，0通常表示成功
        "data": [                  // 包含多个群组信息的数组
            {
                "group_all_shut": 0,        // 群禁言状态，0表示未全员禁言，1表示已全员禁言，-1表示未知或不适用
                "group_remark": "",         // 群备注名
                "group_id": "********",     // 群号 (已脱敏)
                "group_name": "********",   // 群名称 (已脱敏)
                "member_count": 41,         // 当前群成员数量
                "max_member_count": 200     // 群最大成员数量限制
            }
        ],
        "message": "",              // 状态消息，通常在出错时包含错误信息
        "wording": "",              // 补充信息或提示
        "echo": null                // 回显字段，通常用于请求和响应的匹配
    }
    """
    global last_request_time
    try:
        current_time = int(time.time())
        # 检查距离上次请求是否已超过指定时间
        if current_time - last_request_time >= REQUEST_INTERVAL:
            # 发送获取群列表的请求
            await get_group_list(websocket, no_cache=True)
            last_request_time = current_time

        # 如果有修改群名的通知
        if msg.get("sub_type") == "group_name":
            # 发送获取群列表的请求
            await get_group_list(websocket, no_cache=True)
            last_request_time = current_time

        # 如果有进退群通知
        if (
            msg.get("notice_type") == "group_increase"
            or msg.get("notice_type") == "group_decrease"
        ):
            # 发送获取群列表的请求
            await get_group_list(websocket, no_cache=True)
            last_request_time = current_time

        if msg.get("status") == "ok":
            echo = msg.get("echo", "")
            if echo == "get_group_list":
                # 保存data
                save_group_list_to_file(msg.get("data", []))
                logger.info(f"[Core]已保存群列表")
                # 群列表更新后，清理不在群列表中的群成员数据和开关数据
                try:
                    # 获取当前有效的群号列表
                    current_group_ids = get_all_group_ids()

                    # 清理群成员数据
                    member_cleaned_count, member_error_count = (
                        clean_old_group_member_data()
                    )

                    # 清理群开关数据
                    switch_cleaned_count, switch_error_count, switch_cleaned_groups = (
                        switchs.clean_invalid_group_switches(current_group_ids)
                    )

                    # 统计总的清理结果
                    total_cleaned = member_cleaned_count + switch_cleaned_count
                    total_errors = member_error_count + switch_error_count

                    # 只在有清理操作或出现错误时才发送通知
                    if total_cleaned > 0 or total_errors > 0:
                        notification_parts = []

                        if member_cleaned_count > 0:
                            notification_parts.append(
                                f"🗑️ 群成员数据清理：清理了 {member_cleaned_count} 个Bot不在的群的数据文件"
                            )

                        if switch_cleaned_count > 0:
                            notification_parts.append(
                                f"⚙️ 群开关数据清理：清理了 {len(switch_cleaned_groups)} 个Bot不在的群的 {switch_cleaned_count} 条开关记录"
                            )

                        if total_errors > 0:
                            notification_parts.append(
                                f"❌ 清理过程中出现 {total_errors} 个错误"
                            )

                        notification_msg = "\n".join(notification_parts)
                        await send_private_msg(
                            websocket,
                            OWNER_ID,
                            f"[Core]数据清理完成\n{notification_msg}",
                        )

                except Exception as e:
                    logger.error(f"[Core]执行数据清理时出错: {e}")
                    await send_private_msg(
                        websocket, OWNER_ID, f"[Core]执行数据清理时出错: {e}"
                    )
    except Exception as e:
        logger.error(f"[Core]获取群列表失败: {e}")
        await send_private_msg(websocket, OWNER_ID, f"[Core]获取群列表失败: {e}")

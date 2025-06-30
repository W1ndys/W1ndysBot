"""
自动撤回自己发送的消息
"""

import logger
import re
import asyncio
from api.message import delete_msg
import os
import json
import time

DEL_MSG_DB_PATH = os.path.join("data", "Core", "del_msg.json")


def load_del_msg_data():
    """
    加载待撤回消息数据
    """
    try:
        if os.path.exists(DEL_MSG_DB_PATH):
            with open(DEL_MSG_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"加载撤回消息数据失败: {e}")
        return {}


def save_del_msg_data(data):
    """
    保存待撤回消息数据
    """
    try:
        os.makedirs(os.path.dirname(DEL_MSG_DB_PATH), exist_ok=True)
        with open(DEL_MSG_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存撤回消息数据失败: {e}")


def add_del_msg_task(msg_id, del_time):
    """
    添加待撤回消息任务到本地存储
    """
    try:
        data = load_del_msg_data()
        delete_timestamp = time.time() + del_time
        data[str(msg_id)] = {
            "message_id": msg_id,
            "delete_timestamp": delete_timestamp,
            "del_time": del_time,
        }
        save_del_msg_data(data)
        logger.info(f"已添加消息 {msg_id} 到撤回任务列表，将在 {del_time} 秒后撤回")
    except Exception as e:
        logger.error(f"添加撤回消息任务失败: {e}")


def remove_del_msg_task(msg_id):
    """
    从本地存储中移除已撤回的消息任务
    """
    try:
        data = load_del_msg_data()
        if str(msg_id) in data:
            del data[str(msg_id)]
            save_del_msg_data(data)
            logger.info(f"已从撤回任务列表中移除消息 {msg_id}")
    except Exception as e:
        logger.error(f"移除撤回消息任务失败: {e}")


async def restore_del_msg_tasks(websocket):
    """
    恢复重启前的撤回消息任务
    """
    try:
        data = load_del_msg_data()
        current_time = time.time()

        for msg_id, task_info in list(data.items()):
            delete_timestamp = task_info.get("delete_timestamp", 0)
            remaining_time = delete_timestamp - current_time

            if remaining_time > 0:
                # 如果还没到撤回时间，重新创建任务
                logger.info(
                    f"恢复撤回任务: 消息 {msg_id} 将在 {remaining_time:.1f} 秒后撤回"
                )
                asyncio.create_task(
                    del_self_msg(websocket, int(msg_id), remaining_time)
                )
            else:
                # 如果已经超过撤回时间，立即撤回
                logger.info(f"立即撤回过期消息: {msg_id}")
                asyncio.create_task(del_self_msg(websocket, int(msg_id), 0))
    except Exception as e:
        logger.error(f"恢复撤回消息任务失败: {e}")


async def del_self_msg(websocket, msg_id, del_time):
    """
    定时撤回消息
    """
    logger.info(f"自动撤回消息: {msg_id} 将在 {del_time} 秒后撤回")
    await asyncio.sleep(del_time)
    try:
        await delete_msg(websocket, msg_id)
        # 撤回成功后从本地存储中移除
        remove_del_msg_task(msg_id)
    except Exception as e:
        logger.error(f"撤回消息 {msg_id} 失败: {e}")
        # 撤回失败也要移除任务，避免重复尝试
        remove_del_msg_task(msg_id)


async def handle_events(websocket, msg):
    """
    处理回应事件
    """
    try:
        # 处理首次连接事件，扫描本地存储中的待撤回消息
        if (
            msg.get("post_type") == "meta_event"
            and msg.get("meta_event_type") == "lifecycle"
            and msg.get("sub_type") == "connect"
        ):
            await restore_del_msg_tasks(websocket)
            return

        # 处理回应事件
        if msg.get("status") == "ok":
            echo = msg.get("echo", {})
            # 格式：del_msg=秒数
            res = re.search(r"del_msg=(\d+)", echo)
            if res:
                del_time = int(res.group(1))
                message_id = msg.get("data", {}).get("message_id")

                if del_time > 120:  # 只对超过120秒的进行存储
                    add_del_msg_task(message_id, del_time)
                    logger.success(f"[Core]待撤回消息已存储到本地: 消息 {message_id}")

                # 无论是否存储，都创建撤回任务
                asyncio.create_task(del_self_msg(websocket, message_id, del_time))
    except Exception as e:
        logger.error(f"自动撤回发送的消息失败: {e}")

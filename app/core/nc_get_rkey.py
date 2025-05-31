import logger
from config import OWNER_ID
from api.key import nc_get_rkey
from api.message import send_private_msg
import re
import os
import json
import time

DATA_DIR = os.path.join("data", "Core", "nc_get_rkey.json")

# 全局变量，记录上次请求时间
last_request_time = 0
REQUEST_INTERVAL = 600  # 10分钟，单位：秒


def save_rkey_to_file(item):
    """
    保存rkey信息到文件，确保文件夹存在
    """
    dir_path = os.path.dirname(DATA_DIR)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(DATA_DIR, "w", encoding="utf-8") as f:
        json.dump(item, f, ensure_ascii=False, indent=2)


async def handle_events(websocket, msg):
    """
    处理回应事件
    响应示例:
    {
        "status": "ok",
        "retcode": 0,
        "data": [
            {
                "rkey": "string",
                "ttl": "string",
                "time": 0,
                "type": 0
            }
        ],
        "message": "string",
        "wording": "string",
        "echo": "string"
    }
    """
    global last_request_time
    try:
        current_time = int(time.time())
        # 检查距离上次请求是否已超过10分钟
        if current_time - last_request_time >= REQUEST_INTERVAL:
            # 发送nc_get_rkey请求
            await nc_get_rkey(websocket)
            last_request_time = current_time

        if msg.get("status") == "ok":
            echo = msg.get("echo", "")
            # 格式：nc_get_rkey
            match = re.search(r"nc_get_rkey", echo)
            if match:
                data_list = msg.get("data", [])
                if isinstance(data_list, list) and len(data_list) > 0:
                    for item in data_list:
                        rkey = item.get("rkey")
                        ttl = item.get("ttl")
                        rkey_time = item.get("time")
                        rkey_type = item.get("type")
                        # 保存到文件
                        save_rkey_to_file(item)
                        logger.success(
                            f"获取到nc_get_rkey: rkey={rkey}, ttl={ttl}, time={rkey_time}, type={rkey_type}，已保存到文件")
                else:
                    logger.warning("未获取到有效的rkey数据列表")
    except Exception as e:
        logger.error(f"自动刷新rkey失败: {e}")
        await send_private_msg(websocket, OWNER_ID, f"自动刷新rkey失败: {e}")

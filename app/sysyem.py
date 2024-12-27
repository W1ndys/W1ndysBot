# script/System/main.py

import logging
import os
import sys
from datetime import datetime
import re

# 添加项目根目录到sys.path
sys.path.append((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.api import *

# 该机器人系统的日志目录
LOG_DIR = os.path.join((os.path.dirname(os.path.abspath(__file__))), "logs")


def get_latest_log_file(log_dir):
    """获取日志目录内最新的日志文件"""
    try:
        return max(
            [
                os.path.join(log_dir, f)
                for f in os.listdir(log_dir)
                if f.endswith(".log")
            ],
            key=lambda x: datetime.strptime(
                os.path.basename(x), "%Y-%m-%d_%H-%M-%S.log"
            ),
        )
    except ValueError:
        logging.error("日志目录中没有找到日志文件")
        return None


# 获取日志文件的最后的指定行日志
def get_last_n_lines(file_path, n):
    with open(file_path, "rb") as f:
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        buffer_size = 1024
        buffer = bytearray()
        lines_found = 0
        while file_size > 0:
            file_size -= buffer_size
            if file_size < 0:
                buffer_size += file_size
                file_size = 0
            f.seek(file_size)
            buffer.extend(f.read(buffer_size + 1))
        lines = buffer.splitlines()
        return lines[-n:]


# 群消息处理函数
async def handle_System_group_message(websocket, msg):

    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))
        latest_log_file = get_latest_log_file(LOG_DIR)
        last_n_lines = get_last_n_lines(latest_log_file, 10)

        if user_id not in owner_id:
            return

        match = re.search(r"logs(\d+)", raw_message)
        if match:
            num_lines = int(match.group(1))
            last_n_lines = get_last_n_lines(latest_log_file, num_lines)
            # 发送日志行到群组
            await send_group_msg(
                websocket,
                group_id,
                "\n".join(line.decode("utf-8") for line in last_n_lines),
            )
            return

    except Exception as e:
        logging.error(f"处理System群消息失败: {e}")
        await send_group_msg(
            websocket,
            group_id,
            "处理System群消息失败，错误信息：" + str(e),
        )
        return

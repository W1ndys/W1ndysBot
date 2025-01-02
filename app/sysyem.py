# script/System/main.py

import logging
import os
import sys
from datetime import datetime
import re
from collections import deque

# 添加项目根目录到sys.path
sys.path.append((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.api import *

# 该机器人系统的日志目录
LOG_DIR = os.path.join((os.path.dirname(os.path.abspath(__file__))), "logs")

# 确保日志目录存在
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


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


# 获取指定文件的最后的指定行内容
def get_last_n_lines(file_path, n):
    """从文件中获取最后n行"""
    try:
        with open(file_path, "rb") as file:
            # 使用seek从文件末尾开始读取
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            buffer_size = 1024
            buffer = deque()
            lines = []

            while file_size > 0 and len(lines) <= n:
                # 计算要读取的字节数
                read_size = min(buffer_size, file_size)
                file_size -= read_size
                file.seek(file_size)
                data = file.read(read_size)
                buffer.appendleft(data)  # 直接添加数据

                # 将缓冲区转换为字节串并分割行
                lines = b"".join(buffer).splitlines()

            # 返回最后n行
            return lines[-n:]
    except Exception as e:
        logging.error(f"读取文件失败: {e}")
        return []


# 过滤日志中的debug日志
def filter_debug_logs(log_content):
    """过滤掉日志内容中的DEBUG级别日志"""
    try:
        # 将日志内容按行分割
        lines = log_content.splitlines()

        # 过滤掉包含"DEBUG"的行
        filtered_lines = [line for line in lines if "DEBUG" not in line]

        # 返回过滤后的内容
        return "\n".join(filtered_lines)

    except Exception as e:
        logging.error(f"过滤DEBUG日志失败: {e}")
        return log_content  # 返回原始内容以防止数据丢失


# 群消息处理函数
async def handle_System_group_message(websocket, msg):

    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))
        latest_log_file = get_latest_log_file(LOG_DIR)

        if user_id not in owner_id:
            return

        match_logs = re.search(r"logs(\d+)", raw_message)
        match_errorlog = re.search(r"errorlog(\d+)", raw_message)

        if match_logs:
            num_lines = int(match_logs.group(1))
            last_n_lines = get_last_n_lines(latest_log_file, num_lines)
            last_n_lines_str = "\n".join(line.decode("utf-8") for line in last_n_lines)
            last_n_lines_filter_debug_logs = filter_debug_logs(last_n_lines_str)
            latest_log_file = latest_log_file or "未知日志文件"
            last_n_lines_filter_debug_logs = (
                last_n_lines_filter_debug_logs or "无日志内容"
            )
            message = (
                "日志文件: " + latest_log_file + "\n\n" + last_n_lines_filter_debug_logs
            )
            await send_group_msg(websocket, group_id, message)

            error_lines = [
                line for line in last_n_lines_str.splitlines() if "ERROR" in line
            ]
            if error_lines:
                error_message = "错误日志:\n" + "\n".join(error_lines)
                await send_group_msg(websocket, group_id, error_message)
            return

        if match_errorlog:
            num_lines = int(match_errorlog.group(1))
            all_lines = get_last_n_lines(latest_log_file, 1000)  # 假设读取足够多的行
            all_lines_str = "\n".join(line.decode("utf-8") for line in all_lines)
            error_lines = [
                line for line in all_lines_str.splitlines() if "ERROR" in line
            ]

            # 取最近的指定数量的错误日志
            recent_error_lines = error_lines[-num_lines:]

            if recent_error_lines:
                error_message = "错误日志:\n" + "\n".join(recent_error_lines)
                await send_group_msg(websocket, group_id, error_message)
            else:
                await send_group_msg(websocket, group_id, "没有找到错误日志")
            return

    except Exception as e:
        logging.error(f"处理System群消息失败: {e}")
        await send_group_msg(
            websocket,
            group_id,
            "处理System群消息失败，错误信息：" + str(e),
        )
        return

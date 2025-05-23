"""
日志清理
"""

import os
import time
from api.message import send_private_msg
from config import OWNER_ID
import logger

LOGS_DIR = "logs"

# 天数
DAYS = 7


async def clean_logs(websocket, msg):
    """清理日志"""
    if not os.path.exists(LOGS_DIR):
        return

    # 获取当前时间
    current_time = time.time()

    # 存储删除的文件
    deleted_files = []
    # 遍历日志目录
    for file in os.listdir(LOGS_DIR):
        file_path = os.path.join(LOGS_DIR, file)
        # 检查文件是否超过指定天数
        if (
            os.path.isfile(file_path)
            and os.path.getmtime(file_path) < current_time - DAYS * 24 * 60 * 60
        ):
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
                logger.info(f"已删除过期日志文件: {file_path}")
            except Exception as e:
                logger.error(f"删除日志文件失败: {e}")
                await send_private_msg(websocket, OWNER_ID, f"删除日志文件失败: {e}")

    # 发送删除的文件列表
    if deleted_files:
        await send_private_msg(
            websocket,
            OWNER_ID,
            f"已删除过期日志文件: \n{'\n'.join(deleted_files)}",
        )

# script/System/main.py

import logging
import os
import sys

# 添加项目根目录到sys.path
sys.path.append((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.api import *

# 该机器人系统的日志目录
LOG_DIR = os.path.join((os.path.dirname(os.path.abspath(__file__))), "logs")
print(LOG_DIR)

# 群消息处理函数
async def handle_System_group_message(websocket, msg):

    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))

    except Exception as e:
        logging.error(f"处理System群消息失败: {e}")
        await send_group_msg(group_id, "处理System群消息失败，错误信息：" + str(e))
        return


# 群通知处理函数
async def handle_System_group_notice(websocket, msg):
    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))

    except Exception as e:
        logging.error(f"处理System群通知失败: {e}")
        await send_group_msg(group_id, "处理System群通知失败，错误信息：" + str(e))
        return

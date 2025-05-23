# app/core/online_detect.py

import logger
from config import OWNER_ID
from api.message import send_private_msg
from utils.feishu import feishu
import time

# 全局变量
is_online = None  # 初始状态为None
last_state_change_time = 0
last_report_time = 0


async def handle_events(websocket, message):
    """处理心跳事件，检测在线状态"""
    global is_online, last_state_change_time, last_report_time

    try:
        # 处理首次连接事件
        if (
            message.get("post_type") == "meta_event"
            and message.get("meta_event_type") == "lifecycle"
            and message.get("sub_type") == "connect"
        ):
            current_time = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(message.get("time", int(time.time()))),
            )
            connect_msg = f"W1ndysGroupBot已上线！\n机器人ID: {message.get('self_id')}\n上线时间: {current_time}"
            logger.info(f"机器人首次连接: {connect_msg}")

            # 向管理员发送私聊消息
            try:
                await send_private_msg(websocket, OWNER_ID, connect_msg)
            except Exception as e:
                logger.error(f"发送上线通知失败: {e}")
            return

        # 只处理心跳事件
        if (
            message.get("post_type") != "meta_event"
            or message.get("meta_event_type") != "heartbeat"
        ):
            return

        # 获取在线状态
        status = message.get("status", {})
        current_online = status.get("online", False)

        # 如果是首次检测或状态发生变化
        current_time = int(time.time())
        if is_online is None or is_online != current_online:
            last_state_change_time = current_time
            last_report_time = current_time

            # 生成通知消息
            if is_online is None:
                status_text = "初始化" if current_online else "掉线"
            else:
                status_text = "重新上线" if current_online else "掉线"

            title = f"机器人状态变更: {status_text}"
            content = (
                f"机器人ID: {message.get('self_id')}\n"
                f"当前状态: {'在线' if current_online else '离线'}\n"
                f"状态变更时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}\n"
                f"心跳间隔: {message.get('interval', 0)/1000}秒"
            )

            # 发送通知
            logger.info(f"机器人状态变更: {status_text}")
            try:
                # 发送飞书通知
                feishu_result = feishu(title, content)
                if "error" in feishu_result:
                    logger.error(f"发送飞书通知失败: {feishu_result.get('error')}")

            except Exception as e:
                logger.error(f"发送飞书通知失败: {e}")

            # 更新状态
            is_online = current_online
    except KeyError as e:
        logger.error(f"处理心跳事件时发生键错误: {e}")
    except TypeError as e:
        logger.error(f"处理心跳事件时发生类型错误: {e}")
    except ValueError as e:
        logger.error(f"处理心跳事件时发生值错误: {e}")
    except Exception as e:
        logger.error(f"处理心跳事件时发生未知错误: {e}")

# handlers/message_handler.py

import json
import logging
import os
import sys
import asyncio


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scripts.GroupManager.main import handle_GroupManager_group_message

from app.scripts.Crypto.main import (
    handle_crypto_group_message,
    handle_crypto_private_message,
)
from app.scripts.Tools.main import (
    handle_group_message as handle_tools_group_message,
    handle_private_message as handle_tools_private_message,
)

from app.scripts.AI.kimi import handle_kimi_group_message


from app.scripts.QASystem.main import handle_qasystem_message_group
from app.scripts.BlacklistSystem.main import (
    handle_blacklist_message_group,
    handle_blacklist_request_event,
    handle_blacklist_group_notice,
)

from app.scripts.WelcomeFarewell.main import (
    handle_WelcomeFarewell_group_notice,
    WelcomeFarewell_manage,
)

from app.scripts.InviteChain.main import (
    handle_InviteChain_group_message,
    handle_InviteChain_group_notice,
)
from app.scripts.BanWords.main import handle_BanWords_group_message
from app.scripts.QFNUTracker.main import (
    start_qfnu_tracker,
    handle_QFNUTracker_group_message,
)

from app.scripts.Custom.main import (
    handle_Custom_group_message,
    handle_Custom_private_message,
)

from app.scripts.SoftBan.main import SoftBan_main

# 总开关
from app.switch import handle_GroupSwitch_group_message

# 菜单
from app.menu import handle_Menu_group_message


# 处理消息事件的逻辑
async def handle_message_event(websocket, msg):
    try:
        # 处理群消息
        if msg.get("message_type") == "group":

            group_id = msg["group_id"]
            logging.info(f"处理群消息,群ID:{group_id}")

            # 并发执行群消息处理函数
            await asyncio.gather(
                handle_GroupManager_group_message(websocket, msg),  # 群管系统
                handle_crypto_group_message(websocket, msg),  # 编解码功能
                handle_tools_group_message(websocket, msg),  # 实用的API工具功能
                handle_qasystem_message_group(websocket, msg),  # 处理知识库问答系统
                handle_blacklist_message_group(websocket, msg),  # 处理黑名单系统
                handle_GroupSwitch_group_message(websocket, msg),  # 处理群组开关
                handle_BanWords_group_message(websocket, msg),  # 处理违禁词系统
                WelcomeFarewell_manage(websocket, msg),  # 处理入群欢迎和退群欢送的管理
                handle_Menu_group_message(websocket, msg),  # 处理菜单
                handle_InviteChain_group_message(websocket, msg),  # 处理邀请链
                SoftBan_main(websocket, msg),  # 处理软封禁
                handle_QFNUTracker_group_message(
                    websocket, msg
                ),  # 处理QFNU追踪器开关消息
                handle_kimi_group_message(websocket, msg),  # 处理kimi群消息
                handle_Custom_group_message(websocket, msg),  # 处理自定义群消息
            )

        # 处理私聊消息
        elif msg.get("message_type") == "private":
            user_id = msg.get("user_id")
            # 并发执行私聊消息处理函数
            await asyncio.gather(
                handle_crypto_private_message(websocket, msg),  # 编解码功能
                handle_tools_private_message(websocket, msg),  # 实用的API工具功能
                handle_Custom_private_message(websocket, msg),  # 处理自定义私聊消息
                # handle_qwen_message_private(websocket, user_id, msg)  # 处理通义千问
            )

        else:
            logging.info(f"收到未知消息类型: {msg}")

    except KeyError as e:
        logging.error(f"处理消息事件的逻辑错误: {e}")


# 处理通知事件的逻辑
async def handle_notice_event(websocket, msg):

    # 处理群通知
    if msg.get("post_type") == "notice":
        group_id = msg["group_id"]
        logging.info(f"处理群通知事件, 群ID: {group_id}")

        await asyncio.gather(
            handle_WelcomeFarewell_group_notice(
                websocket, msg
            ),  # 处理入群欢迎和退群欢送的管理
            handle_InviteChain_group_notice(websocket, msg),  # 处理邀请链
            handle_blacklist_group_notice(websocket, msg),  # 处理黑名单检查
        )


# 处理请求事件的逻辑
async def handle_request_event(websocket, msg):

    await asyncio.gather(
        handle_blacklist_request_event(websocket, msg)  # 处理黑名单请求事件
    )


# 处理元事件的逻辑
async def handle_meta_event(websocket, msg):
    pass


# 处理定时任务，每个心跳周期检查一次
async def handle_cron_task(websocket):
    try:
        await start_qfnu_tracker(websocket)
    except Exception as e:
        logging.error(f"处理定时任务的逻辑错误: {e}")


# 处理ws消息
async def handle_message(websocket, message):

    msg = json.loads(message)

    logging.info(f"处理消息: {msg}")

    # 处理事件
    if "post_type" in msg:
        if msg["post_type"] == "message":
            # 处理消息事件
            await handle_message_event(websocket, msg)
        elif msg["post_type"] == "notice":
            # 处理通知事件
            await handle_notice_event(websocket, msg)
        elif msg["post_type"] == "request":
            # 处理请求事件
            await handle_request_event(websocket, msg)
        elif msg["post_type"] == "meta_event":
            # 处理元事件
            await handle_meta_event(websocket, msg)
            # 处理定时任务，每个心跳周期检查一次
            await handle_cron_task(websocket)

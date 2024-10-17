# handlers/message_handler.py


import json
import logging
import os
import sys
import asyncio
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 表情生成器
from app.scripts.ImageGenerate.main import handle_ImageGenerate_group_message

# 群发消息
from app.scripts.SendAll.main import handle_SendAll_group_message

# 群管系统
from app.scripts.GroupManager.main import handle_GroupManager_group_message

# 编解码
from app.scripts.Crypto.main import (
    handle_crypto_group_message,
    handle_crypto_private_message,
)

# 工具
from app.scripts.Tools.main import (
    handle_group_message as handle_tools_group_message,
    handle_private_message as handle_tools_private_message,
)

# ai对话
from app.scripts.AI.main import handle_ai_group_message

# 知识库
from app.scripts.QASystem.main import handle_qasystem_message_group

# 天气订阅
from app.scripts.WeatherSubscribe.main import (
    handle_WeatherSubscribe_task_Timer,
    handle_WeatherSubscribe_task_Msg,
)

# 课程表
from app.scripts.ClassTable.main import (
    handle_ClassTable_group_message,
    check_and_push_course_schedule,
)

# 关键词回复
from app.scripts.KeywordsReply.main import handle_KeywordsReply_group_message

# 黑名单
from app.scripts.BlacklistSystem.main import (
    handle_blacklist_message_group,
    handle_blacklist_request_event,
    handle_blacklist_group_notice,
)

# 入群欢迎和退群欢送
from app.scripts.WelcomeFarewell.main import (
    handle_WelcomeFarewell_group_notice,
    WelcomeFarewell_manage,
)

# 邀请链
from app.scripts.InviteChain.main import (
    handle_InviteChain_group_message,
    handle_InviteChain_group_notice,
)

# 违禁词
from app.scripts.BanWords.main import handle_BanWords_group_message

# QFNU追踪器
from app.scripts.QFNUTracker.main import (
    start_qfnu_tracker,
    handle_QFNUTracker_group_message,
)

# 群名片锁
from app.scripts.LockGroupCard.main import (
    handle_LockGroupCard_group_message,
)

# 软封禁
from app.scripts.SoftBan.main import SoftBan_main

# 收集阳光
from app.scripts.CollectTheSun.main import handle_CollectTheSun_group_message

# 自定义
from app.scripts.Custom.main import (
    handle_Custom_group_message,
)

# 打断复读
from app.scripts.NoAddOne.main import handle_NoAddOne_group_message

# 总开关
from app.switch import handle_GroupSwitch_group_message

# 菜单
from app.menu import handle_Menu_group_message

# api
from app.api import *

# 配置
from app.config import *


# 处理消息事件的逻辑
async def handle_message_event(websocket, msg):
    try:
        # 处理群消息
        if msg.get("message_type") == "group":

            group_id = msg["group_id"]
            logging.info(f"处理群消息,群ID:{group_id}")

            # 依次执行群消息处理函数
            await handle_SendAll_group_message(websocket, msg)  # 处理群发消息
            await handle_ImageGenerate_group_message(websocket, msg)  # 表情生成器
            await handle_LockGroupCard_group_message(websocket, msg)  # 群名片锁
            await handle_GroupManager_group_message(websocket, msg)  # 群管系统
            await handle_crypto_group_message(websocket, msg)  # 编解码功能
            await handle_tools_group_message(websocket, msg)  # 实用的API工具功能
            await handle_qasystem_message_group(websocket, msg)  # 处理知识库问答系统
            await handle_KeywordsReply_group_message(websocket, msg)  # 处理关键词回复
            await handle_blacklist_message_group(websocket, msg)  # 处理黑名单系统
            await handle_GroupSwitch_group_message(websocket, msg)  # 处理群组开关
            await handle_BanWords_group_message(websocket, msg)  # 处理违禁词系统
            await WelcomeFarewell_manage(websocket, msg)  # 处理入群欢迎和退群欢送的管理
            await handle_Menu_group_message(websocket, msg)  # 处理菜单
            await handle_InviteChain_group_message(websocket, msg)  # 处理邀请链
            await SoftBan_main(websocket, msg)  # 处理软封禁
            await handle_QFNUTracker_group_message(
                websocket, msg
            )  # 处理QFNU追踪器开关消息
            asyncio.create_task(handle_ai_group_message(websocket, msg))  # 处理ai群消息
            await handle_Custom_group_message(websocket, msg)  # 处理自定义群消息
            await handle_CollectTheSun_group_message(websocket, msg)  # 处理收集阳光
            await handle_NoAddOne_group_message(websocket, msg)  # 处理打断复读
            # await handle_WeatherSubscribe_task_Msg(websocket, msg)  # 处理天气订阅
            await handle_ClassTable_group_message(websocket, msg)  # 处理课程表

        # 处理私聊消息
        elif msg.get("message_type") == "private":
            user_id = msg.get("user_id")
            # 依次执行私聊消息处理函数
            await handle_crypto_private_message(websocket, msg)  # 编解码功能
            await handle_tools_private_message(websocket, msg)  # 实用的API工具功能

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

        await handle_WelcomeFarewell_group_notice(
            websocket, msg
        )  # 处理入群欢迎和退群欢送的管理
        await handle_InviteChain_group_notice(websocket, msg)  # 处理邀请链
        await handle_blacklist_group_notice(websocket, msg)  # 处理黑名单检查


# 处理请求事件的逻辑
async def handle_request_event(websocket, msg):

    await handle_blacklist_request_event(websocket, msg)  # 处理黑名单请求事件


# 处理元事件的逻辑
async def handle_meta_event(websocket, msg):
    pass


# 处理定时任务，每个心跳周期检查一次
async def handle_cron_task(websocket):
    try:
        await start_qfnu_tracker(websocket)
        await handle_WeatherSubscribe_task_Timer(websocket)
        await check_and_push_course_schedule(websocket)
    except Exception as e:
        logging.error(f"处理定时任务的逻辑错误: {e}")


# 处理ws消息
async def handle_message(websocket, message):

    msg = json.loads(message)

    # 排除回应消息
    if msg.get("status") == "ok":
        return

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

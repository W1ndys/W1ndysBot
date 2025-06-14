# handlers/message_handler.py


import json
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入在线监测模块
from app.core.online_detect import Online_detect_manager

# 统一从各模块导入事件处理器

from app.scripts.ClassTable.main import handle_events as handle_ClassTable_events


from app.scripts.Custom.main import handle_events as handle_Custom_events
from app.scripts.TimeAwareGreetings.main import (
    handle_events as handle_TimeAwareGreetings_events,
)


from app.scripts.LLM.main import handle_events as handle_LLM_events
from app.scripts.QFNUEatWhat.main import handle_events as handle_QFNUEatWhat_events
from app.scripts.QFNUGetFreeClassrooms.main import (
    handle_events as handle_QFNUGetFreeClassrooms_events,
)

from app.scripts.QFNUNoticeMonitor.main import (
    handle_events as handle_QFNUNoticeMonitor_events,
)
from app.scripts.FunnySayings.main import handle_events as handle_FunnySayings_events
from app.scripts.QFNUElectricityQuery.main import (
    handle_events as handle_QFNUElectricityQuery_events,
)

from app.scripts.GunRouletteGame.main import (
    handle_events as handle_GunRouletteGame_events,
)
from app.scripts.HaiXian.main import handle_events as handle_HaiXian_events

# 系统模块
from app.system import handle_events as handle_System_events
from app.switch import handle_events as handle_Switch_events


# 处理ws消息
async def handle_message(websocket, message):
    try:
        msg = json.loads(message)

        logging.info(f"\n收到ws事件：\n{msg}\n")

        # 系统基础功能
        await handle_System_events(websocket, msg)
        await handle_Switch_events(websocket, msg)

        # 在线监测模块
        await Online_detect_manager.handle_events(websocket, msg)

        await handle_GunRouletteGame_events(websocket, msg)
        await handle_Custom_events(websocket, msg)
        await handle_QFNUGetFreeClassrooms_events(websocket, msg)
        await handle_QFNUElectricityQuery_events(websocket, msg)
        await handle_FunnySayings_events(websocket, msg)
        await handle_HaiXian_events(websocket, msg)
        await handle_QFNUEatWhat_events(websocket, msg)
        await handle_ClassTable_events(websocket, msg)
        await handle_TimeAwareGreetings_events(websocket, msg)
        await handle_LLM_events(websocket, msg)
        await handle_QFNUNoticeMonitor_events(websocket, msg)

    except Exception as e:
        logging.error(f"处理ws消息的逻辑错误: {e}")

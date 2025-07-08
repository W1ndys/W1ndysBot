import logger
from config import OWNER_ID
from api.group import get_group_list
from api.message import send_private_msg
import re
import os
import json
import time

last_request_time = 0
REQUEST_INTERVAL = 600  # 10分钟，单位：秒


async def handle_events(websocket, msg):
    """
    处理回应事件
    响应示例:
    {
      "status": "ok",  // 状态，"ok"表示成功
      "retcode": 0,    // 返回码，0通常表示成功
      "data": [        // 包含多个群组信息的数组
        {
          "group_all_shut": 0,         // 群禁言状态，0表示未全员禁言，1表示已全员禁言，-1表示未知或不适用（例如，比赛群可能不会有传统禁言）
          "group_remark": "",          // 群备注名
          "group_id": "********",      // 群号 (已脱敏)
          "group_name": "********",    // 群名称 (已脱敏)
          "member_count": 41,          // 当前群成员数量
          "max_member_count": 200      // 群最大成员数量限制
        }
      ],
      "message": "",               // 状态消息，通常在出错时包含错误信息
      "wording": "",               // 补充信息或提示
      "echo": null                 // 回显字段，通常用于请求和响应的匹配
    }
    """
    global last_request_time
    try:
        current_time = int(time.time())
        # 检查距离上次请求是否已超过10分钟
        if current_time - last_request_time >= REQUEST_INTERVAL:
            # 发送nc_get_rkey请求
            await get_group_list(websocket, no_cache=True)
            last_request_time = current_time

        if msg.get("status") == "ok":
            echo = msg.get("echo", "")
            pass
    except Exception as e:
        logger.error(f"获取群列表失败: {e}")
        await send_private_msg(websocket, OWNER_ID, f"获取群列表失败: {e}")

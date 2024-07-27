import json
import logging

# 配置
owner = 2769731875  # 机器人管理员 QQ 号

logging.basicConfig(level=logging.DEBUG)


async def handle_message(websocket, message):
    msg = json.loads(message)

    # 检查消息类型和内容
    if msg.get("post_type") == "message" and msg.get("message_type") == "group":
        logging.debug(f"[test.py] 收到群消息: {msg}")
        user_id = msg["user_id"]
        group_id = msg["group_id"]
        raw_message = msg.get("raw_message", "")

        # 检查是否为主人发送的"测试"消息
        if user_id == owner and raw_message == "测试":
            logging.debug("[test.py] 收到主人的测试消息.")
            await send_message(websocket, group_id, "测试成功")


async def send_message(websocket, group_id, content):
    message = {
        "action": "send_group_msg",
        "params": {"group_id": group_id, "message": content},
    }
    await websocket.send(json.dumps(message))
    logging.info(f"[test.py] 已发送消息: {content} 到群 {group_id}.")

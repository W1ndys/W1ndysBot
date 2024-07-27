import json
import logging
import asyncio
import websockets

# 配置
ws_url = "ws://127.0.0.1:3001"  # napcatQQ 的 WebSocket API 地址
token = None  # 如果需要认证，请填写认证 token
owner = 2769731875  # 机器人管理员 QQ 号

logging.basicConfig(level=logging.DEBUG)


async def handle_message(websocket, message):
    msg = json.loads(message)

    # 检查消息类型和内容
    if msg.get("post_type") == "message" and msg.get("message_type") == "group":
        logging.debug(f"收到群消息: {msg}")
        user_id = msg["user_id"]
        group_id = msg["group_id"]
        raw_message = msg.get("raw_message", "")

        # 检查是否为主人发送的"测试"消息
        if user_id == owner and raw_message == "测试":
            logging.debug("收到主人的测试消息.")
            await send_message(websocket, group_id, "测试成功")


async def send_message(websocket, group_id, content):
    message = {
        "action": "send_group_msg",
        "params": {"group_id": group_id, "message": content},
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已发送消息: {content} 到群 {group_id}.")


async def run(websocket):
    async for message in websocket:
        logging.debug(f"收到消息: {message}")
        await handle_message(websocket, message)

import asyncio
import websockets
import json
import logging

# 配置日志输出
logging.basicConfig(level=logging.DEBUG)

# 配置你的napcatQQ机器人信息
ws_url = "ws://127.0.0.1:3001"
group_id = 728077087
token = ""  # 如果不需要token认证，可以留空

# 定义关键词和回复内容的字典
keyword_responses = {
    # "测试": "测试成功",
    "你好": "你好，有什么可以帮你的吗？",
    "帮助": "请描述你的问题，我们会尽力帮你解决。",
    "带回车的测试": """带回车
的测试成功""",
}


async def connect_to_bot():
    logging.info("Connecting to bot...")
    async with websockets.connect(ws_url) as websocket:
        logging.info("Connected to bot.")
        # 发送认证信息，如果需要的话
        await authenticate(websocket)

        async for message in websocket:
            logging.debug(f"Received message: {message}")
            await handle_message(websocket, message)


async def authenticate(websocket):
    if token:
        auth_message = {"action": "authenticate", "params": {"token": token}}
        await websocket.send(json.dumps(auth_message))
        logging.info("Sent authentication message.")
    else:
        logging.info("No token provided, skipping authentication.")


async def handle_message(websocket, message):
    msg = json.loads(message)

    # 检查消息类型和内容
    if msg.get("post_type") == "message" and msg.get("message_type") == "group":
        if msg["group_id"] == group_id:
            raw_message = msg.get("raw_message", "")
            logging.debug(f"Group message received: {raw_message}")
            response = get_response(raw_message)
            if response:
                logging.info(f"Sending response: {response}")
                await send_message(websocket, msg["group_id"], response)


def get_response(message):
    for keyword, response in keyword_responses.items():
        if keyword in message:
            logging.debug(f"Keyword '{keyword}' matched with message '{message}'")
            return response
    return None


async def send_message(websocket, group_id, content):
    message = {
        "action": "send_group_msg",
        "params": {"group_id": group_id, "message": content},
    }
    await websocket.send(json.dumps(message))
    logging.info(f"Message sent to group {group_id}: {content}")


# 主函数
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_to_bot())

import json
import logging
import asyncio
import websockets
import re

# 全局配置
global owner, ws_url, token, forbidden_words_file, warning_message, enabled_groups

owner = 2769731875  # 机器人管理员 QQ 号
ws_url = "ws://127.0.0.1:3001"  # napcatQQ 的 WebSocket API 地址
token = None  # 如果需要认证，请填写认证 token

warning_message = "警告：请不要发送违禁词！"  # 警告消息

enabled_groups_file = (
    "forbidden_word_detector/enabled_groups.txt"  # 启用的群聊群号文件路径
)

forbidden_words_file = "forbidden_word_detector/forbidden_words.txt"  # 违禁词文件路径


# 加载违禁词列表
async def load_forbidden_words(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        patterns = [line.strip() for line in file if line.strip()]
    logging.info(f"加载的违禁词: {patterns}")
    return patterns


# 加载开启违禁词检测的群聊群号
async def load_enabled_groups(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        groups = [int(line.strip()) for line in file if line.strip()]
    return groups


logging.basicConfig(level=logging.DEBUG)


# 连接到 QQ 机器人
async def connect_to_bot():
    logging.info("正在连接到机器人...")
    async with websockets.connect(ws_url) as websocket:
        logging.info("已连接到机器人。")
        # 发送认证信息，如果需要的话
        await authenticate(websocket)

        async for message in websocket:
            logging.debug(f"收到消息: {message}")
            await handle_message(websocket, message)


# 发送认证信息
async def authenticate(websocket):
    if token:
        auth_message = {"action": "authenticate", "params": {"token": token}}
        await websocket.send(json.dumps(auth_message))
        logging.info("已发送认证信息。")
    else:
        logging.info("未提供 token，跳过认证。")


# 处理消息
async def handle_message(websocket, message):

    msg = json.loads(message)
    if msg["post_type"] == "meta_event":
        logging.debug(f"心跳包事件: {msg}")
    else:
        # 获取消息相关信息
        user_id = msg["sender"]["user_id"]
        group_id = msg["group_id"]
        message_id = msg["message_id"]

        raw_message = msg.get("raw_message", "")

        # 检查是否为主人发送的"测试"消息
        if user_id == owner and raw_message == "测试":
            logging.debug("[test.py] 收到主人的测试消息。")
            await send_message(websocket, group_id, "测试成功")

        # 检查消息类型和内容
        if msg.get("post_type") == "message" and msg.get("message_type") == "group":
            logging.debug(f"收到群消息: {msg}")

            group_id = msg["group_id"]
            message_id = msg["message_id"]
            raw_message = msg.get("raw_message", "")

            # 检查群号是否在启用列表中
            if group_id in enabled_groups:
                logging.debug(f"群 {group_id} 已启用违禁词检测。")
                # 检测违禁词
                if any(
                    re.search(pattern, raw_message) for pattern in forbidden_patterns
                ):
                    logging.debug(f"在消息中检测到违禁词: {raw_message}")

                    # 撤回消息
                    await delete_message(websocket, message_id)

                    # 发送警告消息
                    await send_message(websocket, group_id, warning_message)
            else:
                logging.debug(f"群 {group_id} 未启用违禁词检测。")


# 撤回消息
async def delete_message(websocket, message_id):
    delete_msg = {
        "action": "delete_msg",
        "params": {"message_id": message_id},
    }
    await websocket.send(json.dumps(delete_msg))
    logging.info(f"消息 {message_id} 已删除。")


# 发送消息
async def send_message(websocket, group_id, content):
    message = {
        "action": "send_group_msg",
        "params": {"group_id": group_id, "message": content},
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已发送消息到群 {group_id}: {content}")


# 主函数
async def main():
    global enabled_groups, forbidden_patterns
    enabled_groups = await load_enabled_groups(
        enabled_groups_file
    )  # 加载启用的群聊群号
    forbidden_patterns = await load_forbidden_words(
        forbidden_words_file
    )  # 加载违禁词列表
    await connect_to_bot()


if __name__ == "__main__":
    asyncio.run(main())

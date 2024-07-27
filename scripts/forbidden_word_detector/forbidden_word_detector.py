import json
import logging
import re
import os

# 配置
module_dir = os.path.dirname(__file__)
forbidden_words_file = os.path.join(module_dir, "forbidden_words.txt")  # 违禁词文件路径
warning_message = "警告：请不要发送违禁词！"
enabled_groups = [728077087, 236562801, 781550983]  # 需要开启检测功能的群聊群号

logging.basicConfig(level=logging.DEBUG)


def load_forbidden_words(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        patterns = [line.strip() for line in file if line.strip()]
    return patterns


async def handle_message(websocket, message, forbidden_patterns):
    msg = json.loads(message)

    # 检查消息类型和内容
    if msg.get("post_type") == "message" and msg.get("message_type") == "group":
        logging.debug(f"收到群消息: {msg}")
        user_id = msg["user_id"]
        group_id = msg["group_id"]
        message_id = msg["message_id"]
        raw_message = msg.get("raw_message", "")

        # 检查群号是否在启用列表中
        if group_id in enabled_groups:
            logging.debug(f"群 {group_id} 已开启检测功能.")
            # 检测违禁词
            if any(re.search(pattern, raw_message) for pattern in forbidden_patterns):
                logging.debug(f"发现违禁词: {raw_message}")

                await set_group_ban(websocket, group_id, user_id, 60 * 5)

                # 撤回消息
                await delete_message(websocket, message_id)

                warning_message = f"警告：群 {group_id} 的用户 {user_id} 发送的消息包含违禁词！请注意言行！"

                # 发送警告消息
                await send_message(websocket, group_id, warning_message)
        else:
            logging.debug(f"群 {group_id} 未开启检测功能，忽略该消息.")


async def set_group_ban(websocket, group_id, user_id, duration):
    ban_msg = {
        "action": "set_group_ban",
        "params": {"group_id": group_id, "user_id": user_id, "duration": duration},
    }
    await websocket.send(json.dumps(ban_msg))
    logging.info(f"User {user_id} banned from group {group_id} for {duration} seconds.")


async def delete_message(websocket, message_id):
    delete_msg = {
        "action": "delete_msg",
        "params": {"message_id": message_id},
    }
    await websocket.send(json.dumps(delete_msg))
    logging.info(f"消息 {message_id} 已撤回.")


async def send_message(websocket, group_id, content):
    message = {
        "action": "send_group_msg",
        "params": {"group_id": group_id, "message": content},
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已发送消息: {content} 到群 {group_id}.")


async def run(websocket):
    forbidden_patterns = load_forbidden_words(forbidden_words_file)
    async for message in websocket:
        logging.debug(f"收到消息: {message}")
        await handle_message(websocket, message, forbidden_patterns)

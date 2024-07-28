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
    logging.info(f"加载的启用的群聊群号: {groups}")
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


import json
import re
import logging


# 处理消息
async def handle_message(websocket, message):
    msg = json.loads(message)

    logging.debug(f"\n\n{msg}\n\n")

    # 处理心跳包
    if "post_type" in msg and msg["post_type"] == "meta_event":
        logging.debug(f"心跳包事件: {msg}")

    # 处理群聊消息
    elif (
        "post_type" in msg
        and msg["post_type"] == "message"
        and msg["message_type"] == "group"
    ):
        user_id = msg["sender"]["user_id"]
        group_id = msg["group_id"]
        message_id = msg["message_id"]
        raw_message = msg["raw_message"]

        # 检查是否为主人发送的"测试"消息
        if user_id == owner and raw_message == "测试":
            logging.debug("收到主人的测试消息。")
            await send_message(websocket, group_id, "测试成功")

        # 禁言命令
        if user_id == owner and re.match(r"ban.*", raw_message):
            logging.debug("收到主人的禁言消息。")
            ban_qq = None
            ban_duration = None

            # 遍历message列表，查找type为'at'的项并读取qq字段
            for i, item in enumerate(msg["message"]):
                if item["type"] == "at":
                    ban_qq = item["data"]["qq"]
                    # 检查下一个元素是否存在且类型为'text'
                    if (
                        i + 1 < len(msg["message"])
                        and msg["message"][i + 1]["type"] == "text"
                    ):
                        ban_duration = int(
                            msg["message"][i + 1]["data"]["text"].strip()
                        )
                    break

            if ban_qq and ban_duration:
                await set_group_ban(websocket, group_id, ban_qq, ban_duration * 60)

        # 解除禁言命令
        if user_id == owner and re.match(r"unban.*", raw_message):
            logging.debug("收到主人的解除禁言消息。")
            unban_qq = None

            # 遍历message列表，查找type为'at'的项并读取qq字段
            for i, item in enumerate(msg["message"]):
                if item["type"] == "at":
                    unban_qq = item["data"]["qq"]
                    break

            if unban_qq:
                await set_group_ban(websocket, group_id, unban_qq, 0)

        # 撤回消息命令
        if user_id == owner and "recall" in raw_message:
            logging.debug("收到主人的撤回消息命令。")
            message_id = int(msg["message"][0]["data"]["id"])
            await delete_message(websocket, message_id)

        # 检查群号是否在启用列表中
        if group_id in enabled_groups:
            logging.debug(f"群 {group_id} 启用了违禁词检测。")
            # 检测违禁词
            if any(re.search(pattern, raw_message) for pattern in forbidden_patterns):
                logging.debug(f"在消息中检测到违禁词: {raw_message}")

                # 撤回消息
                await delete_message(websocket, message_id)

                # 发送警告消息
                await send_message(websocket, group_id, warning_message)

                # 执行禁言
                await set_group_ban(websocket, group_id, user_id, 60)
    else:
        logging.debug(f"收到消息: {msg}")


# 禁言用户
async def set_group_ban(websocket, group_id, user_id, duration):
    ban_msg = {
        "action": "set_group_ban",
        "params": {"group_id": group_id, "user_id": user_id, "duration": duration},
    }
    await websocket.send(json.dumps(ban_msg))
    logging.info(f"已禁止用户 {user_id} {duration} 秒。")


# 撤回消息
async def delete_message(websocket, message_id):
    delete_msg = {
        "action": "delete_msg",
        "params": {"message_id": message_id},
    }
    await websocket.send(json.dumps(delete_msg))
    logging.info(f"消息 {message_id} 已撤回。")


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

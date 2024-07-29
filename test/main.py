import json
import logging
import asyncio
import websockets
import re
import colorlog

# 全局配置
global owner_id, ws_url, token, test_group_id, forbidden_words_patterns, forbidden_words_enabled_groups, admin_id

owner_id = [2769731875]  # 机器人管理员 QQ 号
ws_url = "ws://127.0.0.1:3001"  # napcatQQ 监听的 WebSocket API 地址
token = None  # 如果需要认证，请填写认证 token
test_group_id = 728077087  # 测试群群号
forbidden_words_file = "forbidden_config/forbidden_words.txt"
forbidden_words_enabled_groups_file = "forbidden_config/enable_groups.txt"
admin_id_file = "admin/admin_id.txt"  # 管理员 QQ 号文件


# 加载违禁词列表
async def load_forbidden_words(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        patterns = [line.strip() for line in file if line.strip()]
    logging.info(f"加载的违禁词: {patterns}")
    return patterns


# 加载开启违禁词检测的群聊群号
async def load_forbidden_words_enabled_groups(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        groups = [int(line.strip()) for line in file if line.strip()]
    logging.info(f"加载的启用的群聊群号: {groups}")
    return groups


# 加载管理员 QQ 号
async def load_admin_id(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        admin_id = [int(line.strip()) for line in file if line.strip()]
    logging.info(f"加载的管理员 QQ 号: {admin_id}")
    return admin_id


# 加载配置文件
async def load_config():
    global forbidden_words_enabled_groups, forbidden_words_patterns, admin_id
    forbidden_words_enabled_groups = await load_forbidden_words_enabled_groups(
        forbidden_words_enabled_groups_file
    )  # 加载启用的群聊群号
    forbidden_words_patterns = await load_forbidden_words(
        forbidden_words_file
    )  # 加载违禁词列表
    admin_id = await load_admin_id(admin_id_file)  # 加载管理员 QQ 号


# 日志等级配置
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s:%(name)s:%(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "light_green",  # 使用更亮的绿色
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
)
logging.basicConfig(level=logging.DEBUG, handlers=[handler])


# 连接到 QQ 机器人
async def connect_to_bot():
    logging.info("正在连接到机器人...")
    async with websockets.connect(ws_url) as websocket:
        logging.info("已连接到机器人。")
        # 发送认证信息，如果需要的话
        await authenticate(websocket)

        async for message in websocket:
            # logging.info(f"收到消息: {message}")
            await handle_message(websocket, message)


# 发送认证信息
async def authenticate(websocket):
    if token:
        auth_message = {"action": "authenticate", "params": {"token": token}}
        await websocket.send(json.dumps(auth_message))
        logging.info("已发送认证信息。")
    else:
        logging.info("未提供 token，跳过认证。")


# 发送群消息
async def send_group_msg(websocket, group_id, content):
    message = {
        "action": "send_group_msg",
        "params": {"group_id": group_id, "message": content},
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已发送消息到群 {group_id}: {content}")


# 群发消息
async def send_group_msgs(websocket, group_ids, content):
    for group_id in group_ids:
        await send_group_msg(websocket, group_id, content)


# 发送消息
async def send_msg(websocket, message_type, user_id, group_id, message):
    message = {
        "action": "send_msg",
        "params": {
            "message_type": message_type,
            "user_id": user_id,
            "group_id": group_id,
            "message": message,
        },
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已发送消息: {message}")


# 禁言
async def set_group_ban(websocket, group_id, user_id, duration):
    message = {
        "action": "set_group_ban",
        "params": {
            "group_id": group_id,
            "user_id": user_id,
            "duration": duration,
        },
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已禁言用户 {user_id} 在群 {group_id} 中 {duration} 秒")


# 解禁
async def unban(websocket, group_id, user_id):
    await set_group_ban(websocket, group_id, user_id, 0)
    logging.info(f"已解除用户 {user_id} 在群 {group_id} 中的禁言")


# 全员禁言
async def mute_all_members(websocket, group_id):
    message = {
        "action": "set_group_whole_ban",
        "params": {
            "group_id": group_id,
            "enable": True,
        },
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已在群 {group_id} 中开启全员禁言")


# 解除全员禁言
async def unmute_all_members(websocket, group_id):
    message = {
        "action": "set_group_whole_ban",
        "params": {
            "group_id": group_id,
            "enable": False,
        },
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已在群 {group_id} 中解除全员禁言")


# 踢出群成员
async def kick_member(websocket, group_id, user_id):
    message = {
        "action": "set_group_kick",
        "params": {
            "group_id": group_id,
            "user_id": user_id,
            "reject_add_request": False,  # 是否拒绝此人再次加群
        },
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已将用户 {user_id} 踢出群 {group_id}")


# 处理消息
async def handle_message(websocket, message):
    try:
        msg = json.loads(message)
        # logging.info(f"\n收到消息:\n{msg}\n\n")

        # 处理心跳包
        if "post_type" in msg and msg["post_type"] == "meta_event":
            logging.info(f"心跳包事件: {msg}")

        # 处理群聊消息
        elif (
            "post_type" in msg
            and msg["post_type"] == "message"
            and msg["message_type"] == "group"
            and msg["group_id"]
            in forbidden_words_enabled_groups  # 仅处理启用违禁词检测的群
        ):
            logging.info(f"\n\n收到消息:\n{msg}\n\n")
            user_id = msg["sender"]["user_id"]
            group_id = msg["group_id"]
            message_id = msg["message_id"]
            raw_message = msg["raw_message"]

            # 检查是否为管理员发送的"测试"消息
            if (user_id in owner_id or user_id in admin_id) and (
                raw_message == "测试" or raw_message == "test"
            ):
                logging.info("收到管理员的测试消息。")
                await send_group_msg(websocket, group_id, "测试成功")

            # 提取被@的用户ID
            mentioned_users = re.findall(r"\[CQ:at,qq=(\d+)\]", msg["raw_message"])

            # 添加管理员
            if user_id in owner_id and "add-admin" in raw_message:
                if mentioned_users:
                    new_admin_id = int(mentioned_users[0])
                    if new_admin_id not in admin_id:
                        admin_id.append(new_admin_id)
                        with open(admin_id_file, "w", encoding="utf-8") as file:
                            file.write("\n".join(map(str, admin_id)))
                        await send_group_msg(
                            websocket, group_id, f"添加管理员成功: {new_admin_id}"
                        )
                        await load_admin_id(admin_id_file)
                    else:
                        await send_group_msg(
                            websocket, group_id, f"管理员 {new_admin_id} 已存在"
                        )

            # 移除管理员
            if user_id in owner_id and "del-admin" in raw_message:
                if mentioned_users:
                    remove_admin_id = int(mentioned_users[0])
                    if remove_admin_id in admin_id:
                        admin_id.remove(remove_admin_id)
                        with open(admin_id_file, "w", encoding="utf-8") as file:
                            file.write("\n".join(map(str, admin_id)))
                        await send_group_msg(
                            websocket,
                            group_id,
                            f"移除管理员成功: {remove_admin_id}",
                        )
                        await load_admin_id(admin_id_file)
                    else:
                        await send_group_msg(
                            websocket, group_id, f"管理员 {remove_admin_id} 不存在"
                        )

            # 违禁词检测
            for word in forbidden_words_patterns:
                if word in raw_message:
                    await send_group_msg(websocket, group_id, f"检测到违禁词: {word}")
                    await set_group_ban(websocket, group_id, user_id, 60)  # 禁言 60 秒
                    break

            # 禁言命令
            if (user_id in owner_id or user_id in admin_id) and re.match(
                r"ban.*", raw_message
            ):
                logging.info("收到管理员的禁言消息。")
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

                if ban_duration is None:
                    ban_duration = 1  # 默认禁言 1 分钟

                if ban_qq and ban_duration:
                    await set_group_ban(websocket, group_id, ban_qq, ban_duration * 60)

            # 解除禁言命令
            if (user_id in owner_id or user_id in admin_id) and re.match(
                r"unban.*", raw_message
            ):
                logging.info("收到管理员的解除禁言消息。")
                unban_qq = None

                # 遍历message列表，查找type为'at'的项并读取qq字段
                for i, item in enumerate(msg["message"]):
                    if item["type"] == "at":
                        unban_qq = item["data"]["qq"]
                        break

                if unban_qq:
                    await set_group_ban(websocket, group_id, unban_qq, 0)

            # 全员禁言
            if (user_id in owner_id or user_id in admin_id) and "banall" in raw_message:
                await mute_all_members(websocket, group_id)
                await send_group_msg(websocket, group_id, "已开启全员禁言")

            # 解除全员禁言
            if (
                user_id in owner_id or user_id in admin_id
            ) and "unbanall" in raw_message:
                await unmute_all_members(websocket, group_id)
                await send_group_msg(websocket, group_id, "已解除全员禁言")

            # 踢出群成员
            if (user_id in owner_id or user_id in admin_id) and "踢出群" in raw_message:
                if mentioned_users:
                    kick_user_id = int(mentioned_users[0])
                    await kick_member(websocket, group_id, kick_user_id)
                    await send_group_msg(
                        websocket, group_id, f"已将用户 {kick_user_id} 踢出群"
                    )

        # 处理私聊消息
        elif "post_type" in msg and msg["message_type"] == "private":  # 私聊消息
            user_id = msg["sender"]["user_id"]
            message_id = msg["message_id"]
            raw_message = msg["raw_message"]
            logging.info(f"收到私聊消息: {raw_message}")

        # 其他消息类型
        else:
            # logging.info(f"收到消息: {msg}")
            pass

    # 处理异常
    except Exception as e:
        logging.error(f"处理消息时出错: {e}")


# 主函数
async def main():
    await load_config()  # 加载配置文件
    await connect_to_bot()  # 连接到 QQ 机器人


if __name__ == "__main__":
    asyncio.run(main())

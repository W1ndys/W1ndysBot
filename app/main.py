import json
import logging
import asyncio
import websockets
import re
import colorlog

# 全局配置
global owner, ws_url, token, forbidden_words_file, warning_message, forbidden_words_enabled_groups

owner = [2769731875, 1044420589]  # 机器人管理员 QQ 号
ws_url = "ws://127.0.0.1:3001"  # napcatQQ 监听的 WebSocket API 地址
token = None  # 如果需要认证，请填写认证 token

warning_message = "警告：请不要发送违禁词！\n视频形式的广告检测难度大，请及时联系管理员处理。\n如有误删是发的内容触发了违禁词，请及时联系管理员处理。\n有新的事件被处理了，请查看是否正常处理[CQ:at,qq=2769731875]"  # 警告消息

forbidden_words_enabled_groups_file = "forbidden_word_detector/forbidden_words_enabled_groups.txt"  # 启用的群聊群号文件路径

forbidden_words_file = "forbidden_word_detector/forbidden_words.txt"  # 违禁词文件路径


# 日志等级配置
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s:%(name)s:%(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
)
logging.basicConfig(level=logging.DEBUG, handlers=[handler])


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


# 加载配置文件
async def load_config():
    global forbidden_words_enabled_groups, forbidden_words_patterns
    forbidden_words_enabled_groups = await load_forbidden_words_enabled_groups(
        forbidden_words_enabled_groups_file
    )  # 加载启用的群聊群号
    forbidden_words_patterns = await load_forbidden_words(
        forbidden_words_file
    )  # 加载违禁词列表


# 连接到 QQ 机器人
async def connect_to_bot():
    logging.info("正在连接到机器人...")
    async with websockets.connect(ws_url) as websocket:
        logging.info("已连接到机器人。")
        # 发送认证信息，如果需要的话
        await authenticate(websocket)

        async for message in websocket:
            logging.info(f"收到消息: {message}")
            await handle_message(websocket, message)


# 发送认证信息
async def authenticate(websocket):
    if token:
        auth_message = {"action": "authenticate", "params": {"token": token}}
        await websocket.send(json.dumps(auth_message))
        logging.info("已发送认证信息。")
    else:
        logging.info("未提供 token，跳过认证。")


# 发送私聊消息
async def send_private_msg(websocket, user_id, content):
    message = {
        "action": "send_private_msg",
        "params": {"user_id": user_id, "message": content},
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已发送消息到用户 {user_id}: {content}")


# 发送群消息
async def send_group_msg(websocket, group_id, content):
    message = {
        "action": "send_group_msg",
        "params": {"group_id": group_id, "message": content},
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已发送消息到群 {group_id}: {content}")


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


# 撤回消息
async def delete_msg(websocket, message_id):
    delete_msg = {
        "action": "delete_msg",
        "params": {"message_id": message_id},
    }
    await websocket.send(json.dumps(delete_msg))
    logging.info(f"消息 {message_id} 已撤回。")


# 获取消息
async def get_msg(websocket, message_id):
    get_msg = {
        "action": "get_msg",
        "params": {"message_id": message_id},
    }
    await websocket.send(json.dumps(get_msg))
    logging.info(f"已获取消息 {message_id}。")


# 获取合并转发消息
async def get_forward_msg(websocket, id):
    get_forward_msg = {
        "action": "get_forward_msg",
        "params": {"message_id": id},
    }
    await websocket.send(json.dumps(get_forward_msg))
    logging.info(f"已获取合并转发消息 {id}。")


# 发送好友赞
async def send_like(websocket, user_id, times):
    like_msg = {
        "action": "send_like",
        "params": {"user_id": user_id, "times": times},
    }
    await websocket.send(json.dumps(like_msg))
    logging.info(f"已发送好友赞 {user_id} {times} 次。")


# 群组踢人
async def set_group_kick(websocket, group_id, user_id):
    kick_msg = {
        "action": "set_group_kick",
        "params": {"group_id": group_id, "user_id": user_id},
    }
    await websocket.send(json.dumps(kick_msg))
    logging.info(f"已踢出用户 {user_id}。")
    await send_group_msg(websocket, group_id, f"已踢出用户 {user_id}。")


# 群组单人禁言
async def set_group_ban(websocket, group_id, user_id, duration):
    ban_msg = {
        "action": "set_group_ban",
        "params": {"group_id": group_id, "user_id": user_id, "duration": duration},
    }
    await websocket.send(json.dumps(ban_msg))
    logging.info(f"已禁止用户 {user_id} {duration} 秒。")


# 群组匿名用户禁言
# 此功能需要从群消息上报的数据中获得数据，暂未测试，慎用
# 此功能需要从群消息上报的数据中获得数据，暂未测试，慎用
# 此功能需要从群消息上报的数据中获得数据，暂未测试，慎用
# 此功能需要从群消息上报的数据中获得数据，暂未测试，慎用
# 此功能需要从群消息上报的数据中获得数据，暂未测试，慎用
async def set_group_anonymous_ban(websocket, group_id, anonymous_flag, duration):
    anonymous_ban_msg = {
        "action": "set_group_anonymous_ban",
        "params": {"group_id": group_id, "flag": anonymous_flag, "duration": duration},
    }
    await websocket.send(json.dumps(anonymous_ban_msg))
    logging.info(f"已禁止匿名用户 {anonymous_flag} {duration} 秒。")


# 群组全员禁言
async def set_group_whole_ban(websocket, group_id, enable):
    whole_ban_msg = {
        "action": "set_group_whole_ban",
        "params": {"group_id": group_id, "enable": enable},
    }
    await websocket.send(json.dumps(whole_ban_msg))
    await send_group_msg(
        websocket,
        group_id,
        f"已{'开启' if enable else '解除'}群 {group_id} 的全员禁言。",
    )
    logging.info(f"已{'开启' if enable else '解除'}群 {group_id} 的全员禁言。")


# 群组设置管理员
async def set_group_admin(websocket, group_id, user_id, enable):
    admin_msg = {
        "action": "set_group_admin",
        "params": {"group_id": group_id, "user_id": user_id, "enable": enable},
    }
    await websocket.send(json.dumps(admin_msg))
    logging.info(
        f"已{'授予' if enable else '解除'}群 {group_id} 的管理员 {user_id} 的权限。"
    )


# 群组匿名
async def set_group_anonymous(websocket, group_id, enable):
    anonymous_msg = {
        "action": "set_group_anonymous",
        "params": {"group_id": group_id, "enable": enable},
    }
    await websocket.send(json.dumps(anonymous_msg))
    logging.info(f"已{'开启' if enable else '关闭'}群 {group_id} 的匿名。")


# 解析并执行命令
async def execute_command(websocket, action, params):
    try:
        params_json = json.loads(params)

        if not action:
            logging.error("无效的命令: 缺少 action")
            return

        logging.info(f"即将执行API命令: {action} {params_json}")
        await run_api(websocket, action, params_json)
    except json.JSONDecodeError:
        logging.error("参数解析失败: 无效的 JSON 格式")
    except Exception as e:
        logging.error(f"执行命令时出错: {e}")


# 执行API调用
async def run_api(websocket, action, params):
    api_message = {"action": action, "params": params}
    await websocket.send(json.dumps(api_message))
    logging.info(f"已调用 API {action}。")


async def handle_message(websocket, message):
    try:
        msg = json.loads(message)
        logging.info(f"\n\n{msg}\n\n")

        # 处理心跳包
        if "post_type" in msg and msg["post_type"] == "meta_event":
            logging.info(f"心跳包事件: {msg}")

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

            # 检查是否为管理员发送的"测试"消息
            if user_id in owner and (raw_message == "测试" or raw_message == "test"):
                logging.info("收到管理员的测试消息。")
                await send_group_msg(websocket, group_id, "测试成功")

            # 全员禁言命令
            if user_id in owner and (
                re.match(r"全员禁言.*", raw_message)
                or re.match(r"ban-all.*", raw_message)
            ):
                logging.info("收到管理员的全员禁言消息。")
                await set_group_whole_ban(websocket, group_id, True)  # 全员禁言

            # 全员解禁命令
            if user_id in owner and (
                re.match(r"全员解禁.*", raw_message)
                or re.match(r"unban-all.*", raw_message)
            ):
                logging.info("收到管理员的全员解禁消息。")
                await set_group_whole_ban(websocket, group_id, False)  # 全员解禁

            # 踢人命令
            if user_id in owner and (
                re.match(r"kick.*", raw_message)
                or re.match(r"t.*", raw_message)
                or re.match(r"踢.*", raw_message)
            ):
                logging.info("收到管理员的踢人消息。")
                kick_qq = None

                # 遍历message列表，查找type为'at'的项并读取qq字段
                for i, item in enumerate(msg["message"]):
                    if item["type"] == "at":
                        kick_qq = item["data"]["qq"]
                        break

                if kick_qq:
                    await set_group_kick(websocket, group_id, kick_qq)

            # 禁言命令
            if user_id in owner and re.match(r"ban.*", raw_message):
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
            if user_id in owner and re.match(r"unban.*", raw_message):
                logging.info("收到管理员的解除禁言消息。")
                unban_qq = None

                # 遍历message列表，查找type为'at'的项并读取qq字段
                for i, item in enumerate(msg["message"]):
                    if item["type"] == "at":
                        unban_qq = item["data"]["qq"]
                        break

                if unban_qq:
                    await set_group_ban(websocket, group_id, unban_qq, 0)

            # 撤回消息命令
            if user_id in owner and ("recall" in raw_message or "撤回" in raw_message):
                logging.info("收到管理员的撤回消息命令。")
                message_id = int(msg["message"][0]["data"]["id"])
                await delete_msg(websocket, message_id)

            # 检查群号是否在启用列表中
            if group_id in forbidden_words_enabled_groups:
                logging.info(f"群 {group_id} 启用了违禁词检测。")
                # 检测违禁词
                if any(
                    re.search(pattern, raw_message)
                    for pattern in forbidden_words_patterns
                ):
                    logging.info(f"在消息中检测到违禁词: {raw_message}")

                    # 撤回消息
                    await delete_msg(websocket, message_id)

                    # 发送警告消息
                    await send_group_msg(websocket, group_id, warning_message)

                    # 执行禁言
                    await set_group_ban(websocket, group_id, user_id, 60)

        # 处理私聊消息
        elif "post_type" in msg and msg["message_type"] == "private":  # 私聊消息
            user_id = msg["sender"]["user_id"]
            message_id = msg["message_id"]
            raw_message = msg["raw_message"]
            logging.info(f"收到私聊消息: {raw_message}")
            if user_id == 2769731875:  # 机器人管理员
                match = re.search(r"执行API(.*)参数(.*)", raw_message)
                if match:
                    action = match.group(1).strip()  # 提取“执行API:”后面的action
                    params = match.group(2).strip()  # 提取“参数:”后面的params
                    try:
                        # 解析并执行命令
                        await execute_command(websocket, action, params)
                    except Exception as e:
                        logging.error(f"执行命令时出错: {e}")

        # 其他消息类型
        else:
            logging.info(f"收到消息: {msg}")

    # 处理异常
    except Exception as e:
        logging.error(f"处理消息时出错: {e}")


# 主函数
async def main():
    global forbidden_words_enabled_groups, forbidden_words_patterns
    await load_config()  # 加载配置文件
    await connect_to_bot()  # 连接到 QQ 机器人


if __name__ == "__main__":
    asyncio.run(main())

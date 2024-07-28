import json
import logging
import asyncio
import websockets
import re
import colorlog

# 全局配置
global owner, ws_url, token

owner = []  # 机器人管理员 QQ 号
ws_url = ""  # napcatQQ 监听的 WebSocket API 地址
token = None  # 如果需要认证，请填写认证 token


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
            raw_message = msg["raw_message"]

            # 检查是否为管理员发送的"测试"消息
            if user_id in owner and (raw_message == "测试" or raw_message == "test"):
                logging.info("收到管理员的测试消息。")
                await send_group_msg(websocket, group_id, "测试成功")

            # 检查是否包含图片消息
            if "image" in raw_message:
                image_urls = extract_image_urls(raw_message)
                logging.info(f"提取到的图片链接: {image_urls}")
                await send_group_msg(
                    websocket, group_id, f"图片链接: {', '.join(image_urls)}"
                )

        # 处理私聊消息
        elif "post_type" in msg and msg["message_type"] == "private":  # 私聊消息
            user_id = msg["sender"]["user_id"]
            message_id = msg["message_id"]
            raw_message = msg["raw_message"]
            logging.info(f"收到私聊消息: {raw_message}")

            # 检查是否包含图片消息
            if "image" in raw_message:
                image_urls = extract_image_urls(raw_message)
                logging.info(f"提取到的图片链接: {image_urls}")
                await send_msg(
                    websocket,
                    "private",
                    user_id,
                    None,
                    f"图片链接: {', '.join(image_urls)}",
                )

        # 其他消息类型
        else:
            logging.info(f"收到消息: {msg}")

    # 处理异常
    except Exception as e:
        logging.error(f"处理消息时出错: {e}")


# 提取图片链接
def extract_image_urls(raw_message):
    image_urls = re.findall(r"url=([^ ]+)", raw_message)
    return image_urls


# 主函数
async def main():

    await connect_to_bot()  # 连接到 QQ 机器人


if __name__ == "__main__":
    asyncio.run(main())

import json
import logging
import asyncio
import websockets
import colorlog
import requests
import os
from urllib3 import PoolManager
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# 全局配置
global owner, ws_url, token

owner = [2769731875]  # 机器人管理员 QQ 号
ws_url = "ws://127.0.0.1:3001"  # napcatQQ 监听的 WebSocket API 地址
token = None  # 如果需要认证，请填写认证 token
group_status_file = "group_status.txt"  # 保存群解析状态的文件

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

# 记录群解析状态
group_parse_status = {}


# 加载群解析状态
def load_group_status():
    if os.path.exists(group_status_file):
        with open(group_status_file, "r") as f:
            status = {}
            for line in f:
                group_id, parse_status = line.strip().split(":")
                status[int(group_id)] = parse_status == "True"
            logging.info(f"加载的群解析状态: {status}")
            return status
    return {}


# 保存群解析状态
def save_group_status():
    with open(group_status_file, "w") as f:
        for group_id, parse_status in group_parse_status.items():
            f.write(f"{group_id}:{parse_status}\n")


# 自定义TLS适配器
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.check_hostname = False
        context.verify_mode = False
        kwargs["ssl_context"] = context
        self.poolmanager = PoolManager(*args, **kwargs)


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


# 处理消息
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

            # 仅管理员可开启或关闭解析功能
            if user_id in owner:
                if raw_message == "开启解析":
                    group_parse_status[group_id] = True
                    save_group_status()
                    await send_group_msg(websocket, group_id, "解析功能已开启")
                elif raw_message == "关闭解析":
                    group_parse_status[group_id] = False
                    save_group_status()
                    await send_group_msg(websocket, group_id, "解析功能已关闭")
            if group_parse_status.get(group_id, False):
                # 检查是否包含图片
                for segment in msg["message"]:
                    if segment["type"] == "image":
                        image_url = segment["data"]["url"]
                        local_path = "/opt/1panel/apps/openresty/openresty/www/sites/47.104.173.131/index/temp.jpg"
                        save_image_locally(image_url, local_path)
                        decoded_text = decode_qr_code("http://47.104.173.131/temp.jpg")
                        await send_group_msg(
                            websocket,
                            group_id,
                            decoded_text,  # 仅返回解码结果
                        )

        # 处理私聊消息
        elif "post_type" in msg and msg["message_type"] == "private":  # 私聊消息
            user_id = msg["sender"]["user_id"]
            raw_message = msg["raw_message"]
            logging.info(f"收到私聊消息: {raw_message}")

            # 检查是否包含图片
            for segment in msg["message"]:
                if segment["type"] == "image":
                    image_url = segment["data"]["url"]
                    local_path = "/opt/1panel/apps/openresty/openresty/www/sites/47.104.173.131/index/temp.jpg"
                    save_image_locally(image_url, local_path)
                    decoded_text = decode_qr_code("http://47.104.173.131/temp.jpg")
                    await send_msg(
                        websocket,
                        "private",
                        user_id,
                        None,
                        decoded_text,  # 仅返回解码结果
                    )

        # 其他消息类型
        else:
            logging.info(f"收到消息: {msg}")

    # 处理异常
    except Exception as e:
        logging.error(f"处理消息时出错: {e}")


# 保存图片到本地
def save_image_locally(image_url, local_path):
    session = requests.Session()
    session.mount("https://", TLSAdapter())
    response = session.get(image_url, verify=False)
    if response.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(response.content)
        logging.info(f"图片已保存到 {local_path}")
    else:
        logging.error(f"无法下载图片: {image_url}")


# 解码二维码
def decode_qr_code(image_url):
    session = requests.Session()
    session.mount("https://", TLSAdapter())
    response = session.post(
        "https://api.uomg.com/api/qr.encode", data={"url": image_url}, verify=False
    )
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 1:
            return data["qrurl"]
    return json.dumps(response.json(), ensure_ascii=False)


# 主函数
async def main():
    global group_parse_status
    group_parse_status = load_group_status()  # 加载群解析状态
    await connect_to_bot()  # 连接到 QQ 机器人


if __name__ == "__main__":
    asyncio.run(main())

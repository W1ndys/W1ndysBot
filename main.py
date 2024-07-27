# main.py
from flask import Flask, request
import requests

app = Flask(__name__)

# NapCatQQ API的基础URL
base_url = "http://127.0.0.1:30000"


# 发送群聊消息的函数
def send_group_message(group_id, message):
    url = f"{base_url}/send_group_msg"
    params = {"group_id": group_id, "message": message, "access_token": "你的token值"}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print("Failed to send message")
        print(response.status_code, response.text)


@app.route("/", methods=["POST"])
def receive_event():
    指定群聊 = 728077087
    data = request.json
    print("Received event:", data)

    # 检查是否是群消息事件并且是目标群消息
    if (
        data["post_type"] == "message"
        and data["message_type"] == "group"
        and data["group_id"] == 指定群聊
    ):
        # 提取消息内容并确保是字符串
        message_objects = data["message"]
        message = "".join(
            [m["data"]["text"] for m in message_objects if m["type"] == "text"]
        )

        print(f"Processed message: {message}")

        # 检查消息内容是否包含“卷卷”
        if "卷卷" in message:
            send_group_message(指定群聊, "hello world")

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7777)

import requests
from _secret import anpush_token


def send_push_notification():
    token = anpush_token
    title = "机器人掉线通知"
    content = "你的机器人掉线了！"
    channel = "39930"
    url = f"https://api.anpush.com/push/{token}?title={title}&content={content}&channel={channel}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": "Failed to send push notification",
            "status_code": response.status_code,
        }


print(send_push_notification())

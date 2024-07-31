# handlers/dingtalk_notifier.py
# 用于发送钉钉通知
import requests
import json


class DingTalkNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_message(self, message):
        headers = {"Content-Type": "application/json"}
        data = {"msgtype": "text", "text": {"content": message}}
        response = requests.post(
            self.webhook_url, headers=headers, data=json.dumps(data)
        )
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")


# 使用示例
if __name__ == "__main__":
    webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_ACCESS_TOKEN"
    notifier = DingTalkNotifier(webhook_url)
    notifier.send_message("Hello, this is a test message from DingTalkNotifier.")

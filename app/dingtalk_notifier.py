# handlers/dingtalk_notifier.py
# 用于发送钉钉通知
import requests
import json
import time
import hmac
import hashlib
import urllib
import base64
from logger import logging
import asyncio


# 推送到钉钉
async def dingtalk(text, desp, DD_BOT_TOKEN, DD_BOT_SECRET=None):
    url = f"https://oapi.dingtalk.com/robot/send?access_token={DD_BOT_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {"msgtype": "text", "text": {"content": f"{text}\n{desp}"}}

    if DD_BOT_TOKEN and DD_BOT_SECRET:
        timestamp = str(round(time.time() * 1000))
        secret_enc = DD_BOT_SECRET.encode("utf-8")
        string_to_sign = f"{timestamp}\n{DD_BOT_SECRET}"
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(
            base64.b64encode(hmac_code).decode("utf-8").strip()
        )
        url = f"{url}&timestamp={timestamp}&sign={sign}"

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    try:
        data = response.json()
        if response.status_code == 200 and data.get("errcode") == 0:
            logging.info("钉钉发送通知消息成功🎉")
        else:
            logging.error(f"钉钉发送通知消息失败😞\n{data.get('errmsg')}")
    except Exception as e:
        logging.error(f"钉钉发送通知消息失败😞\n{e}")

    return response.json()


if __name__ == "__main__":
    DD_BOT_SECRET = "x"
    DD_BOT_TOKEN = "x"
    asyncio.run(dingtalk("test", "test", DD_BOT_TOKEN, DD_BOT_SECRET))

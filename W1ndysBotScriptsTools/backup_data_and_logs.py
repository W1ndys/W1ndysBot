import os
import tarfile
import requests
import json
import time
import hmac
import hashlib
import urllib
import base64
import urllib.parse
import asyncio

dingtalk_token = "0c0ad4540eed1d1eab06d7229a573146430e6a8b5429eb4e3ada81e039987f6c"

dingtalk_secret = "SEC1000ac85e635258597301a211cde38a94644e10f473b110af6f2463e6008e441"


async def dingtalk(text, desp):
    """发送钉钉通知"""
    DD_BOT_TOKEN = dingtalk_token
    DD_BOT_SECRET = dingtalk_secret

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
            print("钉钉发送通知消息成功🎉")
        else:
            print(f"钉钉发送通知消息失败😞\n{data.get('errmsg')}")
    except Exception as e:
        print(f"钉钉发送通知消息失败😞\n{e}")

    return response.json()


async def backup_data_and_logs():
    """备份数据和日志"""
    # 进入/home/bot/app目录
    try:
        os.chdir("/home/bot/app")
    except Exception as e:
        print("/home/bot/app 目录不存在或无法访问")
        return False

    # 检查data和logs目录是否存在
    if not os.path.exists("data") or not os.path.exists("logs"):
        print("data 或 logs 目录不存在")
        return False

    # 获取当前日期
    current_date = time.strftime("%Y%m%d")
    archive_name = "backup_data_and_logs.tar.gz"

    try:
        # 打包data和logs目录
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add("data")
            tar.add("logs")
        print(f"打包成功: {archive_name}")

        # 发送成功通知
        await dingtalk("data和logs文件打包成功", archive_name)
        return True
    except Exception as e:
        print(f"打包失败: {str(e)}")
        return False


if __name__ == "__main__":
    asyncio.run(backup_data_and_logs())

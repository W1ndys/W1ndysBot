#! /usr/bin/env python3
import os
import asyncio
from datetime import datetime
from logger import logger
from bot import connect_to_bot
from config import OWNER_ID, WS_URL, TOKEN, FEISHU_BOT_URL, FEISHU_BOT_SECRET


def verify_config():
    # 如果.env文件不存在，则提示用户
    if not os.path.exists(".env"):
        logger.error("请在完成 .env 文件配置后，删除.example后缀")
        exit()

    """验证配置是否正确"""
    if not OWNER_ID:
        logger.error("OWNER_ID未设置，请在环境变量中设置")
        exit()
    if not WS_URL:
        logger.error("WS_URL未设置，请在环境变量中设置")
        exit()
    if not TOKEN:
        logger.warning(
            "TOKEN未设置，如果需要使用token认证，请在环境变量中设置，若不需要则可以忽略"
        )
    # 以下是选填项
    if not FEISHU_BOT_URL:
        logger.warning(
            "FEISHU_BOT_URL未设置, 飞书机器人可能无法正常工作，若不需要则可以忽略，如果需要设置，请在环境变量中设置"
        )
    if not FEISHU_BOT_SECRET:
        logger.warning(
            "FEISHU_BOT_SECRET未设置, 飞书机器人可能无法正常工作，若不需要则可以忽略，如果需要设置，请在环境变量中设置"
        )


class Application:
    def __init__(self):

        # 验证环境变量
        verify_config()

    async def run(self):
        """运行主程序"""
        # 打印当前运行根目录
        logger.info(f"当前运行根目录: {os.getcwd()}")
        while True:
            try:
                result = await connect_to_bot()
                if result is None:
                    raise ValueError("连接返回None")
            except KeyboardInterrupt:
                logger.error("检测到用户主动退出程序（Ctrl+C），程序已终止。")
                break
            except Exception as e:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.error(f"连接失败，正在重试: {e} 当前时间: {current_time}")

                await asyncio.sleep(2)  # 每2秒重试一次


if __name__ == "__main__":
    app = Application()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logger.error("检测到用户主动退出程序（Ctrl+C），程序已终止。")

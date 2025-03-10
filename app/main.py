# main.py

import asyncio
from bot import connect_to_bot
from dingtalk import dingtalk
import logging
import datetime
from logger import setup_logger

setup_logger()


async def main():
    while True:
        try:
            result = await connect_to_bot()
            if result is None:
                raise ValueError("连接返回None")
        except Exception as e:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.error(f"连接失败，正在重试: {e} 当前时间: {current_time}")
            if not hasattr(main, "notified"):
                await dingtalk(
                    f"机器人断开连接，当前时间:{current_time}", f"错误信息: {e}"
                )
                main.notified = True

            await asyncio.sleep(1)  # 每秒重试一次


if __name__ == "__main__":
    asyncio.run(main())

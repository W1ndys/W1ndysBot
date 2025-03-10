# bot.py

import logging
import asyncio
import websockets
from config import *


from datetime import datetime


from handler_events import handle_message

from api import send_private_msg


async def connect_to_bot():
    # 创建信号量，限制并发任务数量
    semaphore = asyncio.Semaphore(10)  # 限制最大并发数为10
    tasks = set()  # 用于存储所有任务的集合

    async def process_message(websocket, message):
        async with semaphore:
            try:
                await handle_message(websocket, message)
            except Exception as e:
                # 添加更详细的错误日志
                logging.error(f"处理消息时出错: {e}")
                logging.error(f"消息内容: {message}")
                # 可选：将错误通知发送给机器人所有者
                try:
                    await send_private_msg(
                        websocket,
                        owner_id[0],
                        f"处理消息时出错: {e}\n消息内容: {message}",
                    )
                except Exception as notify_error:
                    logging.error(f"发送错误通知失败: {notify_error}")

    # 清理已完成的任务
    def clean_tasks(tasks):
        done = {t for t in tasks if t.done()}
        tasks.difference_update(done)
        for t in done:
            try:
                t.result()
            except Exception as e:
                # 添加更详细的错误日志
                logging.error(f"任务执行出错: {e}")
                logging.exception("详细错误信息:")

    logging.info("正在连接到机器人...")
    logging.info(f"连接地址: {ws_url}")

    # 如果 token 不为 None，则添加到请求头
    if token:
        async with websockets.connect(
            ws_url, extra_headers={"Authorization": f"Bearer {token}"}
        ) as websocket:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"已连接到机器人。当前时间: {current_time}")
            await send_private_msg(
                websocket, owner_id[0], f"机器人已连接。当前时间: {current_time}"
            )
            async for message in websocket:
                # 清理已完成的任务
                clean_tasks(tasks)
                # 创建新任务并添加到任务集合
                task = asyncio.create_task(process_message(websocket, message))
                tasks.add(task)
    else:
        async with websockets.connect(ws_url) as websocket:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"已连接到机器人。当前时间: {current_time}")
            await send_private_msg(
                websocket, owner_id[0], f"机器人已连接。当前时间: {current_time}"
            )
            async for message in websocket:
                # 清理已完成的任务
                clean_tasks(tasks)
                # 创建新任务并添加到任务集合
                task = asyncio.create_task(process_message(websocket, message))
                tasks.add(task)


if __name__ == "__main__":
    asyncio.run(connect_to_bot())

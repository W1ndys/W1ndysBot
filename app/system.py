# script/System/main.py

import logging
import os
import sys
from datetime import datetime
import re
from collections import deque
import asyncio

# 添加项目根目录到sys.path
sys.path.append((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.api import *

# 该机器人系统的日志目录
LOG_DIR = os.path.join((os.path.dirname(os.path.abspath(__file__))), "logs")

# 确保日志目录存在
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def get_latest_log_file(log_dir):
    """获取日志目录内最新的日志文件"""
    try:
        return max(
            [
                os.path.join(log_dir, f)
                for f in os.listdir(log_dir)
                if f.endswith(".log")
            ],
            key=lambda x: datetime.strptime(
                os.path.basename(x), "%Y-%m-%d_%H-%M-%S.log"
            ),
        )
    except ValueError:
        logging.error("日志目录中没有找到日志文件")
        return None


# 获取指定文件的最后的指定行内容
def get_last_n_lines(file_path, n):
    """从文件中获取最后n行"""
    try:
        with open(file_path, "rb") as file:
            # 使用seek从文件末尾开始读取
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            buffer_size = 1024
            buffer = deque()
            lines = []

            while file_size > 0 and len(lines) <= n:
                # 计算要读取的字节数
                read_size = min(buffer_size, file_size)
                file_size -= read_size
                file.seek(file_size)
                data = file.read(read_size)
                buffer.appendleft(data)  # 直接添加数据

                # 将缓冲区转换为字节串并分割行
                lines = b"".join(buffer).splitlines()

            # 返回最后n行
            return lines[-n:]
    except Exception as e:
        logging.error(f"读取文件失败: {e}")
        return []


# 过滤日志中的debug日志
def filter_debug_logs(log_content):
    """过滤掉日志内容中的DEBUG级别日志"""
    try:
        # 将日志内容按行分割
        lines = log_content.splitlines()

        # 过滤掉包含"DEBUG"的行
        filtered_lines = [line for line in lines if "DEBUG" not in line]

        # 返回过滤后的内容
        return "\n".join(filtered_lines)

    except Exception as e:
        logging.error(f"过滤DEBUG日志失败: {e}")
        return log_content  # 返回原始内容以防止数据丢失


# 更新源代码的函数
async def handle_update_source_code(websocket, target_id, message_id, is_group=True):
    """处理更新源代码的通用函数"""
    send_msg = send_group_msg if is_group else send_private_msg
    await send_msg(
        websocket,
        target_id,
        f"[CQ:reply,id={message_id}]开始更新源代码...\n当前时间："
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    # 执行解包
    backup_process = await asyncio.create_subprocess_shell(
        "bash /home/bot/app/extract-backup-scripts.sh",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    backup_stdout, backup_stderr = await backup_process.communicate()

    if backup_process.returncode != 0:
        await send_msg(
            websocket,
            target_id,
            f"[CQ:reply,id={message_id}]更新源代码失败:\n{backup_stderr.decode()}",
        )
        return

    # 执行重启
    await handle_restart(websocket, target_id, message_id, is_group)


# 通用消息处理函数
async def handle_update_blog(websocket, target_id, message_id, is_group=True):
    """处理更新博客的通用函数"""
    send_msg = send_group_msg if is_group else send_private_msg
    await send_msg(
        websocket,
        target_id,
        f"[CQ:reply,id={message_id}]开始更新博客...预计需要15秒左右\n当前时间："
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    process = await asyncio.create_subprocess_shell(
        "bash /home/W1ndys/BlogTools/update_site.sh",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        await send_msg(
            websocket,
            target_id,
            f"[CQ:reply,id={message_id}]更新博客完成\n当前时间："
            + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
    else:
        await send_msg(
            websocket,
            target_id,
            f"[CQ:reply,id={message_id}]更新博客失败:\n{stderr.decode()}",
        )


async def handle_update_easy_qfnu(websocket, target_id, message_id, is_group=True):
    """处理更新Easy-QFNU的通用函数"""
    send_msg = send_group_msg if is_group else send_private_msg
    await send_msg(
        websocket,
        target_id,
        f"[CQ:reply,id={message_id}]开始更新Easy-QFNU...预计需要15秒左右\n当前时间："
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    process = await asyncio.create_subprocess_shell(
        "bash /home/W1ndys/Easy-QFNU_scripts/update_site.sh",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        await send_msg(
            websocket,
            target_id,
            f"[CQ:reply,id={message_id}]更新Easy-QFNU完成\n当前时间："
            + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
    else:
        await send_msg(
            websocket,
            target_id,
            f"[CQ:reply,id={message_id}]更新Easy-QFNU失败:\n{stderr.decode()}",
        )


async def handle_backup(websocket, target_id, message_id, is_group=True):
    """处理备份的通用函数"""
    send_msg = send_group_msg if is_group else send_private_msg
    await send_msg(
        websocket,
        target_id,
        f"[CQ:reply,id={message_id}]开始备份...",
    )
    process = await asyncio.create_subprocess_shell(
        "python3 /home/bot/W1ndysBotScriptsTools/backup_data_and_logs.py",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        await send_msg(
            websocket,
            target_id,
            f"[CQ:reply,id={message_id}]备份完成",
        )
    else:
        await send_msg(
            websocket,
            target_id,
            f"[CQ:reply,id={message_id}]备份失败:\n{stderr.decode()}",
        )


async def handle_restart(websocket, target_id, message_id, is_group=True):
    """处理重启的通用函数"""
    send_msg = send_group_msg if is_group else send_private_msg
    await send_msg(
        websocket,
        target_id,
        f"[CQ:reply,id={message_id}]即将重启，请稍等...",
    )
    process = await asyncio.create_subprocess_shell(
        "sh /home/bot/restart-app.sh",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        await send_msg(
            websocket,
            target_id,
            f"[CQ:reply,id={message_id}]重启命令已执行",
        )
    else:
        await send_msg(
            websocket,
            target_id,
            f"[CQ:reply,id={message_id}]重启失败:\n{stderr.decode()}",
        )


async def handle_logs(
    websocket, target_id, message_id, latest_log_file, num_lines, is_group=True
):
    """处理日志查看的通用函数"""
    send_msg = send_group_msg if is_group else send_private_msg
    last_n_lines = get_last_n_lines(latest_log_file, num_lines)
    last_n_lines_str = "\n".join(line.decode("utf-8") for line in last_n_lines)
    last_n_lines_filter_debug_logs = filter_debug_logs(last_n_lines_str)
    latest_log_file_path = latest_log_file or "未知日志文件"
    last_n_lines_filter_debug_logs = last_n_lines_filter_debug_logs or "无日志内容"
    message = (
        "日志文件: " + latest_log_file_path + "\n\n" + last_n_lines_filter_debug_logs
    )
    await send_msg(
        websocket,
        target_id,
        f"[CQ:reply,id={message_id}]{message}",
    )

    error_lines = [line for line in last_n_lines_str.splitlines() if "ERROR" in line]
    if error_lines:
        error_message = "错误日志:\n" + "\n".join(error_lines)
        await send_msg(
            websocket,
            target_id,
            f"[CQ:reply,id={message_id}]{error_message}",
        )


# 群消息处理函数
async def handle_System_group_message(websocket, msg):

    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))

        # 获取最新日志文件路径
        latest_log_file = get_latest_log_file(LOG_DIR)
        if not latest_log_file:
            await send_group_msg(websocket, group_id, "未找到日志文件")
            return

        # 卷卷的介绍
        if raw_message == "卷卷":
            await send_group_msg(
                websocket,
                group_id,
                "卷卷是一个由W1ndys开发的QQ机器人，基于NapCatQQ框架。"
                "开源地址：https://github.com/W1ndys/W1ndysBot"
                "使用手册：https://blog.w1ndys.top/posts/fbd9a8fd.html"
                "开发文档（暂未完成）：https://w1ndysbot.github.io/W1ndysBotDocs/",
            )
            return

        if user_id not in owner_id:
            return

        match_logs = re.match(r"logs(\d+)?", raw_message)
        match_errorlog = re.match(r"errorlog(\d+)?", raw_message)
        match_debuglog = re.match(r"debuglog(\d+)?", raw_message)
        match_restart = raw_message == "重启" or raw_message == "restart"
        match_backup = raw_message == "备份" or raw_message == "backup"

        match_update_easy_qfnu = re.match("更新Easy-QFNU", raw_message) or re.match(
            "update Easy-QFNU", raw_message
        )

        match_update_blog = re.match("更新博客", raw_message) or re.match(
            "update blog", raw_message
        )
        match_update_source_code = re.match("更新源代码", raw_message) or re.match(
            "update source code", raw_message
        )

        if match_update_source_code:
            await handle_update_source_code(
                websocket, group_id, message_id, is_group=True
            )
            return

        if match_update_blog:
            await handle_update_blog(websocket, group_id, message_id, is_group=True)
            return

        if match_update_easy_qfnu:
            await handle_update_easy_qfnu(
                websocket, group_id, message_id, is_group=True
            )
            return

        if match_backup:
            await handle_backup(websocket, group_id, message_id, is_group=True)
            return

        if match_restart:
            await handle_restart(websocket, group_id, message_id, is_group=True)
            return

        if match_logs:
            num_lines = int(match_logs.group(1) or 50)
            await handle_logs(
                websocket,
                group_id,
                message_id,
                latest_log_file,
                num_lines,
                is_group=True,
            )
            return

        if match_errorlog:
            num_lines = int(match_errorlog.group(1) or 50)  # 默认50条
            all_lines = get_last_n_lines(latest_log_file, 1000)  # 假设读取足够多的行
            all_lines_str = "\n".join(line.decode("utf-8") for line in all_lines)
            error_lines = [
                line for line in all_lines_str.splitlines() if "ERROR" in line
            ]

            # 取最近的指定数量的错误日志
            recent_error_lines = error_lines[-num_lines:]

            if recent_error_lines:
                error_message = "错误日志:\n" + "\n".join(recent_error_lines)
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]{error_message}",
                )
            else:
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]没有找到错误日志",
                )
            return

        if match_debuglog:
            num_lines = int(match_debuglog.group(1) or 50)  # 默认50条
            all_lines = get_last_n_lines(latest_log_file, 1000)  # 假设读取足够多的行
            all_lines_str = "\n".join(line.decode("utf-8") for line in all_lines)
            debug_lines = [
                line
                for line in all_lines_str.splitlines()
                if "DEBUG" in line and "DEBUG:root:" in line
            ]

            # 取最近的指定数量的错误日志
            recent_debug_lines = debug_lines[-num_lines:]

            if recent_debug_lines:
                debug_message = "调试日志:\n" + "\n".join(recent_debug_lines)
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]{debug_message}",
                )
            else:
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]没有找到调试日志",
                )
            return

    except Exception as e:
        logging.error(f"处理System群消息失败: {e}")
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]处理System群消息失败，错误信息：{str(e)}",
        )
        return


# 私聊消息处理函数
async def handle_System_private_message(websocket, msg):
    try:
        user_id = str(msg.get("user_id"))
        raw_message = str(msg.get("raw_message"))
        message_id = str(msg.get("message_id"))

        # 获取最新日志文件路径
        latest_log_file = get_latest_log_file(LOG_DIR)
        if not latest_log_file:
            await send_private_msg(websocket, user_id, "未找到日志文件")
            return

        # 卷卷的介绍
        if raw_message == "卷卷":
            await send_private_msg(
                websocket,
                user_id,
                "卷卷是一个由W1ndys开发的QQ机器人，基于NapCatQQ框架。"
                "开源地址：https://github.com/W1ndys/W1ndysBot"
                "使用手册：https://blog.w1ndys.top/posts/fbd9a8fd.html"
                "开发文档（暂未完成）：https://w1ndysbot.github.io/W1ndysBotDocs/",
            )
            return

        if user_id not in owner_id:
            return

        match_logs = re.match(r"logs(\d+)?", raw_message)
        match_errorlog = re.match(r"errorlog(\d+)?", raw_message)
        match_debuglog = re.match(r"debuglog(\d+)?", raw_message)
        match_restart = raw_message == "重启" or raw_message == "restart"
        match_backup = raw_message == "备份" or raw_message == "backup"

        match_update_easy_qfnu = re.match("更新Easy-QFNU", raw_message) or re.match(
            "update Easy-QFNU", raw_message
        )

        match_update_blog = re.match("更新博客", raw_message) or re.match(
            "update blog", raw_message
        )

        if match_update_blog:
            await handle_update_blog(websocket, user_id, message_id, is_group=False)
            return

        if match_update_easy_qfnu:
            await handle_update_easy_qfnu(
                websocket, user_id, message_id, is_group=False
            )
            return

        if match_backup:
            await handle_backup(websocket, user_id, message_id, is_group=False)
            return

        if match_restart:
            await handle_restart(websocket, user_id, message_id, is_group=False)
            return

        if match_logs:
            num_lines = int(match_logs.group(1) or 50)
            await handle_logs(
                websocket,
                user_id,
                message_id,
                latest_log_file,
                num_lines,
                is_group=False,
            )
            return

        if match_errorlog:
            num_lines = int(match_errorlog.group(1) or 50)  # 默认50条
            all_lines = get_last_n_lines(latest_log_file, 1000)  # 假设读取足够多的行
            all_lines_str = "\n".join(line.decode("utf-8") for line in all_lines)
            error_lines = [
                line for line in all_lines_str.splitlines() if "ERROR" in line
            ]

            # 取最近的指定数量的错误日志
            recent_error_lines = error_lines[-num_lines:]

            if recent_error_lines:
                error_message = "错误日志:\n" + "\n".join(recent_error_lines)
                await send_private_msg(
                    websocket,
                    user_id,
                    f"[CQ:reply,id={message_id}]{error_message}",
                )
            else:
                await send_private_msg(
                    websocket,
                    user_id,
                    f"[CQ:reply,id={message_id}]没有找到错误日志",
                )
            return

        if match_debuglog:
            num_lines = int(match_debuglog.group(1) or 50)  # 默认50条
            all_lines = get_last_n_lines(latest_log_file, 1000)  # 假设读取足够多的行
            all_lines_str = "\n".join(line.decode("utf-8") for line in all_lines)
            debug_lines = [
                line
                for line in all_lines_str.splitlines()
                if "DEBUG" in line and "DEBUG:root:" in line
            ]

            # 取最近的指定数量的错误日志
            recent_debug_lines = debug_lines[-num_lines:]

            if recent_debug_lines:
                debug_message = "调试日志:\n" + "\n".join(recent_debug_lines)
                await send_private_msg(
                    websocket,
                    user_id,
                    f"[CQ:reply,id={message_id}]{debug_message}",
                )
            else:
                await send_private_msg(
                    websocket,
                    user_id,
                    f"[CQ:reply,id={message_id}]没有找到调试日志",
                )
            return

    except Exception as e:
        logging.error(f"处理System私聊消息失败: {e}")
        await send_private_msg(
            websocket,
            user_id,
            f"[CQ:reply,id={message_id}]处理System私聊消息失败，错误信息：{str(e)}",
        )
        return


# 统一事件处理入口
async def handle_events(websocket, msg):
    """统一事件处理入口

    处理所有类型的事件,包括:
    - 回调事件
    - 元事件
    - 消息事件(群聊/私聊)
    - 通知事件

    Args:
        websocket: WebSocket连接对象
        msg: 接收到的消息字典
    """
    try:
        # 处理回调事件
        if msg.get("status") == "ok":
            pass
            return

        post_type = msg.get("post_type")

        # 处理元事件
        if post_type == "meta_event":
            pass
            return

        # 处理消息事件
        elif post_type == "message":
            message_type = msg.get("message_type")
            if message_type == "group":
                await handle_System_group_message(websocket, msg)
            elif message_type == "private":
                await handle_System_private_message(websocket, msg)
            return

        # 处理通知事件
        elif post_type == "notice":
            notice_type = msg.get("notice_type")
            if notice_type == "group":
                return

        # 处理未知事件类型
        else:
            logging.warning(f"收到未知事件类型: {post_type}")
            return

    except Exception as e:
        error_type = {
            "message": "消息",
            "notice": "通知",
            "request": "请求",
            "meta_event": "元事件",
        }.get(post_type, "未知")

        logging.error(f"处理{error_type}事件失败: {e}")
        logging.exception(e)  # 打印完整堆栈信息

        # 发送错误提示
        if post_type == "message":
            message_type = msg.get("message_type")
            error_msg = f"处理{error_type}事件失败，错误信息：{str(e)}"

            if message_type == "group":
                await send_group_msg(websocket, msg.get("group_id"), error_msg)
            elif message_type == "private":
                await send_private_msg(websocket, msg.get("user_id"), error_msg)

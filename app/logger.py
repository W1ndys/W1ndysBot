import os
import sys
import asyncio
from datetime import datetime, timezone, timedelta
from loguru import logger as loguru_logger
from api.message import send_private_msg
from config import OWNER_ID


class Logger:
    def __init__(self, websocket=None, logs_dir="logs", console_level="INFO"):
        self.websocket = websocket
        self.console_level = console_level

        # 获取日志目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logs_dir = logs_dir or os.path.join(current_dir, "logs")
        self.log_filename = None

        # 初始化时自动设置
        self.setup()

    def _is_user_exit_error(self):
        """检查是否是用户主动退出导致的错误"""
        # 获取当前异常信息
        exc_type, exc_value, exc_traceback = sys.exc_info()

        if exc_type is None:
            return False

        # 用户主动退出相关的异常类型
        user_exit_exceptions = (
            KeyboardInterrupt,  # Ctrl+C
            SystemExit,  # 正常退出
            BrokenPipeError,  # 管道中断
            ConnectionAbortedError,  # 连接中断
            ConnectionResetError,  # 连接重置
        )

        return issubclass(exc_type, user_exit_exceptions)

    def setup(self):
        """设置日志器"""
        # 移除默认处理器
        loguru_logger.remove()

        # 创建日志目录
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        # 设置日志文件名模式，支持轮转时自动命名
        self.log_filename = os.path.join(
            self.logs_dir, "bot_{time:YYYY-MM-DD_HH-mm-ss}.log"
        )

        # 添加控制台处理器 - 美化格式
        loguru_logger.add(
            sink=lambda msg: print(msg, end=""),
            format="<green>{time:MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>",
            level=self.console_level,
            colorize=True,
        )

        # 添加文件处理器（带日志轮转） - 详细格式
        loguru_logger.add(
            sink=self.log_filename,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{process.id}:{thread.id} | "
            "{name}:{function}:{line} | "
            "{message}",
            level="DEBUG",
            encoding="utf-8",
            rotation="1 day",  # 每天轮转一次，生成更大的日志文件
            retention="30 days",  # 保留30天内的日志文件
            compression="gz",  # 使用gzip压缩，压缩率更好且更通用
        )

        self.success(f"初始化日志器，日志文件名: {self.log_filename}")
        return self.log_filename

    # 便捷日志方法
    def debug(self, message):
        loguru_logger.debug(message)

    def info(self, message):
        loguru_logger.info(message)

    def warning(self, message):
        loguru_logger.warning(message)

    def error(self, message):
        loguru_logger.error(message)

        # 检查是否是用户主动退出导致的错误，如果是则不发送错误报告
        if self._is_user_exit_error():
            return

        # 异步发送私聊到OWNER_ID
        if OWNER_ID and self.websocket:
            try:
                # 通过事件循环调度异步任务
                loop = asyncio.get_event_loop()
                # 兼容在协程和主线程下的调用
                if loop.is_running():
                    asyncio.create_task(
                        send_private_msg(self.websocket, OWNER_ID, f"[ERROR] {message}")
                    )
                else:
                    loop.run_until_complete(
                        send_private_msg(self.websocket, OWNER_ID, f"[ERROR] {message}")
                    )
            except Exception as e:
                loguru_logger.error(f"发送错误日志到OWNER_ID失败: {e}")

    def critical(self, message):
        loguru_logger.critical(message)

    def success(self, message):
        loguru_logger.log("SUCCESS", message)

    def set_console_level(self, level):
        """动态设置控制台日志级别"""
        self.console_level = level
        # 重新设置日志器
        self.setup()

    def set_level(self, level):
        """为了向后兼容保留的方法，实际调用set_console_level"""
        self.set_console_level(level)


# 创建一个全局日志器实例
logger = Logger()


# 便捷函数，使调用更简单
def debug(message):
    logger.debug(message)


def info(message):
    logger.info(message)


def warning(message):
    logger.warning(message)


def error(message):
    logger.error(message)


def critical(message):
    logger.critical(message)


def success(message):
    logger.success(message)

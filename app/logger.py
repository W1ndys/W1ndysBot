import logging
import colorlog
import os
import asyncio
from datetime import datetime, timezone, timedelta
from api.message import send_private_msg
from config import OWNER_ID

# 自定义SUCCESS日志级别 (在INFO和WARNING之间)
SUCCESS = 25  # INFO是20，WARNING是30
logging.addLevelName(SUCCESS, "SUCCESS")


# 添加success方法到logging模块
def _logger_success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kwargs)


# 将success方法添加到Logger类 - 使用setattr避免类型检查问题
setattr(logging.Logger, "success", _logger_success)


class Logger:
    def __init__(self, websocket=None, logs_dir="logs", console_level="INFO"):
        self.websocket = websocket
        self.root_logger = logging.getLogger()
        self.console_level = console_level  # 重命名为更明确的含义

        # 获取日志目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logs_dir = logs_dir or os.path.join(current_dir, "logs")
        self.log_filename = None

        # 初始化时自动设置
        self.setup()

    def setup(self):
        """设置日志器"""
        # 清除之前的处理器
        self.root_logger.handlers = []

        # 创建控制台和文件处理器
        console_handler, file_handler = self._create_handlers()

        # 设置根日志记录器的级别为DEBUG（最低级别，确保所有日志都能被记录）
        self.root_logger.setLevel(logging.DEBUG)
        self.root_logger.addHandler(console_handler)
        self.root_logger.addHandler(file_handler)

        # 确保日志及时刷新
        for handler in self.root_logger.handlers:
            handler.flush()

        self.success(f"初始化日志器，日志文件名: {self.log_filename}")

        return self.log_filename

    def _create_handlers(self):
        """创建控制台和文件处理器"""
        # 通用配置
        date_format = "%Y-%m-%d %H:%M:%S"
        log_colors = {
            "DEBUG": "cyan",  # 调试信息（青色）
            "INFO": "white",  # 普通信息（白色）
            "WARNING": "yellow",  # 警告信息（黄色）
            "ERROR": "red",  # 错误信息（红色）
            "CRITICAL": "bold_red",  # 严重错误（加粗红色）
            "SUCCESS": "green",  # 发送成功（绿色）
            "NAPCAT": "bold_blue",  # 接收NapCatQQ的消息日志（加粗蓝色）
        }

        # 创建控制台处理器 - 使用console_level
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(
            colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s [%(levelname)s]: %(message)s",
                datefmt=date_format,
                log_colors=log_colors,
            )
        )
        console_handler.setLevel(self.console_level)  # 使用实例变量

        # 创建文件处理器
        # 创建 logs 目录
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        # 以当前启动时间为文件名，使用东八区时间
        tz = timezone(timedelta(hours=8))
        self.log_filename = os.path.join(
            self.logs_dir, f"{datetime.now(tz).strftime('%Y-%m-%d_%H-%M-%S')}.log"
        )

        # 使用普通的FileHandler，不进行轮转
        file_handler = logging.FileHandler(self.log_filename, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s]: %(message)s", datefmt=date_format
            )
        )
        file_handler.setLevel(logging.DEBUG)  # 文件始终记录DEBUG及以上级别

        return console_handler, file_handler

    # 便捷日志方法
    def debug(self, message):
        logging.debug(message)

    def info(self, message):
        logging.info(message)

    def warning(self, message):
        logging.warning(message)

    def error(self, message):
        logging.error(message)
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
                logging.error(f"发送错误日志到OWNER_ID失败: {e}")

    def critical(self, message):
        logging.critical(message)

    def success(self, message):
        logging.log(SUCCESS, message)

    def set_console_level(self, level):
        """动态设置控制台日志级别"""
        self.console_level = level
        # 只更新控制台处理器的级别，文件处理器保持DEBUG
        for handler in self.root_logger.handlers:
            if isinstance(handler, colorlog.StreamHandler):
                handler.setLevel(level)

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

import logging
import colorlog
import os
from datetime import datetime, timezone, timedelta
from logging.handlers import RotatingFileHandler


class Logger:
    def __init__(self, logs_dir="logs", level=logging.INFO):
        self.root_logger = logging.getLogger()
        self.level = level

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

        # 创建控制台处理器
        console_handler = self._create_console_handler()

        # 创建文件处理器
        file_handler = self._create_file_handler()

        # 设置根日志记录器的级别和处理器
        self.root_logger.setLevel(self.level)
        self.root_logger.addHandler(console_handler)
        self.root_logger.addHandler(file_handler)

        # 确保日志及时刷新
        for handler in self.root_logger.handlers:
            handler.flush()

        self.info(f"初始化日志器，日志文件名: {self.log_filename}")

        return self.log_filename

    def _create_console_handler(self):
        """创建控制台处理器"""
        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s %(levelname)s:\n%(message)s\n",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "light_green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
        )
        handler.setLevel(self.level)
        return handler

    def _create_file_handler(self):
        """创建文件处理器"""
        # 创建 logs 目录
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        # 以当前启动时间为文件名，使用东八区时间
        tz = timezone(timedelta(hours=8))
        self.log_filename = os.path.join(
            self.logs_dir, datetime.now(tz).strftime("%Y-%m-%d_%H-%M-%S.log")
        )

        file_handler = RotatingFileHandler(
            self.log_filename, maxBytes=1024 * 1024, backupCount=0, encoding="utf-8"
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s:\n%(message)s\n",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        file_handler.namer = lambda name: name.replace(
            ".log", f"_{datetime.now(tz).strftime('%Y-%m-%d_%H-%M-%S')}.log"
        )
        file_handler.rotator = lambda source, dest: os.rename(source, dest)
        file_handler.setLevel(self.level)
        return file_handler

    # 便捷日志方法
    def debug(self, message):
        logging.debug(message)

    def info(self, message):
        logging.info(message)

    def warning(self, message):
        logging.warning(message)

    def error(self, message):
        logging.error(message)

    def critical(self, message):
        logging.critical(message)

    def set_level(self, level):
        """动态设置日志级别"""
        self.level = level
        self.root_logger.setLevel(level)
        for handler in self.root_logger.handlers:
            handler.setLevel(level)


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


if __name__ == "__main__":
    # 演示logger的使用方法

    # 1. 使用全局logger实例
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志")

    # 2. 使用便捷函数
    debug("使用便捷函数：调试信息")
    info("使用便捷函数：普通信息")
    warning("使用便捷函数：警告信息")
    error("使用便捷函数：错误信息")
    critical("使用便捷函数：严重错误")

    # 3. 修改日志级别
    print("\n修改日志级别为DEBUG后的输出:")
    logger.set_level(logging.DEBUG)
    logger.debug("修改级别后可以看到的调试日志")

    # 4. 创建自定义日志实例
    custom_logger = Logger(logs_dir="custom_logs", level=logging.DEBUG)
    custom_logger.info("这是来自自定义日志器的消息")

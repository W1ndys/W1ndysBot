import logging
import colorlog
import os
from datetime import datetime, timezone, timedelta
from logging.handlers import RotatingFileHandler

# 自定义SUCCESS日志级别 (在INFO和WARNING之间)
SUCCESS = 25  # INFO是20，WARNING是30
logging.addLevelName(SUCCESS, "SUCCESS")

# 添加success方法到logging模块


def _logger_success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kwargs)


# 自定义NAPCAT日志级别 (在INFO和WARNING之间)
NAPCAT = 26  # INFO是20，WARNING是30
logging.addLevelName(NAPCAT, "NAPCAT")


# 添加napcat方法到logging模块
def _logger_napcat(self, message, *args, **kwargs):
    if self.isEnabledFor(NAPCAT):
        self._log(NAPCAT, message, args, **kwargs)


# 将success方法添加到Logger类 - 使用setattr避免类型检查问题
setattr(logging.Logger, "success", _logger_success)
setattr(logging.Logger, "napcat", _logger_napcat)


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
        console_handler = self._create_handler(stream=True)

        # 创建文件处理器
        file_handler = self._create_handler()

        # 设置根日志记录器的级别和处理器
        self.root_logger.setLevel(self.level)
        self.root_logger.addHandler(console_handler)
        self.root_logger.addHandler(file_handler)

        # 确保日志及时刷新
        for handler in self.root_logger.handlers:
            handler.flush()

        self.info(f"初始化日志器，日志文件名: {self.log_filename}")

        return self.log_filename

    def _create_handler(self, stream=False):
        """创建控制台或文件处理器"""
        # 创建格式化器
        log_format = "%(log_color)s[%(asctime)s] [%(levelname)s]: %(message)s"
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

        if stream:
            # 创建控制台处理器
            handler = colorlog.StreamHandler()
            handler.setFormatter(
                colorlog.ColoredFormatter(
                    log_format,
                    datefmt=date_format,
                    log_colors=log_colors,
                )
            )
        else:
            # 创建 logs 目录
            if not os.path.exists(self.logs_dir):
                os.makedirs(self.logs_dir)

            # 以当前启动时间为文件名，使用东八区时间
            tz = timezone(timedelta(hours=8))
            self.log_filename = os.path.join(
                self.logs_dir, datetime.now(
                    tz).strftime("%Y-%m-%d_%H-%M-%S.log")
            )

            # 创建文件处理器
            handler = RotatingFileHandler(
                self.log_filename, maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
            )
            handler.setFormatter(
                logging.Formatter(
                    "[%(asctime)s %(levelname)s]: %(message)s",
                    datefmt=date_format
                )
            )
            handler.namer = lambda name: name.replace(
                ".log", f"_{datetime.now(tz).strftime('%Y-%m-%d_%H-%M-%S')}.log"
            )
            handler.rotator = lambda source, dest: os.rename(source, dest)
        handler.setLevel(self.level)
        return handler

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

    def success(self, message):
        logging.log(SUCCESS, message)

    def napcat(self, message):
        logging.log(NAPCAT, message)

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


def success(message):
    logger.success(message)


def napcat(message):
    logger.napcat(message)


if __name__ == "__main__":
    # 演示logger的使用方法

    # 1. 使用全局logger实例
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志")
    logger.success("这是一条成功日志")
    logger.napcat("这是一条Napcat信息日志")
    # 2. 使用便捷函数
    debug("使用便捷函数：调试信息")
    info("使用便捷函数：普通信息")
    warning("使用便捷函数：警告信息")
    error("使用便捷函数：错误信息")
    critical("使用便捷函数：严重错误")
    success("使用便捷函数：成功信息")
    napcat("使用便捷函数：Napcat信息")

    # 3. 修改日志级别
    print("\n修改日志级别为DEBUG后的输出:")
    logger.set_level(logging.DEBUG)
    logger.debug("修改级别后可以看到的调试日志")

    # 4. 创建自定义日志实例
    custom_logger = Logger(logs_dir="custom_logs", level=logging.DEBUG)
    custom_logger.info("这是来自自定义日志器的消息")

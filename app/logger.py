# logger.py

import logging
import colorlog
import os
from datetime import datetime, timezone, timedelta


def setup_logger():
    # 清除之前的处理器
    root_logger = logging.getLogger()
    root_logger.handlers = []

    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s %(levelname)s:%(name)s:%(message)s",  # 添加日期
            datefmt="%Y-%m-%d %H:%M:%S",  # 日期格式
            log_colors={
                "DEBUG": "cyan",
                "INFO": "light_green",  # 使用更亮的绿色
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )

    # 创建 logs 目录
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # 以当前启动时间为文件名，使用东八区时间
    tz = timezone(timedelta(hours=8))
    log_filename = datetime.now(tz).strftime("logs/%Y-%m-%d_%H-%M-%S.log")

    # 添加 FileHandler 将日志保存到本地文件
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s:%(name)s:%(message)s",  # 添加日期
            datefmt="%Y-%m-%d %H:%M:%S",  # 日期格式
        )
    )

    # 设置根日志记录器的级别和处理器
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)
    root_logger.addHandler(file_handler)

    logging.info("初始化日志器")
    logging.info(f"日志文件名: {log_filename}")

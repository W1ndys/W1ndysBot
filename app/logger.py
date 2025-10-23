import os
import sys
import asyncio
from typing import Optional
from loguru import logger as _logger

from config import OWNER_ID

# 全局配置缓存，方便动态调整
_logs_dir: Optional[str] = None
_console_level: str = "INFO"
_owner_ws = None


def _resolve_logs_dir(logs_dir: Optional[str]) -> str:
    if logs_dir:
        return logs_dir
    # 默认放到当前文件同级的 logs 目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "logs")


def _owner_notify_sink(message):
    """
    ERROR 级别私信通知 OWNER（可选）。
    注意：此 sink 内不要再用 _logger 记录日志，避免递归；出错直接写 stderr。
    """
    if not _owner_ws or not OWNER_ID:
        return

    try:
        # 取简要文本；你也可以拼接更多字段：message.record["file"], ["line"], ["function"] 等
        text = message.record["message"]
        try:
            from api.message import send_private_msg
        except Exception as import_err:
            sys.stderr.write(f"[logger] 无法导入 send_private_msg: {import_err}\n")
            return

        coro = send_private_msg(_owner_ws, OWNER_ID, f"[ERROR] {text}")

        # 在现有事件循环下调度；无循环则临时跑一次
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(coro)
            else:
                loop.run_until_complete(coro)
        except RuntimeError:
            # 非主线程或无事件循环
            asyncio.run(coro)
    except Exception as e:
        sys.stderr.write(f"[logger] 发送错误日志到 OWNER_ID 失败: {e}\n")


def setup_logging(
    websocket=None, logs_dir: Optional[str] = None, console_level: str = "INFO"
):
    """
    初始化 loguru：
    - 控制台彩色输出
    - 文件输出，按天轮转、30 天保留、gz 压缩
    - 可选 ERROR 私信通知 sink
    """
    global _logs_dir, _console_level, _owner_ws
    _logs_dir = _resolve_logs_dir(logs_dir)
    _console_level = console_level
    _owner_ws = websocket

    os.makedirs(_logs_dir, exist_ok=True)
    log_path = os.path.join(_logs_dir, "bot_{time:YYYY-MM-DD_HH-mm-ss}.log")

    # 清空旧的 handler，重新配置
    _logger.remove()

    # 控制台
    _logger.add(
        sink=sys.stdout,
        format="<green>{time:MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{file.name}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>",
        level=_console_level,
        colorize=True,
        diagnose=False,
        backtrace=False,
    )

    # 文件
    _logger.add(
        sink=log_path,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{process.id}:{thread.id} | "
        "{file.path}:{function}:{line} | "
        "{message}",
        level="DEBUG",
        encoding="utf-8",
        rotation="1 day",
        retention="30 days",
        compression="gz",
        diagnose=False,
        backtrace=False,
        enqueue=True,  # 文件 IO 放到队列线程，减少阻塞
    )

    # ERROR 私信通知（可选；不想要就注释掉）
    _logger.add(
        sink=_owner_notify_sink,
        level="ERROR",
        diagnose=False,
        backtrace=False,
    )

    _logger.info(f"日志初始化完成，目录: {_logs_dir}")


def set_level(level: str):
    """动态调整控制台日志级别（会重建 handlers）"""
    # 复用现有 websocket 与目录
    setup_logging(websocket=_owner_ws, logs_dir=_logs_dir, console_level=level)


# 直接导出 loguru 的 logger，业务方应这样用：
# from app.logger import logger
# logger.info("hello")
logger = _logger


class AppLogger:
    """
    极薄包装：如果你更喜欢“类”的使用方式，可以这样：
        log = AppLogger(websocket=ws, logs_dir="logs", console_level="INFO")
        log.info("xxx")
    通过 opt(depth=1) 确保调用栈指向业务代码而非此文件。
    """

    def __init__(
        self,
        websocket=None,
        logs_dir: Optional[str] = None,
        console_level: str = "INFO",
    ):
        setup_logging(
            websocket=websocket, logs_dir=logs_dir, console_level=console_level
        )

    def __getattr__(self, name: str):
        # 将 debug/info/warning/error/exception/... 动态转发到 loguru，并提升调用栈深度
        target = getattr(_logger.opt(depth=1), name, None)
        if callable(target):
            return target
        raise AttributeError(f"'AppLogger' object has no attribute '{name}'")

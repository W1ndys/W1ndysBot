import json
import asyncio
import logger
import shutil
import os
import importlib.util
import inspect


# 核心模块列表 - 这些模块将始终被加载
# 格式: ("模块路径", "模块中的函数名")
# 请不要修改这些模块，除非你知道你在做什么
CORE_MODULES = [
    # 系统工具
    ("utils.clean_logs", "clean_logs"),  # 日志清理
    # 核心功能
    ("core.online_detect", "handle_events"),  # 在线监测
    ("core.del_self_msg", "handle_events"),  # 自动撤回自己发送的消息
    # 在这里添加其他必须加载的核心模块
]


class EventHandler:
    def __init__(self):
        self.handlers = []

        # 加载核心模块（固定加载）
        self._load_core_modules()

        # 动态加载modules目录下的所有模块
        self._load_modules_dynamically()

        # 记录已加载的模块数量
        logger.info(f"总共加载了 {len(self.handlers)} 个事件处理器")

    def _load_core_modules(self):
        """加载核心模块"""
        for module_path, handler_name in CORE_MODULES:
            try:
                module = importlib.import_module(module_path)
                handler = getattr(module, handler_name)
                self.handlers.append(handler)
                logger.info(f"已加载核心模块: {module_path}.{handler_name}")
            except Exception as e:
                logger.error(
                    f"加载核心模块失败: {module_path}.{handler_name}, 错误: {e}"
                )

    def _load_modules_dynamically(self):
        """动态加载modules目录下的所有模块"""
        modules_dir = os.path.join(os.path.dirname(__file__), "modules")
        if not os.path.exists(modules_dir):
            logger.warning(f"模块目录不存在: {modules_dir}")
            return

        # 遍历模块目录
        for module_name in os.listdir(modules_dir):
            module_path = os.path.join(modules_dir, module_name)

            # 跳过非目录和以下划线开头的目录
            if not os.path.isdir(module_path) or module_name.startswith("_"):
                continue

            # 检查模块是否有main.py文件
            main_file = os.path.join(module_path, "main.py")
            if not os.path.exists(main_file):
                logger.warning(f"模块 {module_name} 缺少main.py文件，已跳过")
                continue

            try:
                # 动态导入模块
                module_import_path = f"modules.{module_name}.main"
                module = importlib.import_module(module_import_path)

                # 检查模块是否有handle_events函数
                if hasattr(module, "handle_events") and inspect.iscoroutinefunction(
                    module.handle_events
                ):
                    self.handlers.append(module.handle_events)
                    logger.info(f"已加载模块: {module_name}")
                else:
                    logger.warning(
                        f"模块 {module_name} 缺少异步handle_events函数，已跳过"
                    )
            except Exception as e:
                logger.error(f"加载模块失败: {module_name}, 错误: {e}")

    async def handle_message(self, websocket, message):
        """处理websocket消息"""
        try:
            msg = json.loads(message)

            # 打印WebSocket消息
            terminal_width = shutil.get_terminal_size().columns
            logger.info(
                f"{'-' * terminal_width}\n📩 收到WebSocket消息:\n{msg}\n{'-' * terminal_width}"
            )

            # 并发调用各个模块的事件处理器
            tasks = [handler(websocket, msg) for handler in self.handlers]
            await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f"处理websocket消息的逻辑错误: {e}")

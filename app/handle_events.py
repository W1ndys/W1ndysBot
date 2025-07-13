import json
import asyncio
import logger
import os
import importlib
import inspect
from config import OWNER_ID
from api.message import send_private_msg
from utils.generate import generate_text_message


# 核心模块列表 - 这些模块将始终被加载
# 格式: ("模块路径", "模块中的函数名")
# 请不要修改这些模块，除非你知道你在做什么
CORE_MODULES = [
    # 系统工具
    ("utils.clean_logs", "clean_logs"),  # 日志清理
    # 核心功能
    ("core.online_detect", "handle_events"),  # 在线监测
    ("core.del_self_msg", "handle_events"),  # 自动撤回自己发送的消息
    ("core.nc_get_rkey", "handle_events"),  # 自动刷新rkey
    ("core.menu_manager", "handle_events"),  # 全局菜单命令
    ("core.switchs", "handle_events"),  # 全局开关命令
    ("core.get_group_list", "handle_events"),  # 获取群列表
    ("core.get_group_member_list", "handle_events"),  # 获取群成员列表
    # 在这里添加其他必须加载的核心模块
]


class EventHandler:
    def __init__(self, websocket):
        self.websocket = websocket
        self.handlers = []
        # 用于记录成功加载的模块
        self.loaded_modules = []
        # 用于记录加载失败的模块及原因
        self.failed_modules = []

        # 加载核心模块（固定加载）
        self._load_core_modules()

        # 动态加载modules目录下的所有模块
        self._load_modules_dynamically()

        # 记录已加载的模块数量
        logger.success(f"总共加载了 {len(self.handlers)} 个事件处理器")

        # 向管理员上报模块加载状况
        asyncio.create_task(self._report_loading_status())

    async def _report_loading_status(self):
        """向管理员上报模块加载状况"""
        # 生成成功加载的模块报告（按字母顺序排序）
        sorted_loaded_modules = sorted(self.loaded_modules)
        success_msg = "模块加载成功：\n" + "\n".join(sorted_loaded_modules)

        # 生成失败加载的模块报告（按字母顺序排序）
        failed_msg = "模块加载失败：\n"
        if self.failed_modules:
            sorted_failed_modules = sorted(self.failed_modules, key=lambda x: x[0])
            for module_name, error in sorted_failed_modules:
                failed_msg += f"{module_name}：{error}\n"
        else:
            failed_msg += "无"

        # 组合报告信息
        report_msg = f"{success_msg}\n\n{failed_msg}"

        # 发送给管理员
        try:
            await send_private_msg(
                self.websocket, OWNER_ID, [generate_text_message(report_msg)]
            )
            logger.info("已向管理员上报模块加载状况")
        except Exception as e:
            logger.error(f"向管理员上报模块加载状况失败：{e}")

    def _load_core_modules(self):
        """加载核心模块"""
        for module_path, handler_name in CORE_MODULES:
            try:
                module = importlib.import_module(module_path)
                handler = getattr(module, handler_name)
                self.handlers.append(handler)
                # 记录成功加载的模块
                self.loaded_modules.append(f"{module_path}.{handler_name}")
                logger.success(f"已加载核心模块: {module_path}.{handler_name}")
            except Exception as e:
                # 记录加载失败的模块及原因
                self.failed_modules.append((f"{module_path}.{handler_name}", str(e)))
                logger.error(
                    f"加载核心模块失败: {module_path}.{handler_name}, 错误: {e}"
                )

    def _load_modules_dynamically(self):
        """动态加载modules目录下的所有模块"""
        modules_dir = os.path.join(os.path.dirname(__file__), "modules")
        if not os.path.exists(modules_dir):
            logger.warning(f"模块目录不存在: {modules_dir}")
            return

        # 获取所有模块目录并按字母顺序排序
        module_names = sorted(
            [
                module_name
                for module_name in os.listdir(modules_dir)
                if os.path.isdir(os.path.join(modules_dir, module_name))
                and not module_name.startswith("_")
            ]
        )

        # 遍历排序后的模块目录
        for module_name in module_names:
            module_path = os.path.join(modules_dir, module_name)

            # 检查模块是否有main.py文件
            main_file = os.path.join(module_path, "main.py")
            if not os.path.exists(main_file):
                self.failed_modules.append((module_name, "缺少main.py文件"))
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
                    # 记录成功加载的模块
                    self.loaded_modules.append(module_name)
                    logger.success(f"已加载模块: {module_name}")
                else:
                    # 记录加载失败的模块及原因
                    self.failed_modules.append(
                        (module_name, "缺少异步handle_events函数")
                    )
                    logger.warning(
                        f"模块 {module_name} 缺少异步handle_events函数，已跳过"
                    )
            except Exception as e:
                # 记录加载失败的模块及原因
                self.failed_modules.append((module_name, str(e)))
                logger.error(f"加载模块失败: {module_name}, 错误: {e}")

    async def _safe_handle(self, handler, websocket, msg):
        try:
            await handler(websocket, msg)
        except Exception as e:
            logger.error(f"模块 {handler} 处理消息时出错: {e}")

    async def handle_message(self, websocket, message):
        """处理websocket消息"""
        try:
            msg = json.loads(message)

            # 日志忽略列表，echo字段包含这些字符串时不记录日志
            LOG_IGNORE_ECHO_LIST = [
                "get_group_member_list",
                "get_group_list",
                "get_friend_list",
                "get_group_info",
                "nc_get_rkey",
                # 可以根据需要继续添加
            ]

            # 判断是否需要忽略日志
            echo_value = msg.get("echo", "")
            if not any(
                ignore_str in str(echo_value) for ignore_str in LOG_IGNORE_ECHO_LIST
            ):
                logger.info(f"接收到websocket消息: {msg}")

            # 每个 handler 独立异步后台处理
            for handler in self.handlers:
                asyncio.create_task(self._safe_handle(handler, websocket, msg))

        except Exception as e:
            logger.error(f"处理websocket消息的逻辑错误: {e}")

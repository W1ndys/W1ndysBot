"""
开关系统命令处理器
负责处理开关相关的命令和事件
"""

from logger import logger
from utils.generate import generate_reply_message, generate_text_message
from api.message import send_private_msg, send_group_msg
from utils.auth import is_system_admin, is_group_admin
from .config import SWITCH_COMMAND
from .switch_manager import SwitchManager


class SwitchCommandHandler:
    """开关命令处理器"""

    @staticmethod
    async def handle_module_private_switch(module_name, websocket, user_id, message_id):
        """
        处理模块私聊开关命令

        Args:
            module_name: 模块名称
            websocket: WebSocket连接
            user_id: 用户ID
            message_id: 消息ID
        """
        try:
            switch_status = SwitchManager.toggle_private_switch(module_name)
            switch_status_text = "开启" if switch_status else "关闭"

            reply_message = generate_reply_message(message_id)
            text_message = generate_text_message(
                f"[{module_name}]私聊开关已切换为【{switch_status_text}】"
            )

            await send_private_msg(
                websocket,
                user_id,
                [reply_message, text_message],
                note="del_msg=10",
            )
        except Exception as e:
            logger.error(f"[{module_name}]处理模块私聊开关命令失败: {e}")

    @staticmethod
    async def handle_module_group_switch(module_name, websocket, group_id, message_id):
        """
        处理模块群聊开关命令

        Args:
            module_name: 模块名称
            websocket: WebSocket连接
            group_id: 群ID
            message_id: 消息ID

        Returns:
            str: 切换后的状态文本
        """
        try:
            switch_status = SwitchManager.toggle_group_switch(group_id, module_name)
            switch_status_text = "开启" if switch_status else "关闭"

            reply_message = generate_reply_message(message_id)
            text_message = generate_text_message(
                f"[{module_name}]群聊开关已切换为【{switch_status_text}】"
            )

            await send_group_msg(
                websocket,
                group_id,
                [reply_message, text_message],
                note="del_msg=10",
            )
            return switch_status_text
        except Exception as e:
            logger.error(f"[{module_name}]处理模块群聊开关命令失败: {e}")
            return "错误"

    @staticmethod
    async def handle_switch_query(websocket, group_id, message_id):
        """
        处理开关查询命令

        Args:
            websocket: WebSocket连接
            group_id: 群ID
            message_id: 消息ID
        """
        try:
            # 获取本群已开启的模块
            enabled_modules = SwitchManager.get_enabled_modules_in_group(group_id)

            reply_message = generate_reply_message(message_id)

            if enabled_modules:
                switch_text = f"本群（{group_id}）已开启的模块：\n"
                for i, module_name in enumerate(enabled_modules, 1):
                    switch_text += f"{i}. 【{module_name}】\n"
                switch_text += f"\n共计 {len(enabled_modules)} 个模块"
            else:
                switch_text = f"本群（{group_id}）暂未开启任何模块"

            text_message = generate_text_message(switch_text)
            await send_group_msg(
                websocket,
                group_id,
                [reply_message, text_message],
                note="del_msg=30",
            )
        except Exception as e:
            logger.error(f"处理开关查询命令失败: {e}")

    @staticmethod
    async def handle_copy_switches_command(
        websocket, group_id, message_id, source_group_id, user_id
    ):
        """
        处理复制开关命令

        Args:
            websocket: WebSocket连接
            group_id: 目标群ID
            message_id: 消息ID
            source_group_id: 源群ID
            user_id: 用户ID
        """
        try:
            reply_message = generate_reply_message(message_id)

            # 权限检查
            if not is_system_admin(user_id):
                text_message = generate_text_message(
                    "⚠️ 只有系统管理员才能执行复制开关操作"
                )
                await send_group_msg(
                    websocket,
                    group_id,
                    [reply_message, text_message],
                    note="del_msg=10",
                )
                return

            # 验证群号格式
            if not source_group_id.isdigit():
                text_message = generate_text_message(
                    "❌ 群号格式错误，请输入纯数字群号"
                )
                await send_group_msg(
                    websocket,
                    group_id,
                    [reply_message, text_message],
                    note="del_msg=10",
                )
                return

            # 不能复制自己的开关
            if source_group_id == group_id:
                text_message = generate_text_message("❌ 不能复制本群的开关配置到本群")
                await send_group_msg(
                    websocket,
                    group_id,
                    [reply_message, text_message],
                    note="del_msg=10",
                )
                return

            # 执行复制操作
            success, copied_modules, unchanged_modules = (
                SwitchManager.copy_group_switches(source_group_id, group_id)
            )

            # 构建回复消息
            if success and copied_modules:
                copy_text = f"✅ 成功从群 {source_group_id} 复制开关配置到本群（{group_id}）\n\n📋 复制的模块开关：\n"
                for i, module_info in enumerate(copied_modules, 1):
                    copy_text += f"{i}. {module_info}\n"
                copy_text += f"\n共复制 {len(copied_modules)} 个模块开关"

                # 如果有保持不变的模块，也显示出来
                if unchanged_modules:
                    copy_text += f"\n\n🔒 保持原有配置的模块：\n"
                    for i, module_info in enumerate(unchanged_modules, 1):
                        copy_text += f"{i}. {module_info}\n"
                    copy_text += f"\n共保持 {len(unchanged_modules)} 个模块的原有配置"

            elif success and not copied_modules:
                copy_text = f"ℹ️ 群 {source_group_id} 没有任何已配置的模块开关"
            else:
                copy_text = (
                    f"❌ 复制失败，群 {source_group_id} 可能不存在或没有开关数据"
                )

            text_message = generate_text_message(copy_text)
            await send_group_msg(
                websocket,
                group_id,
                [reply_message, text_message],
                note="del_msg=60",
            )

        except Exception as e:
            logger.error(f"处理复制开关命令失败: {e}")

    @staticmethod
    async def handle_private_copy_switches_command(
        websocket, user_id, message_id, source_group_id, target_group_id
    ):
        """
        处理私聊复制开关命令

        Args:
            websocket: WebSocket连接
            user_id: 用户ID
            message_id: 消息ID
            source_group_id: 源群ID
            target_group_id: 目标群ID
        """
        try:
            reply_message = generate_reply_message(message_id)

            # 权限检查 - 只有系统管理员可以在私聊中执行复制开关操作
            if not is_system_admin(user_id):
                text_message = generate_text_message(
                    "⚠️ 只有系统管理员才能执行复制开关操作"
                )
                await send_private_msg(
                    websocket,
                    user_id,
                    [reply_message, text_message],
                    note="del_msg=10",
                )
                return

            # 验证群号格式
            if not source_group_id.isdigit() or not target_group_id.isdigit():
                text_message = generate_text_message(
                    "❌ 群号格式错误，请输入纯数字群号"
                )
                await send_private_msg(
                    websocket,
                    user_id,
                    [reply_message, text_message],
                    note="del_msg=10",
                )
                return

            # 不能复制相同的群
            if source_group_id == target_group_id:
                text_message = generate_text_message("❌ 源群和目标群不能是同一个群")
                await send_private_msg(
                    websocket,
                    user_id,
                    [reply_message, text_message],
                    note="del_msg=10",
                )
                return

            # 执行复制操作
            success, copied_modules, unchanged_modules = (
                SwitchManager.copy_group_switches(source_group_id, target_group_id)
            )

            # 构建回复消息
            if success and copied_modules:
                copy_text = f"✅ 成功从群 {source_group_id} 复制开关配置到群 {target_group_id}\n\n📋 复制的模块开关：\n"
                for i, module_info in enumerate(copied_modules, 1):
                    copy_text += f"{i}. {module_info}\n"
                copy_text += f"\n共复制 {len(copied_modules)} 个模块开关"

                # 如果有保持不变的模块，也显示出来
                if unchanged_modules:
                    copy_text += f"\n\n🔒 保持原有配置的模块：\n"
                    for i, module_info in enumerate(unchanged_modules, 1):
                        copy_text += f"{i}. {module_info}\n"
                    copy_text += f"\n共保持 {len(unchanged_modules)} 个模块的原有配置"

            elif success and not copied_modules:
                copy_text = f"ℹ️ 群 {source_group_id} 没有任何已配置的模块开关"
            else:
                copy_text = (
                    f"❌ 复制失败，群 {source_group_id} 可能不存在或没有开关数据"
                )

            text_message = generate_text_message(copy_text)
            await send_private_msg(
                websocket,
                user_id,
                [reply_message, text_message],
                note="del_msg=60",
            )

        except Exception as e:
            logger.error(f"处理私聊复制开关命令失败: {e}")

    @staticmethod
    async def handle_events(websocket, message):
        """
        统一处理 switch 命令和复制开关命令，支持群聊和私聊
        支持命令：
        群聊中：
        1. switch - 扫描本群已开启的模块
        2. 复制开关 群号 - 复制指定群号的开关配置到本群
        私聊中：
        1. 复制开关 群1 群2 - 复制群1的开关配置到群2

        Args:
            websocket: WebSocket连接
            message: 消息对象
        """
        try:
            # 只处理文本消息
            if message.get("post_type") != "message":
                return

            raw_message = message.get("raw_message", "")

            # 检查是否是支持的命令
            if not (
                raw_message.lower() == SWITCH_COMMAND
                or raw_message.startswith("复制开关 ")
            ):
                return

            # 获取基本信息
            user_id = str(message.get("user_id", ""))
            message_type = message.get("message_type", "")
            role = message.get("sender", {}).get("role", "")
            message_id = message.get("message_id", "")

            # 鉴权 - 根据消息类型进行不同的权限检查
            if message_type == "group":
                group_id = str(message.get("group_id", ""))
                # 群聊中需要是系统管理员或群管理员
                if not is_system_admin(user_id) and not is_group_admin(role):
                    return

                # 处理复制开关命令
                if raw_message.startswith("复制开关 "):
                    parts = raw_message.split(" ", 1)
                    if len(parts) != 2:
                        reply_message = generate_reply_message(message_id)
                        text_message = generate_text_message(
                            "❌ 命令格式错误，请使用：复制开关 群号"
                        )
                        await send_group_msg(
                            websocket,
                            group_id,
                            [reply_message, text_message],
                            note="del_msg=10",
                        )
                        return

                    source_group_id = parts[1].strip()
                    await SwitchCommandHandler.handle_copy_switches_command(
                        websocket, group_id, message_id, source_group_id, user_id
                    )

                # 处理 switch 查询命令
                elif raw_message.lower() == SWITCH_COMMAND:
                    await SwitchCommandHandler.handle_switch_query(
                        websocket, group_id, message_id
                    )

            elif message_type == "private":
                # 私聊中需要是系统管理员
                if not is_system_admin(user_id):
                    return

                # 私聊中只支持复制开关命令
                if raw_message.startswith("复制开关 "):
                    parts = raw_message.split(" ")
                    if len(parts) != 3:
                        reply_message = generate_reply_message(message_id)
                        text_message = generate_text_message(
                            "❌ 命令格式错误，请使用：复制开关 群1 群2"
                        )
                        await send_private_msg(
                            websocket,
                            user_id,
                            [reply_message, text_message],
                            note="del_msg=10",
                        )
                        return

                    source_group_id = parts[1].strip()
                    target_group_id = parts[2].strip()
                    await SwitchCommandHandler.handle_private_copy_switches_command(
                        websocket, user_id, message_id, source_group_id, target_group_id
                    )

        except Exception as e:
            logger.error(f"[SwitchManager]处理开关命令失败: {e}")

"""
群组管理模块
"""

import logger
from .. import (
    MODULE_NAME,
    GROUP_RECALL_COMMAND,
    SCAN_INACTIVE_USER_COMMAND,
    GROUP_TOGGLE_AUTO_APPROVE_COMMAND,
)
from api.group import (
    set_group_ban,
    set_group_kick,
    set_group_whole_ban,
    get_group_member_list,
)
from api.message import send_group_msg, delete_msg
from utils.generate import (
    generate_text_message,
    generate_at_message,
    generate_reply_message,
)
import re
import random
from .data_manager import DataManager


class GroupManagerHandle:
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.group_id = msg.get("group_id", "")
        self.user_id = msg.get("user_id", "")
        self.role = msg.get("role", "")
        self.raw_message = msg.get("raw_message", "")
        self.message_id = msg.get("message_id", "")

    async def handle_mute(self):
        """
        处理群组禁言
        支持以下格式：
            {command}[CQ:at,qq={user_id}] [CQ:at,qq={user_id}] ... 禁言时间(分钟)  # 多个at
            {command} {user_id} {user_id} ... 禁言时间(分钟)  # 多个QQ号
            {command}[CQ:at,qq={user_id}] {user_id} ... 禁言时间(分钟)  # at和QQ号混用
        """
        try:
            # 匹配所有 at 格式
            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_matches = re.finditer(at_pattern, self.raw_message)
            target_user_ids = [match.group(1) for match in at_matches]

            # 处理QQ号格式
            message_parts = self.raw_message.split()
            # 去掉命令部分,剩下的应该是QQ号和时间
            parts = [part for part in message_parts[1:] if part.isdigit()]

            # 如果最后一个数字小于1000,认为是时间参数
            if parts and int(parts[-1]) < 1000:
                mute_time = int(parts[-1])
                # 移除时间参数,剩下的都是QQ号
                parts = parts[:-1]
            else:
                mute_time = 5  # 默认5分钟

            # 添加QQ号格式的目标
            target_user_ids.extend(parts)

            # 批量执行禁言操作
            for target_user_id in target_user_ids:
                await set_group_ban(
                    self.websocket,
                    self.group_id,
                    target_user_id,
                    mute_time * 60,
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]禁言操作失败: {e}")

    async def _update_mute_record(self, user_id, duration):
        """
        更新禁言记录并通报记录

        参数:
            user_id: QQ号
            duration: 禁言时长(秒)
        """
        try:
            with DataManager() as dm:
                result = dm.update_mute_record(self.group_id, user_id, duration)
                (
                    is_new_record,
                    break_personal_record,
                    break_group_record,
                    old_duration,
                ) = result

                # 构建消息内容
                message_parts = []

                # 如果打破个人记录
                if break_personal_record:
                    message_parts.append(
                        f"恭喜 {user_id} 打破个人禁言记录！\n旧记录：{old_duration} 秒\n新记录：{duration} 秒"
                    )
                # 如果打破群记录
                elif break_group_record:
                    message_parts.append(
                        f"恭喜用户 {user_id} 打破本群今日禁言最高记录！\n时长：{duration} 秒\n🏆 新的禁言之王诞生！"
                    )
                # 如果没有打破任何记录，只显示当前禁言时长
                else:
                    message_parts.append(f"禁言时长：{duration} 秒")

                # 发送包含禁言信息的消息
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_at_message(user_id),
                        generate_text_message("\n".join(message_parts)),
                    ],
                    note="del_msg=60",
                )

                # 移除原来的禁言之王单独显示逻辑，避免重复发送
                # 现在只有在打破群记录时才会在上面的消息中显示禁言之王信息

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]更新禁言记录失败: {e}")

    async def handle_unmute(self):
        """
        处理群组解禁
        支持以下格式：
            {command}[CQ:at,qq={user_id}] [CQ:at,qq={user_id}] ...  # 多个at
            {command} {user_id} {user_id} ...  # 多个QQ号
            {command}[CQ:at,qq={user_id}] {user_id} ...  # at和QQ号混用
        """
        try:
            # 匹配所有 at 格式
            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_matches = re.finditer(at_pattern, self.raw_message)
            target_user_ids = [match.group(1) for match in at_matches]

            # 处理QQ号格式
            message_parts = self.raw_message.split()
            # 去掉命令和at部分,剩下的应该都是QQ号
            qq_numbers = [part for part in message_parts[1:] if part.isdigit()]
            target_user_ids.extend(qq_numbers)

            # 批量执行解禁操作
            for target_user_id in target_user_ids:
                await set_group_ban(self.websocket, self.group_id, target_user_id, 0)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]解禁操作失败: {e}")

    async def handle_kick(self):
        """
        处理群组踢出
        支持以下格式：
            {command}[CQ:at,qq={user_id}] [CQ:at,qq={user_id}] ...  # 多个at
            {command} {user_id} {user_id} ...  # 多个QQ号
            {command}[CQ:at,qq={user_id}] {user_id} ...  # at和QQ号混用
        """
        try:
            # 匹配所有 at 格式
            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_matches = re.finditer(at_pattern, self.raw_message)
            target_user_ids = [match.group(1) for match in at_matches]

            # 处理QQ号格式
            message_parts = self.raw_message.split()
            # 去掉命令和at部分,剩下的应该都是QQ号
            qq_numbers = [part for part in message_parts[1:] if part.isdigit()]
            target_user_ids.extend(qq_numbers)

            # 批量执行踢出操作
            for target_user_id in target_user_ids:
                await set_group_kick(
                    self.websocket, self.group_id, target_user_id, False
                )
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_text_message(f"已踢出用户\n{' '.join(target_user_ids)}"),
                ],
                note="del_msg=10",
            )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]踢出操作失败: {e}")

    async def handle_all_mute(self):
        """
        处理群组全员禁言
        """
        try:
            await set_group_whole_ban(self.websocket, self.group_id, True)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]全员禁言操作失败: {e}")

    async def handle_all_unmute(self):
        """
        处理群组全员解禁
        """
        try:
            await set_group_whole_ban(self.websocket, self.group_id, False)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]全员解禁操作失败: {e}")

    async def handle_recall(self):
        """
        处理群组撤回
        格式：[CQ:reply,id={message_id}] 任意内容 {command}
        """
        try:
            # 匹配撤回格式
            pattern = rf"\[CQ:reply,id=(\d+)\].*{GROUP_RECALL_COMMAND}"
            match = re.search(pattern, self.raw_message)
            if match:
                message_id = match.group(1)

            # 执行撤回操作
            await delete_msg(self.websocket, message_id)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]撤回操作失败: {e}")

    async def handle_ban_me(self):
        """
        处理群组封禁自己
        """
        try:
            ban_duration = random.randint(60, 600)  # 随机60-600秒(1-10分钟)
            await set_group_ban(
                self.websocket, self.group_id, self.user_id, ban_duration
            )
            # 更新禁言记录
            await self._update_mute_record(self.user_id, ban_duration)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]封禁自己操作失败: {e}")

    async def handle_mute_rank(self):
        """
        处理禁言排行榜查询
        """
        try:
            with DataManager() as dm:
                # 获取群内今日禁言排行榜
                top_user = dm.get_group_today_top_mute_user(self.group_id)

                # 获取用户自己的今日禁言时长
                user_duration = dm.get_user_today_mute_duration(
                    self.group_id, self.user_id
                )

                # 获取全局禁言记录
                global_top = dm.get_global_top_mute_user()

                # 组装消息
                message = "【禁言排行榜】\n"

                if top_user:
                    message += f"本群今日禁言之王：{top_user[0]}\n"
                    message += f"禁言时长：{top_user[1]} 秒\n\n"
                else:
                    message += "本群今日暂无禁言记录\n\n"

                if user_duration > 0:
                    message += f"您今日的禁言时长：{user_duration} 秒\n\n"
                else:
                    message += "您今日尚未被禁言\n\n"

                if global_top:
                    message += f"全服务器禁言记录保持者：\n"
                    message += f"群号：{global_top[0][:3]}***{global_top[0][-3:]}\n"
                    message += f"用户：{global_top[1][:3]}***{global_top[1][-3:]}\n"
                    message += f"日期：{global_top[2]}\n"
                    message += f"时长：{global_top[3]} 秒"
                else:
                    message += "全服务器暂无禁言记录"

                # 发送消息
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [generate_text_message(message)],
                    note="del_msg=60",
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]查询禁言排行榜失败: {e}")

    async def handle_scan_inactive_user(self):
        """
        处理扫描未活跃用户
        """
        try:
            # 解析时长参数
            pattern = r"警告未活跃用户\s+(\d+)"
            match = re.search(pattern, self.raw_message)
            if match:
                days = int(match.group(1))
            else:
                days = 30

            # 发送获取群信息请求
            await get_group_member_list(
                self.websocket,
                self.group_id,
                False,
                note=f"{SCAN_INACTIVE_USER_COMMAND}-days={days}",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]扫描未活跃用户失败: {e}")

    async def handle_set_curfew(self):
        """
        处理设置宵禁
        格式：{command} 开始时间 结束时间（24小时制），如 {command} 23:00 06:00
        """
        try:
            # 修改正则表达式以匹配起始时间和终止时间
            pattern = r"设置宵禁\s+(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})"
            match = re.search(pattern, self.raw_message)

            if not match:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_text_message(
                            "❌ 格式错误！请使用：设置宵禁 开始时间 结束时间\n示例：设置宵禁 23:00 06:00"
                        )
                    ],
                    note="del_msg=60",
                )
                return

            start_time = match.group(1)  # 起始时间，如 "23:00"
            end_time = match.group(2)  # 终止时间，如 "06:00"

            # 验证时间格式是否正确
            def validate_time(time_str):
                try:
                    hour, minute = map(int, time_str.split(":"))
                    return 0 <= hour <= 23 and 0 <= minute <= 59
                except ValueError:
                    return False

            if not validate_time(start_time) or not validate_time(end_time):
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            "❌ 时间格式错误！请使用24小时制，如：23:00"
                        ),
                    ],
                    note="del_msg=60",
                )
                return

            # 保存宵禁设置到数据库
            with DataManager() as dm:
                success = dm.set_curfew_settings(
                    self.group_id, start_time, end_time, True
                )

                if success:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_text_message(
                                f"✅ 宵禁时间设置成功！\n🕐 开始时间：{start_time}\n🕕 结束时间：{end_time}\n📋 状态：已启用"
                            )
                        ],
                        note="del_msg=60",
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [generate_text_message("❌ 宵禁设置保存失败，请稍后重试")],
                        note="del_msg=60",
                    )

        except Exception as e:
            await send_group_msg(
                self.websocket,
                self.group_id,
                [generate_text_message(f"❌ 设置宵禁失败：{str(e)}")],
                note="del_msg=60",
            )

    async def handle_toggle_curfew(self):
        """
        处理切换宵禁开关
        """
        try:
            with DataManager() as dm:
                new_status = dm.toggle_curfew_status(self.group_id)

                if new_status is None:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_text_message(
                                "❌ 该群尚未设置宵禁时间，请先使用 '设置宵禁' 命令"
                            )
                        ],
                        note="del_msg=60",
                    )
                else:
                    status_text = "已启用" if new_status else "已禁用"
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_text_message(
                                f"✅ 宵禁功能切换成功！\n📋 当前状态：{status_text}"
                            )
                        ],
                        note="del_msg=60",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]切换宵禁状态失败: {e}")

    async def handle_query_curfew(self):
        """
        处理查询宵禁设置
        """
        try:
            with DataManager() as dm:
                settings = dm.get_curfew_settings(self.group_id)

                if settings is None:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [generate_text_message("ℹ️ 该群尚未设置宵禁时间")],
                        note="del_msg=60",
                    )
                else:
                    start_time, end_time, is_enabled = settings
                    status_text = "已启用" if is_enabled else "已禁用"
                    is_current_curfew = dm.is_curfew_time(self.group_id)
                    current_status = (
                        "🌙 当前在宵禁时间内"
                        if is_current_curfew
                        else "☀️ 当前不在宵禁时间内"
                    )

                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_text_message(
                                f"📋 当前宵禁设置：\n"
                                f"🕐 开始时间：{start_time}\n"
                                f"🕕 结束时间：{end_time}\n"
                                f"📊 状态：{status_text}\n"
                                f"{current_status}"
                            )
                        ],
                        note="del_msg=60",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]查询宵禁设置失败: {e}")

    async def handle_delete_curfew(self):
        """
        处理删除宵禁设置
        """
        try:
            with DataManager() as dm:
                success = dm.delete_curfew_settings(self.group_id)

                if success:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [generate_text_message("✅ 宵禁设置已删除")],
                        note="del_msg=60",
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [generate_text_message("❌ 删除宵禁设置失败")],
                        note="del_msg=60",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]删除宵禁设置失败: {e}")

    async def handle_cancel_curfew(self):
        """
        处理取消宵禁设置
        """
        try:
            with DataManager() as dm:
                # 先检查是否有宵禁设置
                settings = dm.get_curfew_settings(self.group_id)

                if settings is None:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [generate_text_message("ℹ️ 该群尚未设置宵禁时间，无需取消")],
                        note="del_msg=60",
                    )
                    return

                # 删除宵禁设置
                success = dm.delete_curfew_settings(self.group_id)

                if success:
                    start_time, end_time, is_enabled = settings
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_text_message(
                                f"✅ 宵禁设置已成功取消！\n"
                                f"🗑️ 已删除配置：{start_time} - {end_time}\n"
                                f"📋 宵禁功能已彻底关闭"
                            )
                        ],
                        note="del_msg=60",
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [generate_text_message("❌ 取消宵禁设置失败，请稍后重试")],
                        note="del_msg=60",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]取消宵禁设置失败: {e}")
            await send_group_msg(
                self.websocket,
                self.group_id,
                [generate_text_message(f"❌ 取消宵禁失败：{str(e)}")],
                note="del_msg=60",
            )

    async def handle_auto_approve(self):
        """
        处理自动同意入群开关
        """
        try:
            with DataManager() as dm:
                if self.raw_message.startswith(GROUP_TOGGLE_AUTO_APPROVE_COMMAND):
                    # 开启自动同意入群
                    success = dm.set_auto_approve_status(self.group_id, True)
                    if success:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [generate_text_message("✅ 自动同意入群已开启")],
                            note="del_msg=60",
                        )
                    else:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [generate_text_message("❌ 开启自动同意入群失败")],
                            note="del_msg=60",
                        )
                elif self.raw_message.startswith(GROUP_TOGGLE_AUTO_APPROVE_COMMAND):
                    # 关闭自动同意入群
                    success = dm.set_auto_approve_status(self.group_id, False)
                    if success:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [generate_text_message("✅ 自动同意入群已关闭")],
                            note="del_msg=60",
                        )
                    else:
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [generate_text_message("❌ 关闭自动同意入群失败")],
                            note="del_msg=60",
                        )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理自动同意入群失败: {e}")
            await send_group_msg(
                self.websocket,
                self.group_id,
                [generate_text_message(f"❌ 操作失败：{str(e)}")],
                note="del_msg=60",
            )

    async def handle_toggle_auto_approve(self):
        """
        处理切换自动同意入群开关
        """
        try:
            with DataManager() as dm:
                # 获取当前状态并切换
                current_status = dm.get_auto_approve_status(self.group_id)
                new_status = dm.toggle_auto_approve_status(self.group_id)

                if new_status != current_status:  # 确认状态确实发生了改变
                    status_text = "已开启" if new_status else "已关闭"
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_text_message(
                                f"✅ 自动同意入群功能切换成功！\n📋 当前状态：{status_text}"
                            )
                        ],
                        note="del_msg=60",
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [generate_text_message("❌ 切换自动同意入群状态失败")],
                        note="del_msg=60",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]切换自动同意入群状态失败: {e}")
            await send_group_msg(
                self.websocket,
                self.group_id,
                [generate_text_message(f"❌ 操作失败：{str(e)}")],
                note="del_msg=60",
            )

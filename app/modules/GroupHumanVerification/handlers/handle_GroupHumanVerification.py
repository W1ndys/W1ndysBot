from datetime import datetime
import asyncio
import logger
from .data_manager import DataManager
from .. import (
    MODULE_NAME,
    SCAN_VERIFICATION,
    STATUS_KICKED,
    STATUS_VERIFIED,
    WARNING_COUNT,
    BAN_TIME,
)
from api.group import set_group_kick, set_group_ban
from api.message import send_group_msg, send_private_msg, delete_msg
from utils.generate import generate_text_message, generate_at_message
from config import OWNER_ID
import re


class GroupHumanVerificationHandler:
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.sub_type = msg.get("sub_type", "")  # 子类型,friend/group
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.group_id = str(msg.get("group_id", ""))  # 群组ID
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.message = msg.get("message", {})  # 消息段数组
        self.raw_message = msg.get("raw_message", "")  # 原始消息
        self.sender = msg.get("sender", {})  # 发送者信息
        self.nickname = self.sender.get("nickname", "")  # 昵称

    async def handle_scan_verification(self):
        """
        处理扫描入群验证
        """
        try:
            with DataManager() as dm:
                unverified_users = dm.get_all_unverified_users_with_code_and_warning()
                result_msgs = []
                if unverified_users:
                    # 创建任务列表
                    tasks = []
                    for group_id, user_list in unverified_users.items():
                        # 为每个群创建单独的任务
                        task = asyncio.create_task(
                            self._process_single_group(
                                group_id, user_list, dm, result_msgs
                            )
                        )
                        tasks.append(task)

                    # 等待所有任务完成
                    await asyncio.gather(*tasks)

                    # 发送最终结果
                    if result_msgs:
                        msg = "\n".join(result_msgs)
                        await send_private_msg(
                            self.websocket, OWNER_ID, f"[扫描验证结果]\n{msg}"
                        )
                    else:
                        await send_private_msg(
                            self.websocket,
                            OWNER_ID,
                            "[扫描验证结果] 当前无未验证用户",
                        )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理扫描入群验证失败: {e}")

    async def handle_scan_verification_by_time(self):
        """
        基于时间间隔处理扫描入群验证（每4小时提醒一次）
        """
        try:
            with DataManager() as dm:
                users_need_warning = dm.get_users_need_warning_by_time()
                if users_need_warning:
                    # 为每个群创建独立的异步任务，不等待结果
                    for group_id, user_list in users_need_warning.items():
                        # 创建独立的异步任务，每个群独立执行
                        asyncio.create_task(
                            self._process_single_group_by_time_independent(
                                group_id, user_list
                            )
                        )
                else:
                    # 不再发送"无未验证用户"消息，避免频繁通知
                    logger.info(f"[{MODULE_NAME}]当前无需要定时提醒的用户")
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理基于时间的扫描入群验证失败: {e}")

    async def _process_single_group(self, group_id, user_list, dm, result_msgs):
        """处理单个群的验证扫描"""
        try:
            await send_private_msg(
                self.websocket,
                OWNER_ID,
                generate_text_message(f"正在扫描群{group_id}未验证用户"),
                note="del_msg=10",
            )
            await asyncio.sleep(0.05)
            # 记录需要踢出的用户
            kick_users = []
            # 记录需要提醒的用户消息（每行@和文本分开生成，合成列表）
            warning_msg_list = []
            for user_id, warning_count, code in user_list:
                # 重新禁言未验证用户
                await set_group_ban(self.websocket, group_id, user_id, BAN_TIME)

                if warning_count > 1:
                    dm.update_warning_count(group_id, user_id, warning_count - 1)
                    # 每行用generate_at_message和generate_text_message生成
                    warning_msg_list.append(generate_at_message(user_id))
                    warning_msg_list.append(
                        generate_text_message(
                            f"({user_id})请尽快私聊我验证码【{code}】（剩余警告{warning_count - 1}/{WARNING_COUNT}）\n\n"
                        )
                    )
                    # 统计
                    result_msgs.append(
                        f"群{group_id} 用户{user_id} 警告-1，剩余{warning_count-1}"
                    )
                else:
                    # 警告次数为0，踢群并标记为超时
                    kick_users.append(user_id)
                    result_msgs.append(
                        f"群{group_id} 用户{user_id} 已被踢出（警告用尽）"
                    )
                await asyncio.sleep(0.05)  # 释放控制权
            # 合并提醒消息，一次性发到群里（每行@和文本分开生成，合成列表）
            if warning_msg_list:
                await send_group_msg(self.websocket, group_id, warning_msg_list)
            # 依次踢出需要踢出的用户前，群内合并通知
            if kick_users:
                message = []
                for user_id in kick_users:
                    message.extend(
                        [
                            generate_at_message(user_id),
                            generate_text_message(f"({user_id})，"),
                        ]
                    )
                message.append(
                    generate_text_message("以上用户已超过警告次数，即将被踢出群聊")
                )
                await send_group_msg(
                    self.websocket,
                    group_id,
                    message,
                    note="del_msg=60",
                )
            for user_id in kick_users:
                await set_group_kick(self.websocket, group_id, user_id)
                dm.update_status(group_id, user_id, STATUS_KICKED)
                # 踢人操作间隔1秒，防止风控
                await asyncio.sleep(1)

            # 释放控制权
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群{group_id}扫描失败: {e}")

    async def _process_single_group_by_time(self, group_id, user_list, dm, result_msgs):
        """基于时间处理单个群的验证扫描"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 记录需要踢出的用户
            kick_users = []
            # 记录需要提醒的用户消息
            warning_msg_list = []

            for (
                user_id,
                warning_count,
                code,
                created_at,
                last_warning_time,
            ) in user_list:
                # 重新禁言未验证用户
                await set_group_ban(self.websocket, group_id, user_id, BAN_TIME)

                if warning_count > 1:
                    # 减少警告次数并更新最后警告时间
                    dm.update_warning_count(group_id, user_id, warning_count - 1)
                    dm.update_last_warning_time(group_id, user_id, current_time)

                    # 计算入群时长用于显示
                    try:
                        join_time = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                        hours_since_join = int(
                            (datetime.now() - join_time).total_seconds() / 3600
                        )

                        # 每行用generate_at_message和generate_text_message生成
                        warning_msg_list.append(generate_at_message(user_id))
                        warning_msg_list.append(
                            generate_text_message(
                                f"({user_id})已入群{hours_since_join}小时，请尽快私聊我验证码【{code}】（剩余警告{warning_count - 1}/{WARNING_COUNT}）\n\n"
                            )
                        )
                        # 统计
                        result_msgs.append(
                            f"群{group_id} 用户{user_id} 入群{hours_since_join}h 警告-1，剩余{warning_count-1}"
                        )
                    except ValueError:
                        # 时间解析失败，使用原有格式
                        warning_msg_list.append(generate_at_message(user_id))
                        warning_msg_list.append(
                            generate_text_message(
                                f"({user_id})请尽快私聊我验证码【{code}】（剩余警告{warning_count - 1}/{WARNING_COUNT}）\n\n"
                            )
                        )
                        result_msgs.append(
                            f"群{group_id} 用户{user_id} 警告-1，剩余{warning_count-1}"
                        )
                else:
                    # 警告次数为0，踢群并标记为超时
                    kick_users.append(user_id)
                    result_msgs.append(
                        f"群{group_id} 用户{user_id} 已被踢出（警告用尽）"
                    )
                await asyncio.sleep(0.05)  # 释放控制权

            # 合并提醒消息，一次性发到群里
            if warning_msg_list:
                await send_group_msg(
                    self.websocket,
                    group_id,
                    warning_msg_list,
                    note="del_msg=14400",
                )

            # 依次踢出需要踢出的用户前，群内合并通知
            if kick_users:
                message = []
                for user_id in kick_users:
                    message.extend(
                        [
                            generate_at_message(user_id),
                            generate_text_message(f"({user_id})，"),
                        ]
                    )
                message.append(
                    generate_text_message("以上用户已超过警告次数，即将被踢出群聊")
                )
                await send_group_msg(
                    self.websocket,
                    group_id,
                    message,
                    note="del_msg=60",
                )

            for user_id in kick_users:
                await set_group_kick(self.websocket, group_id, user_id)
                dm.update_status(group_id, user_id, STATUS_KICKED)

            # 释放控制权
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]基于时间处理群{group_id}扫描失败: {e}")

    async def _process_single_group_by_time_independent(self, group_id, user_list):
        """基于时间处理单个群的验证扫描（独立异步任务）"""
        try:
            # 创建独立的数据库连接
            with DataManager() as dm:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result_msgs = []

                # 记录需要踢出的用户
                kick_users = []
                # 记录需要提醒的用户消息
                warning_msg_list = []

                for (
                    user_id,
                    warning_count,
                    code,
                    created_at,
                    last_warning_time,
                ) in user_list:
                    # 重新禁言未验证用户
                    await set_group_ban(self.websocket, group_id, user_id, BAN_TIME)

                    if warning_count > 1:
                        # 减少警告次数并更新最后警告时间
                        dm.update_warning_count(group_id, user_id, warning_count - 1)
                        dm.update_last_warning_time(group_id, user_id, current_time)

                        # 计算入群时长用于显示
                        try:
                            join_time = datetime.strptime(
                                created_at, "%Y-%m-%d %H:%M:%S"
                            )
                            hours_since_join = int(
                                (datetime.now() - join_time).total_seconds() / 3600
                            )

                            # 每行用generate_at_message和generate_text_message生成
                            warning_msg_list.append(generate_at_message(user_id))
                            warning_msg_list.append(
                                generate_text_message(
                                    f"({user_id})已入群{hours_since_join}小时，请尽快私聊我验证码【{code}】（剩余警告{warning_count - 1}/{WARNING_COUNT}）\n\n"
                                )
                            )
                            # 统计
                            result_msgs.append(
                                f"用户{user_id} 入群{hours_since_join}h 警告-1，剩余{warning_count-1}"
                            )
                        except ValueError:
                            # 时间解析失败，使用原有格式
                            warning_msg_list.append(generate_at_message(user_id))
                            warning_msg_list.append(
                                generate_text_message(
                                    f"({user_id})请尽快私聊我验证码【{code}】（剩余警告{warning_count - 1}/{WARNING_COUNT}）\n\n"
                                )
                            )
                            result_msgs.append(
                                f"用户{user_id} 警告-1，剩余{warning_count-1}"
                            )
                    else:
                        # 警告次数为0，踢群并标记为超时
                        kick_users.append(user_id)
                        result_msgs.append(f"用户{user_id} 已被踢出（警告用尽）")
                    await asyncio.sleep(0.05)  # 释放控制权

                # 合并提醒消息，一次性发到群里
                if warning_msg_list:
                    await send_group_msg(
                        self.websocket,
                        group_id,
                        warning_msg_list,
                        note="del_msg=14400",
                    )

                # 依次踢出需要踢出的用户前，群内合并通知
                if kick_users:
                    message = []
                    for user_id in kick_users:
                        message.extend(
                            [
                                generate_at_message(user_id),
                                generate_text_message(f"({user_id})，"),
                            ]
                        )
                    message.append(
                        generate_text_message("以上用户已超过警告次数，即将被踢出群聊")
                    )
                    await send_group_msg(
                        self.websocket,
                        group_id,
                        message,
                        note="del_msg=60",
                    )

                for user_id in kick_users:
                    await set_group_kick(self.websocket, group_id, user_id)
                    dm.update_status(group_id, user_id, STATUS_KICKED)
                    # 踢人操作间隔1秒，防止风控
                    await asyncio.sleep(1)

                # 单独向管理员上报本群的处理结果
                if result_msgs:
                    msg = "\n".join(result_msgs)
                    await send_private_msg(
                        self.websocket, OWNER_ID, f"[定时验证提醒] 群{group_id}:\n{msg}"
                    )

                # 释放控制权
                await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]独立处理群{group_id}扫描失败: {e}")
            # 发生异常时也向管理员报告
            await send_private_msg(
                self.websocket,
                OWNER_ID,
                f"[定时验证提醒] 群{group_id}处理失败: {str(e)}",
            )

    async def handle_scan_verification_group_only(self):
        """
        仅扫描当前群聊未验证成员并在群内警告，无需私聊通知。
        """
        try:
            # 发出提示
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_text_message(f"正在扫描当前群未验证用户"),
                ],
                note="del_msg=10",
            )
            await asyncio.sleep(0.5)
            with DataManager() as dm:
                unverified_users = dm.get_all_unverified_users_with_code_and_warning()
                result_msgs = []
                group_id = self.group_id
                if group_id and group_id in unverified_users:
                    user_list = unverified_users[group_id]
                    kick_users = []
                    warning_msg_list = []
                    for user_id, warning_count, code in user_list:
                        # 重新禁言未验证用户
                        await set_group_ban(self.websocket, group_id, user_id, BAN_TIME)

                        if warning_count > 1:
                            dm.update_warning_count(
                                group_id, user_id, warning_count - 1
                            )
                            warning_msg_list.append(generate_at_message(user_id))
                            warning_msg_list.append(
                                generate_text_message(
                                    f"({user_id})请尽快私聊我验证码【{code}】（剩余警告{warning_count - 1}/{WARNING_COUNT}）\n\n"
                                )
                            )
                            result_msgs.append(
                                f"用户{user_id} 警告-1，剩余{warning_count-1}"
                            )
                        else:
                            kick_users.append(user_id)
                            result_msgs.append(f"用户{user_id} 已被踢出（警告用尽）")
                    if warning_msg_list:
                        await send_group_msg(self.websocket, group_id, warning_msg_list)
                    if kick_users:
                        message = []
                        for user_id in kick_users:
                            message.extend(
                                [
                                    generate_at_message(user_id),
                                    generate_text_message(f"({user_id})"),
                                ]
                            )
                        message.append(
                            generate_text_message(
                                "以上用户已超过警告次数，即将被踢出群聊"
                            )
                        )
                        await send_group_msg(
                            self.websocket,
                            group_id,
                            message,
                            note="del_msg=30",
                        )
                    for user_id in kick_users:
                        dm.update_status(group_id, user_id, STATUS_KICKED)
                        await set_group_kick(self.websocket, group_id, user_id)
                        await asyncio.sleep(1)
                    await asyncio.sleep(1)
                else:
                    await send_group_msg(
                        self.websocket,
                        group_id,
                        [
                            generate_at_message(self.user_id),
                            generate_text_message(
                                f"({self.user_id})当前群无未验证用户"
                            ),
                        ],
                        note="del_msg=10",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]群内扫描入群验证失败: {e}")

    async def handle_admin_command(self):
        """
        处理管理员命令
        """
        try:
            # 鉴权
            if self.user_id != OWNER_ID:
                return

            # 处理扫描入群验证
            if self.raw_message.startswith(SCAN_VERIFICATION):
                await self.handle_scan_verification()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理管理员命令失败: {e}")

    async def handle_user_command(self):
        """
        处理用户命令，自动从文本中提取UUID验证码
        """
        try:
            # 使用正则表达式提取所有UUID字符串
            uuid_pattern = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
            uuids = re.findall(uuid_pattern, self.raw_message)
            if not uuids:
                # 没有找到UUID，直接返回
                return

            with DataManager() as dm:
                verified = False
                # 有群号时，优先用群号和用户ID检测验证码
                if self.group_id:
                    code = dm.get_code_with_group_and_user(self.group_id, self.user_id)
                    if code and code in uuids:
                        dm.update_status(self.group_id, self.user_id, STATUS_VERIFIED)
                        msg_at = generate_at_message(self.user_id)
                        msg_text = generate_text_message(
                            f"({self.user_id}) 你在群 {self.group_id} 的验证已通过，你可以正常发言了！"
                        )
                        # 解除禁言
                        await set_group_ban(
                            self.websocket, self.group_id, self.user_id, 0
                        )
                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [msg_at, msg_text],
                            note="del_msg=60",
                        )
                        # 撤回验证码消息
                        message_id = dm.get_message_id(self.group_id, self.user_id)
                        if message_id:
                            await delete_msg(self.websocket, message_id)

                        verified = True
                # 如果没有群号，或者上面未通过，则遍历提取到的所有UUID，查找该用户在所有群的未验证状态
                if not verified:
                    for uuid_code in uuids:
                        group_id = dm.get_group_with_code_and_user(
                            self.user_id, uuid_code
                        )
                        if group_id:
                            # 找到未验证的群，更新其状态
                            dm.update_status(group_id, self.user_id, STATUS_VERIFIED)
                            msg_at = generate_at_message(self.user_id)
                            msg_text = generate_text_message(
                                f"({self.user_id}) 你在群 {group_id} 的验证已通过，你可以正常发言了！"
                            )
                            # 解除禁言
                            await set_group_ban(
                                self.websocket, group_id, self.user_id, 0
                            )
                            await send_group_msg(
                                self.websocket,
                                group_id,
                                [msg_at, msg_text],
                                note="del_msg=60",
                            )
                            # 撤回验证码消息
                            message_id = dm.get_message_id(group_id, self.user_id)
                            if message_id:
                                await delete_msg(self.websocket, message_id)

                            verified = True
                            break  # 只处理一个群
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理用户命令失败: {e}")

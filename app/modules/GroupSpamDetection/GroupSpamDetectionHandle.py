from collections import defaultdict
from . import MODULE_NAME
import logger
from api.group import set_group_ban
from api.message import send_group_msg
from api.generate import generate_text_message, generate_at_message


class GroupSpamDetectionHandle:
    # 类属性，用于存储群消息的时间戳和内容
    message_timestamps = defaultdict(lambda: defaultdict(list))
    message_contents = defaultdict(lambda: defaultdict(list))
    # 新增：记录每个群每个用户上次警告的分钟
    warned_users_minute = defaultdict(lambda: defaultdict(int))

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.group_id = str(msg.get("group_id", ""))  # 群号
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.raw_message = str(msg.get("raw_message", ""))  # 原始消息

        # 垃圾消息检测阈值
        self.spam_threshold = 5  # 消息数量阈值
        self.spam_time_window = 1.0  # 时间窗口(秒)
        self.identical_message_threshold = 3  # 相同消息数量阈值
        self.ban_minutes = 1  # 禁言分钟数

    async def handle_message(self):
        """
        缓存群消息数据，检测垃圾消息
        """
        try:
            # 1. 缓存消息时间戳
            timestamps = GroupSpamDetectionHandle.message_timestamps[self.group_id][
                self.user_id
            ]
            contents = GroupSpamDetectionHandle.message_contents[self.group_id][
                self.user_id
            ]
            now = float(self.time)
            timestamps.append(now)
            contents.append(self.raw_message)

            # 获取当前分钟
            current_minute = int(now // 60)
            warned_minute = GroupSpamDetectionHandle.warned_users_minute[self.group_id][
                self.user_id
            ]

            def should_warn():
                # 只在本分钟未警告过才允许警告
                return warned_minute != current_minute

            # 高频消息检测
            # 移除时间窗口外的消息
            while timestamps and now - timestamps[0] > self.spam_time_window:
                timestamps.pop(0)
            if len(timestamps) >= self.spam_threshold and should_warn():
                # 触发高频消息刷屏
                logger.info(
                    f"[{MODULE_NAME}] 用户{self.user_id}在群{self.group_id} 1秒内发送{len(timestamps)}条消息，疑似刷屏。"
                )
                # 禁言加警告
                await set_group_ban(
                    self.websocket, self.group_id, self.user_id, self.ban_minutes * 60
                )
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_at_message(self.user_id),
                        generate_text_message(f"({self.user_id})"),
                        generate_text_message("禁止刷屏，请注意发言频率"),
                    ],
                    note="del_msg=120",
                )
                # 记录本分钟已警告
                GroupSpamDetectionHandle.warned_users_minute[self.group_id][
                    self.user_id
                ] = current_minute

            # 重复消息检测
            if len(contents) >= self.identical_message_threshold and should_warn():
                # 检查最后N条是否完全相同
                last_msgs = contents[-self.identical_message_threshold :]
                if all(msg == last_msgs[0] for msg in last_msgs):
                    logger.info(
                        f"[{MODULE_NAME}] 用户{self.user_id}在群{self.group_id} 连续发送{self.identical_message_threshold}条相同消息，疑似刷屏。"
                    )
                    # 禁言加警告
                    await set_group_ban(
                        self.websocket,
                        self.group_id,
                        self.user_id,
                        self.ban_minutes * 60,
                    )
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_at_message(self.user_id),
                            generate_text_message(f"({self.user_id})"),
                            generate_text_message("禁止刷屏，请注意发言频率"),
                        ],
                        note="del_msg=120",
                    )
                    # 记录本分钟已警告
                    GroupSpamDetectionHandle.warned_users_minute[self.group_id][
                        self.user_id
                    ] = current_minute
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 群垃圾消息检测处理异常: {e}")

import asyncio
from datetime import datetime
import re
from .. import (
    MODULE_NAME,
    BAN_WORD_WEIGHT_MAX,
    BAN_WORD_DURATION,
    UNBAN_WORD_COMMAND,
    KICK_BAN_WORD_COMMAND,
)

from api.message import (
    send_group_msg,
    delete_msg,
    send_private_msg,
    get_group_msg_history,
)
from utils.generate import generate_text_message, generate_at_message
from api.group import set_group_ban
from config import OWNER_ID
from utils.feishu import send_feishu_msg
from .data_manager_words import DataManager
from core.get_group_list import get_group_name_by_id


async def check_and_handle_ban_words(
    websocket,
    group_id,
    user_id,
    message_id,
    raw_message,
    formatted_time=None,
):
    """
    检测违禁词并处理相关逻辑

    Args:
        websocket: WebSocket连接对象
        group_id: 群号
        user_id: 用户ID
        message_id: 消息ID
        raw_message: 原始消息
        formatted_time: 格式化时间，默认为None，会自动生成当前时间

    Returns:
        bool: 是否触发违禁词
    """
    if not formatted_time:
        formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data_manager = DataManager(group_id)

    # 过滤图片CQ码和视频CQ码
    raw_message = re.sub(r"\[CQ:image,.*?\]", "", raw_message)
    raw_message = re.sub(r"\[CQ:video,.*?\]", "", raw_message)

    # 文本预处理
    # 删除所有空格，换行符，制表符
    raw_message = (
        raw_message.replace(" ", "")
        .replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
    )
    # 删除所有中文标点符号
    raw_message = re.sub(
        r"[，。！？；：\'‘’“”【】「」『』（）《》〈〉…—～·、]", "", raw_message
    )
    # 删除所有英文标点符号
    raw_message = re.sub(r'[,.:;!?\'"()\[\]{}<>—~`]', "", raw_message)

    # 过滤后的消息
    print(f"过滤后的消息: {raw_message}")

    # 计算违禁词权重
    total_weight, matched_words = data_manager.calc_message_weight(raw_message)
    is_banned = total_weight >= BAN_WORD_WEIGHT_MAX

    if is_banned:
        # 返回True，表示违规
        # 发送请求获取本群历史消息记录，以便于在回应处理函数中处理
        await get_group_msg_history(
            websocket,
            group_id,
            count=15,
            message_seq=0,
            note=f"GroupBanWords-group_id={group_id}-is_banned_user_id={user_id}",
        )
        await set_group_ban(
            websocket,
            group_id,
            user_id,
            BAN_WORD_DURATION,
        )
        # 撤回消息
        await delete_msg(websocket, message_id)
        # 设置用户状态
        data_manager.set_user_status(user_id, "ban")

        # 发送管理员消息和飞书消息、群内消息
        # 构建共同的消息内容
        common_content = (
            f"时间: {formatted_time}\n"
            f"group_id={group_id}\n"
            f"group_name={get_group_name_by_id(group_id)}\n"
            f"user_id={user_id}\n"
            f"涉及违禁词: {', '.join(f'{word}（{weight}）' for word, weight in matched_words)}"
        )

        admin_msg_content = (
            f"检测到违禁消息\n"
            f"{common_content}\n"
            f"相关消息已通过飞书上报\n"
            f"引用回复本消息【{UNBAN_WORD_COMMAND}】或【{KICK_BAN_WORD_COMMAND}】来处理用户"
        )

        feishu_msg_content = f"{common_content}\n" f"raw_message={raw_message}"

        await send_private_msg(
            websocket,
            OWNER_ID,
            [
                generate_text_message(f"[{MODULE_NAME}]"),
                generate_text_message(admin_msg_content),
            ],
        )

        send_feishu_msg(
            title=f"检测到违禁词",
            content=feishu_msg_content,
        )

        await send_group_msg(
            websocket,
            group_id,
            [
                generate_text_message(f"[{MODULE_NAME}]"),
                generate_at_message(user_id),
                generate_text_message(
                    f"({user_id})请勿发送违禁消息，如误封请联系管理员，发广告的自觉点退群\n"
                    f"时间: {formatted_time}\n"
                    f"group_id={group_id}\n"
                    f"group_name={get_group_name_by_id(group_id)}\n"
                    f"user_id={user_id}\n"
                    f"管理员可回复本消息【{UNBAN_WORD_COMMAND}】或【{KICK_BAN_WORD_COMMAND}】来处理用户"
                ),
            ],
        )
        return True
    else:
        # 检测用户状态
        user_status = data_manager.get_user_status(user_id)
        if user_status == "ban":
            # 撤回消息
            await delete_msg(websocket, message_id)
            # 禁言
            await set_group_ban(
                websocket,
                group_id,
                user_id,
                BAN_WORD_DURATION,
            )
            return True
    return False

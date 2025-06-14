import asyncio
from datetime import datetime
from . import (
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
from api.generate import generate_text_message, generate_at_message
from api.group import set_group_ban
from config import OWNER_ID
from utils.feishu import send_feishu_msg
from .data_manager_words import DataManager


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
    # 计算违禁词权重
    total_weight, matched_words = data_manager.calc_message_weight(raw_message)
    is_banned = total_weight >= BAN_WORD_WEIGHT_MAX

    if is_banned:
        # 返回True，表示违规
        # 发送请求获取本群历史消息记录，以便于在回应处理函数中处理
        await get_group_msg_history(
            websocket,
            group_id,
            count=20,
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
        # 发送警告消息
        await send_group_msg(
            websocket,
            group_id,
            [
                generate_at_message(user_id),
                generate_text_message(
                    f"({user_id})请勿发送违禁消息，如误封请联系管理员"
                ),
            ],
            note="del_msg=20",
        )
        # 发送管理员消息
        await send_private_msg(
            websocket,
            OWNER_ID,
            [
                generate_text_message(
                    f"[{formatted_time}]\n"
                    f"群{group_id}用户{user_id}发送违禁词\n"
                    f"已封禁{BAN_WORD_DURATION}秒\n"
                    f"涉及违禁词: {', '.join(f'{word}（{weight}）' for word, weight in matched_words)}\n"
                    f"相关消息已通过飞书上报\n"
                    f"发送{UNBAN_WORD_COMMAND} {group_id} {user_id}解封用户\n"
                    f"发送{KICK_BAN_WORD_COMMAND} {group_id} {user_id}踢出用户"
                )
            ],
        )

        # 异步延迟0.3秒
        await asyncio.sleep(0.3)

        # 发送快速命令便于复制
        await send_private_msg(
            websocket,
            OWNER_ID,
            [generate_text_message(f"{UNBAN_WORD_COMMAND} {group_id} {user_id}")],
        )
        await asyncio.sleep(0.3)
        await send_private_msg(
            websocket,
            OWNER_ID,
            [generate_text_message(f"{KICK_BAN_WORD_COMMAND} {group_id} {user_id}")],
        )

        # 发送飞书消息
        send_feishu_msg(
            title=f"触发违禁词",
            content=f"时间: {formatted_time}\n"
            f"群{group_id}用户{user_id}发送违禁词\n"
            f"已封禁{BAN_WORD_DURATION}秒\n"
            f"涉及违禁词: {', '.join(f'{word}（{weight}）' for word, weight in matched_words)}\n"
            f"原始消息: {raw_message}",
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

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
    user_name=None,
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

    # 检查用户是否在白名单中
    if data_manager.is_user_whitelisted(user_id):
        return False

    # 如果用户是ban状态，直接禁言撤回
    if data_manager.get_user_status(user_id) == "ban":
        await delete_msg(websocket, message_id)
        await set_group_ban(
            websocket,
            group_id,
            user_id,
            BAN_WORD_DURATION,
        )
        return True

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

    # 过滤后的消息
    print(f"过滤后的消息: {raw_message}")

    # 计算违禁词权重
    total_weight, matched_words = data_manager.calc_message_weight(raw_message)
    is_banned = total_weight >= BAN_WORD_WEIGHT_MAX

    if is_banned:
        from ...InviteTreeRecord.handlers import (
            data_manager as invite_tree_record_data_manager,
        )

        # 获取邀请树信息
        invite_chain_info = ""
        try:
            # 伪造一个msg
            fake_msg = {"group_id": group_id}
            with invite_tree_record_data_manager.InviteTreeRecordDataManager(
                websocket, fake_msg
            ) as itrdm:
                related_users = itrdm.get_related_invite_users(user_id)
                if len(related_users) > 1:
                    invite_chain_info = (
                        f"该用户邀请树相关人员：\n {'  '.join(map(str, related_users))}"
                    )

        except Exception:
            pass

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
            f"group_name={get_group_name_by_id(group_id)}\n"
            f"group_id={group_id}\n"
            f"user_name={user_name}\n"
            f"user_id={user_id}\n"
            f"涉及违禁词: {', '.join(f'{word}（{weight}）' for word, weight in matched_words)}"
        )

        # 如果有邀请树信息，添加到共同内容中
        if invite_chain_info:
            common_content += f"\n{invite_chain_info}"

        admin_msg_content = f"检测到违禁消息\n" f"{common_content}\n"

        feishu_msg_content = f"{common_content}\n"
        feishu_msg_content += f"raw_message={raw_message}"

        await send_private_msg(
            websocket,
            OWNER_ID,
            [
                generate_text_message(admin_msg_content),
            ],
        )

        # 单独构建拉黑相关人员的命令给owner上报
        related_users_msg = f"拉黑 {' '.join(map(str, related_users))}"
        await send_private_msg(
            websocket,
            OWNER_ID,
            [
                generate_text_message(related_users_msg),
            ],
        )

        send_feishu_msg(
            title=f"检测到违禁词",
            content=feishu_msg_content,
        )

        # 修改群内播报格式
        group_msg_content = (
            f"检测到违禁消息！\n"
            f"触发违禁词 {len(matched_words)} 个\n"
            f"总权值 {total_weight} 点\n"
            f"相关人员: {', '.join(map(str, related_users))}"
        )

        if group_id in ["616745113"]:  # 需要主动撤回的群
            await send_group_msg(
                websocket,
                group_id,
                [
                    generate_at_message(user_id),
                    generate_text_message(f"({user_id})\n"),
                    generate_text_message(group_msg_content),
                ],
                note="del_msg=60",
            )
        else:
            await send_group_msg(
                websocket,
                group_id,
                [
                    generate_at_message(user_id),
                    generate_text_message(f"({user_id})\n"),
                    generate_text_message(group_msg_content),
                ],
                note="del_msg=86400",
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

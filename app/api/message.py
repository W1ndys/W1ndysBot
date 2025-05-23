import asyncio
import json
import logger


# 使用cq码发送群消息
async def send_group_msg_with_cq(websocket, group_id, content, note=""):
    """
    发送群消息，使用旧的消息格式（cq码）
    如需自动撤回，请在note参数中添加“del_msg_秒数”
    如：del_msg_10
    则note参数为：del_msg_10
    https://napcat.apifox.cn/226799128e0
    """
    try:
        message = {
            "action": "send_group_msg",
            "params": {"group_id": group_id, "message": content},
            "echo": f"send_group_msg_{note}",
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行发送群消息到群 {group_id}")
    except Exception as e:
        logger.error(f"[API]执行发送群消息失败: {e}")


# 使用cq码发送私聊消息
async def send_private_msg_with_cq(websocket, user_id, content, note=""):
    """
    发送私聊消息，使用旧的消息格式（cq码）
    如需自动撤回，请在note参数中添加“del_msg_秒数”
    如：del_msg_10
    则note参数为：del_msg_10
    https://napcat.apifox.cn/226799128e0
    """
    try:
        message = {
            "action": "send_private_msg",
            "params": {"user_id": user_id, "message": content},
            "echo": f"send_private_msg_{note}",
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行发送消息到用户 {user_id}")
    except Exception as e:
        logger.error(f"[API]执行发送消息失败: {e}")


async def send_group_msg(websocket, group_id, message, note=""):
    """
    发送群聊消息，使用新的消息格式（消息段）
    {
        "type": "text",
        "data": {"text": "消息内容"}
    }
    消息段可使用generate模块的函数生成
    如需自动撤回，请在note参数中添加“del_msg_秒数”
    如：del_msg_10
    则note参数为：del_msg_10
    https://napcat.apifox.cn/226799128e0
    """
    try:
        # 检查message是否为字符串，如果是则转换为列表格式
        if isinstance(message, str):
            message = [{"type": "text", "data": {"text": message}}]
        elif isinstance(message, dict):  # 单个消息对象
            message = [message]
        elif not isinstance(message, list):
            message = [{"type": "text", "data": {"text": str(message)}}]

        message_data = {
            "action": "send_group_msg",
            "params": {
                "group_id": group_id,
                "message": message,
            },
            "echo": f"send_group_msg_{note}",
        }
        await websocket.send(json.dumps(message_data))
        logger.info(f"[API]已执行发送群聊消息到群 {group_id}")
    except Exception as e:
        logger.error(f"[API]执行发送群聊消息失败: {e}")


async def send_private_msg(websocket, user_id, message, note=""):
    """
    发送私聊消息，使用新的消息格式（消息段）
    {
        "type": "text",
        "data": {"text": "消息内容"}
    }
    消息段可使用generate模块的函数生成
    如需自动撤回，请在note参数中添加“del_msg_秒数”
    如：del_msg_10
    则note参数为：del_msg_10
    https://napcat.apifox.cn/226799128e0
    """
    try:
        # 检查message是否为字符串，如果是则转换为列表格式
        if isinstance(message, str):
            message = [{"type": "text", "data": {"text": message}}]
        elif isinstance(message, dict):  # 单个消息对象
            message = [message]
        elif not isinstance(message, list):
            message = [{"type": "text", "data": {"text": str(message)}}]

        message_data = {
            "action": "send_private_msg",
            "params": {"user_id": user_id, "message": message},
            "echo": f"send_private_msg_{note}",
        }
        await websocket.send(json.dumps(message_data))
        logger.info(f"[API]已执行发送私聊消息到用户 {user_id}")
    except Exception as e:
        logger.error(f"[API]执行发送私聊消息失败: {e}")


async def mark_group_msg_as_read(websocket, group_id):
    """
    设置群聊消息已读
    """
    try:
        message = {"action": "mark_group_msg_as_read", "params": {"group_id": group_id}}
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行设置群聊消息已读")
    except Exception as e:
        logger.error(f"[API]执行设置群聊消息已读失败: {e}")


async def mark_private_msg_as_read(websocket, user_id):
    """
    设置私聊消息已读
    """
    try:
        message = {"action": "mark_private_msg_as_read", "params": {"user_id": user_id}}
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行设置私聊消息已读")
    except Exception as e:
        logger.error(f"[API]执行设置私聊消息已读失败: {e}")


async def _mark_all_as_read(websocket):
    """
    设置所有消息已读
    """
    try:
        message = {"action": "_mark_all_as_read"}
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行设置所有消息已读")
    except Exception as e:
        logger.error(f"[API]执行设置所有消息已读失败: {e}")


async def delete_msg(websocket, message_id):
    """
    撤回消息
    """
    try:
        message = {"action": "delete_msg", "params": {"message_id": message_id}}
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行撤回消息：{message_id}")
    except Exception as e:
        logger.error(f"[API]执行撤回消息失败: {e}")


async def get_msg(websocket, message_id):
    """
    获取消息详情
    """
    try:
        message = {"action": "get_msg", "params": {"message_id": message_id}}
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取消息详情")
    except Exception as e:
        logger.error(f"[API]执行获取消息详情失败: {e}")


async def get_image(websocket, file_id):
    """
    获取图片消息详情
    """
    try:
        message = {"action": "get_image", "params": {"file_id": file_id}}
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取图片消息详情")
    except Exception as e:
        logger.error(f"[API]执行获取图片消息详情失败: {e}")


async def get_record(websocket, file, out_format):
    """
    获取语音消息详情
    """
    try:
        message = {
            "action": "get_record",
            "params": {"file": file, "out_format": out_format},
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取语音消息详情")
    except Exception as e:
        logger.error(f"[API]执行获取语音消息详情失败: {e}")


async def get_file(websocket, file_id):
    """
    获取文件消息
    """
    try:
        message = {"action": "get_file", "params": {"file_id": file_id}}
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取文件消息")
    except Exception as e:
        logger.error(f"[API]执行获取文件消息失败: {e}")


async def get_group_msg_history(
    websocket, group_id, user_id, count, message_seq=0, note=""
):
    """
    获取群历史消息
    """
    try:
        message = {
            "action": "get_group_msg_history",
            "params": {
                "group_id": group_id,
                "message_seq": message_seq,
                "count": count,
                "reverseOrder": True,
            },
            "echo": f"get_group_msg_history_{group_id}_{user_id}_{note}",
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取群历史消息")
    except Exception as e:
        logger.error(f"[API]执行获取群历史消息失败: {e}")


async def set_msg_emoji_like(websocket, message_id, emoji_id, set):
    """
    贴表情
    """
    try:
        message = {
            "action": "set_msg_emoji_like",
            "params": {"message_id": message_id, "emoji_id": emoji_id, "set": set},
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行设置消息表情点赞")
    except Exception as e:
        logger.error(f"[API]执行设置消息表情点赞失败: {e}")


async def get_friend_msg_history(
    websocket, user_id, message_seq, count, reverseOrder=False
):
    """
    获取好友历史消息
    """
    try:
        message = {
            "action": "get_friend_msg_history",
            "params": {
                "user_id": user_id,
                "message_seq": message_seq,
                "count": count,
                "reverseOrder": reverseOrder,
            },
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取好友历史消息")
    except Exception as e:
        logger.error(f"[API]执行获取好友历史消息失败: {e}")


async def get_recent_contact(websocket, count):
    """
    获取最近消息列表
    """
    try:
        message = {"action": "get_recent_contact", "params": {"count": count}}
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取最近消息列表")
    except Exception as e:
        logger.error(f"[API]执行获取最近消息列表失败: {e}")


async def fetch_emoji_like(websocket, message_id, emoji_id, emoji_type):
    """
    获取贴表情详情
    message_id 消息id
    emoji_id 表情id
    emoji_type 表情类型
    """
    try:
        message = {
            "action": "fetch_emoji_like",
            "params": {
                "message_id": message_id,
                "emoji_id": emoji_id,
                "emoji_type": emoji_type,
            },
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取消息表情点赞详情")
    except Exception as e:
        logger.error(f"[API]执行获取消息表情点赞详情失败: {e}")


async def get_forward_msg(websocket, message_id, note=""):
    """
    获取合并转发消息
    """
    try:
        message = {
            "action": "get_forward_msg",
            "params": {"message_id": message_id},
            "echo": f"get_forward_msg_{note}",
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取合并转发消息")
    except Exception as e:
        logger.error(f"[API]执行获取合并转发消息失败: {e}")


async def send_forward_msg(websocket, user_id=None, group_id=None, message=None):
    """
    发送合并转发消息

    Args:
        websocket: WebSocket连接实例
        message_id (Union[int, str]): 合并转发消息的message_id
        user_id (Union[int, str], optional): 好友的QQ号 (私聊发送)
        group_id (Union[int, str], optional): 群号 (群聊发送)

    Returns:
        bool: 发送是否成功

    Note:
        user_id和group_id必须提供其中一个，不能同时为空或同时提供
    """
    try:
        # 参数校验
        if user_id is None and group_id is None:
            logger.error(
                "[API]执行发送合并转发消息失败: 必须提供user_id或group_id其中之一"
            )

        if user_id is not None and group_id is not None:
            logger.error("[API]执行发送合并转发消息失败: user_id和group_id不能同时提供")

        if not message:
            logger.error("[API]执行发送合并转发消息失败: message不能为空")

        # 构建请求参数
        params = {"message": message}

        if user_id is not None:
            params["user_id"] = user_id
        if group_id is not None:
            params["group_id"] = group_id

        message = {"action": "send_forward_msg", "params": params}

        # 发送请求
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行发送合并转发消息")

    except Exception as e:
        logger.error(f"[API]执行发送合并转发消息失败: {e}")


async def send_poke(websocket, user_id, group_id=None):
    """
    发送戳一戳

    Args:
        websocket: WebSocket连接实例
        user_id (Union[int, str]): 好友的QQ号 (必填)
        group_id (Union[int, str], optional): 群号 (选填)

    Returns:
        bool: 发送是否成功
    """
    try:
        if not user_id:
            logger.error("[API]执行发送戳一戳失败: user_id不能为空")

        # 构建参数
        params = {"user_id": user_id}
        if group_id:
            params["group_id"] = group_id

        message = {"action": "send_poke", "params": params}
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行发送戳一戳")
    except Exception as e:
        logger.error(f"[API]执行发送戳一戳失败: {e}")

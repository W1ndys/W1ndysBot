import asyncio
import json
import logger


# 使用cq码发送群消息
async def send_group_msg_with_cq(websocket, group_id, content, note=""):
    """
    发送群消息，使用旧的消息格式（cq码）
    如需自动撤回，请在note参数中添加"del_msg=秒数"
    如：del_msg=10
    则note参数为：del_msg=10
    https://napcat.apifox.cn/226799128e0
    """
    try:
        # 删除消息最后的换行符
        if isinstance(content, str):
            content = content.rstrip("\n\r")

        payload = {
            "action": "send_group_msg",
            "params": {"group_id": group_id, "message": content},
            "echo": f"send_group_msg-{note}",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行发送群消息到群 {group_id}")
    except Exception as e:
        logger.error(f"[API]执行发送群消息失败: {e}")


# 使用cq码发送私聊消息
async def send_private_msg_with_cq(websocket, user_id, content, note=""):
    """
    发送私聊消息，使用旧的消息格式（cq码）
    如需自动撤回，请在note参数中添加"del_msg=秒数"
    如：del_msg=10
    则note参数为：del_msg=10
    https://napcat.apifox.cn/226799128e0
    """
    try:
        # 删除消息最后的换行符
        if isinstance(content, str):
            content = content.rstrip("\n\r")

        payload = {
            "action": "send_private_msg",
            "params": {"user_id": user_id, "message": content},
            "echo": f"send_private_msg-{note}",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行发送消息到用户 {user_id}")
    except Exception as e:
        logger.error(f"[API]执行发送消息失败: {e}")


async def send_group_msg(websocket, group_id, message, note=""):
    """
    发送群聊消息，使用新的消息格式（消息段）

    Args:
        websocket: WebSocket连接对象，用于与onebot通信
        group_id (int): 目标群号
        message (str|dict|list): 消息内容，支持以下格式：
            - str: 纯文本消息，会自动转换为消息段格式
            - dict: 单个消息段对象，格式如 {"type": "text", "data": {"text": "消息内容"}}
            - list: 消息段列表，包含多个消息段对象
        note (str, optional): 附加说明，支持以下功能：
            - "del_msg=秒数": 自动撤回消息，如 "del_msg=10" 表示10秒后撤回

    Returns:
        None

    Raises:
        Exception: 发送消息失败时抛出异常

    Examples:
        # 发送纯文本消息
        await send_group_msg(websocket, 123456789, "Hello World")

        # 发送消息段
        await send_group_msg(websocket, 123456789, [{"type": "text", "data": {"text": "Hello"}}])

        # 发送带撤回的消息
        await send_group_msg(websocket, 123456789, "Hello", "del_msg=30")

    Note:
        消息段可使用generate模块的函数生成，如generate_text_message()、generate_at_message()等
        函数会自动处理消息格式转换和换行符清理
        参考文档：https://napcat.apifox.cn/226799128e0
    """
    try:
        # 检查message是否为字符串，如果是则转换为列表格式
        if isinstance(message, str):
            message = [{"type": "text", "data": {"text": message}}]
        elif isinstance(message, dict):  # 单个消息对象
            message = [message]
        elif not isinstance(message, list):
            message = [{"type": "text", "data": {"text": str(message)}}]

        # 处理最后一条消息的换行符
        if message and len(message) > 0:
            last_msg = message[-1]
            if (
                last_msg.get("type") == "text"
                and "data" in last_msg
                and "text" in last_msg["data"]
            ):
                text_content = last_msg["data"]["text"]
                # 如果最后一条消息的文本内容纯换行，则删掉整条消息
                if text_content.strip() == "":
                    message.pop()
                else:
                    # 如果不是纯换行，则删掉末尾的换行符
                    last_msg["data"]["text"] = text_content.rstrip("\n\r")

        message_data = {
            "action": "send_group_msg",
            "params": {
                "group_id": group_id,
                "message": message,
            },
            "echo": f"send_group_msg-{note}",
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
    如需自动撤回，请在note参数中添加"del_msg=秒数"
    如：del_msg=10
    则note参数为：del_msg=10
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

        # 处理最后一条消息的换行符
        if message and len(message) > 0:
            last_msg = message[-1]
            if (
                last_msg.get("type") == "text"
                and "data" in last_msg
                and "text" in last_msg["data"]
            ):
                text_content = last_msg["data"]["text"]
                # 如果最后一条消息的文本内容纯换行，则删掉整条消息
                if text_content.strip() == "":
                    message.pop()
                else:
                    # 如果不是纯换行，则删掉末尾的换行符
                    last_msg["data"]["text"] = text_content.rstrip("\n\r")

        message_data = {
            "action": "send_private_msg",
            "params": {"user_id": user_id, "message": message},
            "echo": f"send_private_msg-{note}",
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
        payload = {
            "action": "mark_group_msg_as_read",
            "params": {"group_id": group_id},
            "echo": "mark_group_msg_as_read",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置群聊消息已读")
    except Exception as e:
        logger.error(f"[API]执行设置群聊消息已读失败: {e}")


async def mark_private_msg_as_read(websocket, user_id):
    """
    设置私聊消息已读
    """
    try:
        payload = {
            "action": "mark_private_msg_as_read",
            "params": {"user_id": user_id},
            "echo": "mark_private_msg_as_read",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置私聊消息已读")
    except Exception as e:
        logger.error(f"[API]执行设置私聊消息已读失败: {e}")


async def _mark_all_as_read(websocket):
    """
    设置所有消息已读
    """
    try:
        payload = {"action": "_mark_all_as_read", "echo": "_mark_all_as_read"}
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置所有消息已读")
    except Exception as e:
        logger.error(f"[API]执行设置所有消息已读失败: {e}")


async def delete_msg(websocket, message_id):
    """
    撤回消息
    """
    try:
        payload = {
            "action": "delete_msg",
            "params": {"message_id": message_id},
            "echo": "delete_msg",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行撤回消息：{message_id}")
    except Exception as e:
        logger.error(f"[API]执行撤回消息失败: {e}")


async def get_msg(websocket, message_id, note=""):
    """
    获取消息详情

    参数:
        websocket: WebSocket连接对象，用于发送消息
        message_id: str 消息ID
        note: str 备注，可选，用于在响应中标识请求的字段，默认空字符串

    返回:
        无返回值，通过websocket发送请求

    说明:
        由于websocket的特殊性，无法一对一获取响应信息
        需要在echo字段中添加标识信息，以便在处理响应时进行匹配
    """
    try:
        payload = {
            "action": "get_msg",
            "params": {"message_id": message_id},
            "echo": f"get_msg-{note}",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取消息详情")
    except Exception as e:
        logger.error(f"[API]执行获取消息详情失败: {e}")


async def get_image(websocket, file_id):
    """
    获取图片消息详情
    """
    try:
        payload = {
            "action": "get_image",
            "params": {"file_id": file_id},
            "echo": "get_image",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取图片消息详情")
    except Exception as e:
        logger.error(f"[API]执行获取图片消息详情失败: {e}")


async def get_record(websocket, file, out_format):
    """
    获取语音消息详情
    """
    try:
        payload = {
            "action": "get_record",
            "params": {"file": file, "out_format": out_format},
            "echo": "get_record",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取语音消息详情")
    except Exception as e:
        logger.error(f"[API]执行获取语音消息详情失败: {e}")


async def get_file(websocket, file_id):
    """
    获取文件消息
    """
    try:
        payload = {
            "action": "get_file",
            "params": {"file_id": file_id},
            "echo": "get_file",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取文件消息")
    except Exception as e:
        logger.error(f"[API]执行获取文件消息失败: {e}")


async def get_group_msg_history(websocket, group_id, count=20, message_seq=0, note=""):
    """
    获取群历史消息
    https://napcat.apifox.cn/226657401e0

    Args:
        websocket: WebSocket连接对象
        group_id: 群号
        count: 获取消息数量，默认20，在payload中可以不填
        message_seq: 起始消息序号，默认为0
        note: 备注信息，默认为空字符串

    Returns:
        None: 该函数通过websocket发送请求，不直接返回结果
    """
    try:
        payload = {
            "action": "get_group_msg_history",
            "params": {
                "group_id": group_id,
                "message_seq": message_seq,
                "count": count,
                "reverseOrder": True,  # 是否倒序
            },
            "echo": f"get_group_msg_history-{group_id}-{note}",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群历史消息")
    except Exception as e:
        logger.error(f"[API]执行获取群历史消息失败: {e}")


async def set_msg_emoji_like(websocket, message_id, emoji_id, set):
    """
    贴表情
    """
    try:
        payload = {
            "action": "set_msg_emoji_like",
            "params": {"message_id": message_id, "emoji_id": emoji_id, "set": set},
            "echo": "set_msg_emoji_like",
        }
        await websocket.send(json.dumps(payload))
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
        payload = {
            "action": "get_friend_msg_history",
            "params": {
                "user_id": user_id,
                "message_seq": message_seq,
                "count": count,
                "reverseOrder": reverseOrder,
            },
            "echo": "get_friend_msg_history",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取好友历史消息")
    except Exception as e:
        logger.error(f"[API]执行获取好友历史消息失败: {e}")


async def get_recent_contact(websocket, count):
    """
    获取最近消息列表
    """
    try:
        payload = {
            "action": "get_recent_contact",
            "params": {"count": count},
            "echo": "get_recent_contact",
        }
        await websocket.send(json.dumps(payload))
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
        payload = {
            "action": "fetch_emoji_like",
            "params": {
                "message_id": message_id,
                "emoji_id": emoji_id,
                "emoji_type": emoji_type,
            },
            "echo": "fetch_emoji_like",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取消息表情点赞详情")
    except Exception as e:
        logger.error(f"[API]执行获取消息表情点赞详情失败: {e}")


async def get_forward_msg(websocket, message_id, note=""):
    """
    获取合并转发消息
    """
    try:
        payload = {
            "action": "get_forward_msg",
            "params": {"message_id": message_id},
            "echo": f"get_forward_msg-{note}",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取合并转发消息")
    except Exception as e:
        logger.error(f"[API]执行获取合并转发消息失败: {e}")


async def send_forward_msg(
    websocket,
    user_id=None,
    group_id=None,
    message=None,
    news="消息预览",
    prompt="消息外显",
    summary="消息摘要",
    source="消息来源",
    note="",
):
    """
    发送合并转发消息

    Args:
        websocket: WebSocket连接实例
        user_id (Union[int, str], optional): 好友的QQ号 (私聊发送)
        group_id (Union[int, str], optional): 群号 (群聊发送)
        message (list, optional): 消息段 (必填)
        news (str, optional): 消息预览 (默认值为“消息预览”)
        prompt (str, optional): 消息外显 (默认值为“消息外显”)
        summary (str, optional): 消息摘要 (默认值为“消息摘要”)
        source (str, optional): 消息来源 (默认值为“消息来源”)
        note (str, optional): 消息备注 (默认值为空字符串)


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
        params = {
            "messages": message,
            "news": [{"text": news}],
            "prompt": prompt,
            "summary": summary,
            "source": source,
        }

        if user_id is not None:
            params["user_id"] = user_id
        if group_id is not None:
            params["group_id"] = group_id

        payload = {
            "action": "send_forward_msg",
            "params": params,
            "echo": f"send_forward_msg-{note}",
        }

        # 发送请求
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行发送合并转发消息")

    except Exception as e:
        logger.error(f"[API]执行发送合并转发消息失败: {e}")


async def send_private_forward_msg(websocket, user_id, messages, note=""):
    """
    发送私聊合并转发消息

    Args:
        websocket: WebSocket连接实例
        user_id (Union[int, str]): 好友的QQ号 (必填)
        messages (list): 消息节点列表 (必填)
            每个节点格式：{
                "type": "node",
                "data": {
                    "nickname": "发送者昵称",
                    "user_id": "发送者QQ号",
                    "content": [消息段列表]
                }
            }
        note (str, optional): 消息备注 (默认值为空字符串)

    Returns:
        None: 该函数通过websocket发送请求，不直接返回结果

    Example:
        messages = [
            {
                "type": "node",
                "data": {
                    "nickname": "发送者1",
                    "user_id": "123456789",
                    "content": [{"type": "text", "data": {"text": "消息内容1"}}]
                }
            },
            {
                "type": "node",
                "data": {
                    "nickname": "发送者2",
                    "user_id": "987654321",
                    "content": [{"type": "text", "data": {"text": "消息内容2"}}]
                }
            }
        ]
        await send_private_forward_msg(websocket, user_id, messages)
    """
    try:
        # 参数校验
        if not user_id:
            logger.error("[API]执行发送私聊合并转发消息失败: user_id不能为空")
            return

        if not messages:
            logger.error("[API]执行发送私聊合并转发消息失败: messages不能为空")
            return

        # 构建请求参数
        payload = {
            "action": "send_private_forward_msg",
            "params": {"user_id": user_id, "messages": messages},
            "echo": f"send_private_forward_msg-{note}",
        }

        # 发送请求
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行发送私聊合并转发消息到用户 {user_id}")

    except Exception as e:
        logger.error(f"[API]执行发送私聊合并转发消息失败: {e}")


async def send_group_forward_msg(
    websocket, group_id, messages, source, news, prompt, summary, note=""
):
    """
    发送群聊合并转发消息

    Args:
        websocket: WebSocket连接实例
        group_id (Union[int, str]): 群号 (必填)
        messages (list): 消息节点列表 (必填)
            每个节点格式：{
                "type": "node",
                "data": {
                    "user_id": "发送者QQ号",
                    "nickname": "发送者昵称",
                    "content": [消息段列表]
                }
            }
        source (str): 消息内容/标题 (必填)
        news (list): 消息预览列表 (必填)
            格式：[{"text": "预览文本"}]
        summary (str): 底下文本 (必填)
        prompt (str): 消息外显 (必填)
        note (str, optional): 消息备注 (默认值为空字符串)

    Returns:
        None: 该函数通过websocket发送请求，不直接返回结果

    Example:
        messages = [
            {
                "type": "node",
                "data": {
                    "user_id": "123456789",
                    "nickname": "发送者1",
                    "content": [{"type": "text", "data": {"text": "消息内容1"}}]
                }
            },
            {
                "type": "node",
                "data": {
                    "user_id": "987654321",
                    "nickname": "发送者2",
                    "content": [{"type": "text", "data": {"text": "消息内容2"}}]
                }
            }
        ]
        news = [{"text": "消息预览"}]
        await send_group_forward_msg(websocket, group_id, messages, news, "外显", "底下文本", "消息来源")
    """
    try:
        # 参数校验
        if not group_id:
            logger.error("[API]执行发送群聊合并转发消息失败: group_id不能为空")
            return

        if not messages:
            logger.error("[API]执行发送群聊合并转发消息失败: messages不能为空")
            return

        if not news:
            logger.error("[API]执行发送群聊合并转发消息失败: news不能为空")
            return

        if not prompt:
            logger.error("[API]执行发送群聊合并转发消息失败: prompt不能为空")
            return

        if not summary:
            logger.error("[API]执行发送群聊合并转发消息失败: summary不能为空")
            return

        if not source:
            logger.error("[API]执行发送群聊合并转发消息失败: source不能为空")
            return

        # 构建请求参数
        payload = {
            "action": "send_group_forward_msg",
            "params": {
                "group_id": group_id,
                "messages": messages,
                "news": news,
                "prompt": prompt,
                "summary": summary,
                "source": source,
            },
            "echo": f"send_group_forward_msg-{note}",
        }

        # 发送请求
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行发送群聊合并转发消息到群 {group_id}")

    except Exception as e:
        logger.error(f"[API]执行发送群聊合并转发消息失败: {e}")


async def group_poke(websocket, group_id, user_id):
    """
    发送戳一戳

    Args:
        websocket: WebSocket连接实例
        group_id (Union[int, str]): 群号 (必填)
        user_id (Union[int, str]): 群友的QQ号 (必填)

    Returns:
        bool: 发送是否成功
    """
    try:
        if not user_id:
            logger.error("[API]执行发送戳一戳失败: user_id不能为空")

        payload = {
            "action": "group_poke",
            "params": {"group_id": group_id, "user_id": user_id},
            "echo": "group_poke",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行发送戳一戳")
    except Exception as e:
        logger.error(f"[API]执行发送戳一戳失败: {e}")

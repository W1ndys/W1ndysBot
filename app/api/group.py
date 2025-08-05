import json
import logger


async def set_group_kick_members(
    websocket, group_id, user_id, reject_add_request=False, note=""
):
    """
    批量踢出群成员

    Args:
        websocket: WebSocket连接对象，用于与上游通信
        group_id (str|int): 群号
        user_id (list): 要踢出的用户ID列表
        reject_add_request (bool, optional): 是否群拉黑，默认为False
        note (str, optional): 附加说明，用于在响应处理中获取结果

    Returns:
        bool: 操作是否成功，True表示成功，False表示失败

    Note:
        此函数通过WebSocket发送API请求到上游，由于WebSocket的特殊性，
        无法直接获取响应结果，需要通过echo字段在响应处理中获取结果
    """
    try:
        payload = {
            "action": "set_group_kick_members",
            "params": {
                "group_id": group_id,
                "user_id": user_id,
                "reject_add_request": reject_add_request,
            },
            "echo": f"set_group_kick_members-{note}",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行批量踢出群成员")
        return True
    except Exception as e:
        logger.error(f"[API]批量踢出群成员失败: {e}")
        return False


async def set_group_kick(
    websocket, group_id, user_id, reject_add_request=False, note=""
):
    """
    设置群踢人

    Args:
        websocket: WebSocket连接对象，用于与上游通信
        group_id (str): 群号
        user_id (str): 要踢出的用户ID
        reject_add_request (bool, optional): 是否拒绝此人的加群请求，默认为False

    Returns:
        bool: 操作是否成功，True表示成功，False表示失败

    Note:
        此函数通过WebSocket发送API请求到上游，由于WebSocket的特殊性，
        无法直接获取响应结果，需要通过echo字段在响应处理中获取结果
    """
    try:
        payload = {
            "action": "set_group_kick",
            "params": {
                "group_id": group_id,
                "user_id": user_id,
                "reject_add_request": reject_add_request,
            },
            "echo": "set_group_kick",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置群踢人")
        return True
    except Exception as e:
        logger.error(f"[API]设置群踢人失败: {e}")
        return False


async def set_group_ban(websocket, group_id, user_id, duration):
    """
    群禁言
    """
    try:
        payload = {
            "action": "set_group_ban",
            "params": {"group_id": group_id, "user_id": user_id, "duration": duration},
            "echo": "set_group_ban",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行群禁言")
        return True
    except Exception as e:
        logger.error(f"[API]群禁言失败: {e}")
        return False


async def set_group_ban_multiple(websocket, group_id, user_ids, duration, note=""):
    """
    批量群禁言

    Args:
        websocket: WebSocket连接对象，用于与上游通信
        group_id (str): 群号
        user_ids (list): 要禁言的用户ID列表
        duration (int): 禁言时长，单位秒，0表示取消禁言，30天=2592000秒
        note (str, optional): 附加说明，用于在响应处理中获取结果

    Returns:
        bool: 操作是否成功，True表示成功，False表示失败

    Note:
        此函数为占位符，需要您根据实际需求实现批量禁言逻辑
        可以选择：
        1. 使用现有的set_group_ban函数循环调用
        2. 实现新的批量禁言API（如果上游支持）
        3. 添加适当的延时避免频率限制
    """
    try:
        # TODO: 请在此处实现批量禁言逻辑
        # 示例实现：循环调用单个禁言API
        success_count = 0
        for user_id in user_ids:
            try:
                await set_group_ban(websocket, group_id, user_id, duration)
                success_count += 1
                # 添加小延时避免频率限制
                import asyncio

                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"[API]禁言用户 {user_id} 失败: {e}")

        logger.info(
            f"[API]批量禁言完成，成功禁言 {success_count}/{len(user_ids)} 个用户"
        )
        return success_count > 0
    except Exception as e:
        logger.error(f"[API]批量群禁言失败: {e}")
        return False


async def get_group_system_msg(websocket, group_id):
    """
    获取群系统消息
    """
    try:
        payload = {
            "action": "get_group_system_msg",
            "params": {"group_id": group_id},
            "echo": "get_group_system_msg",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群系统消息")
        return True
    except Exception as e:
        logger.error(f"[API]获取群系统消息失败: {e}")
        return False


async def get_essence_msg_list(websocket, group_id):
    """
    获取精华消息
    """
    try:
        payload = {
            "action": "get_essence_msg_list",
            "params": {"group_id": group_id},
            "echo": "get_essence_msg_list",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取精华消息")
        return True
    except Exception as e:
        logger.error(f"[API]获取精华消息失败: {e}")
        return False


async def set_group_whole_ban(websocket, group_id, enable):
    """
    全体禁言
    """
    try:
        payload = {
            "action": "set_group_whole_ban",
            "params": {"group_id": group_id, "enable": enable},
            "echo": "set_group_whole_ban",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行全体禁言")
        return True
    except Exception as e:
        logger.error(f"[API]全体禁言失败: {e}")
        return False


async def set_group_portrait(websocket, group_id, file_path):
    """
    设置群头像
    """
    try:
        payload = {
            "action": "set_group_portrait",
            "params": {"group_id": group_id, "file_path": file_path},
            "echo": "set_group_portrait",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置群头像")
        return True
    except Exception as e:
        logger.error(f"[API]设置群头像失败: {e}")
        return False


async def set_group_admin(websocket, group_id, user_id, enable):
    """
    设置群管理
    """
    try:
        payload = {
            "action": "set_group_admin",
            "params": {"group_id": group_id, "user_id": user_id, "enable": enable},
            "echo": "set_group_admin",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置群管理")
        return True
    except Exception as e:
        logger.error(f"[API]设置群管理失败: {e}")
        return False


async def set_group_essence_msg(websocket, group_id, message_id):
    """
    设置群精华消息
    """
    try:
        payload = {
            "action": "set_group_essence_msg",
            "params": {"group_id": group_id, "message_id": message_id},
            "echo": "set_group_essence_msg",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置群精华消息")
        return True
    except Exception as e:
        logger.error(f"[API]设置群精华消息失败: {e}")
        return False


async def set_group_card(websocket, group_id, user_id, card):
    """
    设置群成员名片
    """
    try:
        payload = {
            "action": "set_group_card",
            "params": {"group_id": group_id, "user_id": user_id, "card": card},
            "echo": "set_group_card",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置群成员名片")
        return True
    except Exception as e:
        logger.error(f"[API]设置群成员名片失败: {e}")
        return False


async def delete_group_essence_msg(websocket, group_id, message_id):
    """
    删除群精华消息
    """
    try:
        payload = {
            "action": "delete_group_essence_msg",
            "params": {"group_id": group_id, "message_id": message_id},
            "echo": "delete_group_essence_msg",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行删除群精华消息")
        return True
    except Exception as e:
        logger.error(f"[API]删除群精华消息失败: {e}")
        return False


async def set_group_name(websocket, group_id, group_name):
    """
    设置群名
    """
    try:
        payload = {
            "action": "set_group_name",
            "params": {"group_id": group_id, "group_name": group_name},
            "echo": "set_group_name",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置群名")
        return True
    except Exception as e:
        logger.error(f"[API]设置群名失败: {e}")
        return False


async def set_group_leave(websocket, group_id):
    """
    退群
    """
    try:
        payload = {
            "action": "set_group_leave",
            "params": {"group_id": group_id},
            "echo": "set_group_leave",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行退群")
        return True
    except Exception as e:
        logger.error(f"[API]退群失败: {e}")
        return False


async def _send_group_notice(websocket, group_id, content, image_path):
    """
    _发送群公告
    """
    try:
        payload = {
            "action": "_send_group_notice",
            "params": {
                "group_id": group_id,
                "content": content,
                "image_path": image_path,
            },
            "echo": "_send_group_notice",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行发送群公告")
        return True
    except Exception as e:
        logger.error(f"[API]发送群公告失败: {e}")
        return False


async def _get_group_notice(websocket, group_id):
    """
    获取群公告
    """
    try:
        payload = {
            "action": "_get_group_notice",
            "params": {"group_id": group_id},
            "echo": "_get_group_notice",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群公告")
        return True
    except Exception as e:
        logger.error(f"[API]获取群公告失败: {e}")
        return False


async def set_group_special_title(websocket, group_id, user_id, special_title):
    """
    设置群头衔
    """
    try:
        payload = {
            "action": "set_group_special_title",
            "params": {
                "group_id": group_id,
                "user_id": user_id,
                "special_title": special_title,
            },
            "echo": "set_group_special_title",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置群头衔")
        return True
    except Exception as e:
        logger.error(f"[API]设置群头衔失败: {e}")
        return False


async def upload_group_file(websocket, group_id, file, name, folder_id):
    """
    上传群文件
    """
    try:
        payload = {
            "action": "upload_group_file",
            "params": {
                "group_id": group_id,
                "file": file,
                "name": name,
                "folder_id": folder_id,
            },
            "echo": "upload_group_file",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行上传群文件")
        return True
    except Exception as e:
        logger.error(f"[API]上传群文件失败: {e}")
        return False


async def set_group_add_request(websocket, flag, approve, reason=""):
    """
    处理加群请求

    参数:
        websocket: WebSocket连接
        flag (str): 请求id,必需
        approve (bool): 是否同意,必需
        reason (str): 拒绝理由,当approve为False时生效

    返回:
        bool: 操作是否成功
    """
    try:
        payload = {
            "action": "set_group_add_request",
            "params": {"flag": flag, "approve": approve, "reason": reason},
            "echo": "set_group_add_request",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行处理加群请求")
        return True
    except Exception as e:
        logger.error(f"[API]处理加群请求失败: {e}")
        return False


async def get_group_info(websocket, group_id):
    """
    获取群信息
    参数:
        websocket: WebSocket连接对象
        group_id (int/str): 群号，必填
    返回:
        bool: 操作是否成功（仅表示API是否发送成功，具体响应需通过echo处理）
    特别注意:
        由于WebSocket的特殊性，无法一对一获取相应信息，需通过echo字段处理响应
    """
    try:
        # 构造请求payload，action为get_group_info，params包含group_id，echo用于后续响应识别
        payload = {
            "action": "get_group_info",
            "params": {"group_id": group_id},
            "echo": "get_group_info",
        }
        # 发送请求到上游WebSocket
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群信息")
        return True
    except Exception as e:
        # 捕获异常并记录错误日志
        logger.error(f"[API]获取群信息失败: {e}")
        return False


async def get_group_info_ex(websocket, group_id):
    """
    获取群信息
    """
    try:
        payload = {
            "action": "get_group_info_ex",
            "params": {"group_id": group_id},
            "echo": "get_group_info_ex",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群信息")
        return True
    except Exception as e:
        logger.error(f"[API]获取群信息失败: {e}")
        return False


async def create_group_file_folder(websocket, group_id, folder_name):
    """
    创建群文件夹
    """
    try:
        payload = {
            "action": "create_group_file_folder",
            "params": {"group_id": group_id, "folder_name": folder_name},
            "echo": "create_group_file_folder",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行创建群文件夹")
        return True
    except Exception as e:
        logger.error(f"[API]创建群文件夹失败: {e}")
        return False


async def delete_group_file(websocket, group_id, file_id):
    """
    删除群文件
    """
    try:
        payload = {
            "action": "delete_group_file",
            "params": {"group_id": group_id, "file_id": file_id},
            "echo": "delete_group_file",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行删除群文件")
        return True
    except Exception as e:
        logger.error(f"[API]删除群文件失败: {e}")
        return False


async def delete_group_folder(websocket, group_id, folder_id):
    """
    删除群文件夹
    """
    try:
        payload = {
            "action": "delete_group_folder",
            "params": {"group_id": group_id, "folder_id": folder_id},
            "echo": "delete_group_folder",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行删除群文件夹")
        return True
    except Exception as e:
        logger.error(f"[API]删除群文件夹失败: {e}")
        return False


async def get_group_file_system_info(websocket, group_id):
    """
    获取群文件系统信息
    """
    try:
        payload = {
            "action": "get_group_file_system_info",
            "params": {"group_id": group_id},
            "echo": "get_group_file_system_info",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群文件系统信息")
        return True
    except Exception as e:
        logger.error(f"[API]获取群文件系统信息失败: {e}")
        return False


async def get_group_root_files(websocket, group_id):
    """
    获取群根目录文件列表
    """
    try:
        payload = {
            "action": "get_group_root_files",
            "params": {"group_id": group_id},
            "echo": "get_group_root_files",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群根目录文件列表")
        return True
    except Exception as e:
        logger.error(f"[API]获取群根目录文件列表失败: {e}")
        return False


async def get_group_files_by_folder(websocket, group_id, folder_id, file_count):
    """
    获取群子目录文件列表
    """
    try:
        payload = {
            "action": "get_group_files_by_folder",
            "params": {
                "group_id": group_id,
                "folder_id": folder_id,
                "file_count": file_count,
            },
            "echo": "get_group_files_by_folder",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群子目录文件列表")
        return True
    except Exception as e:
        logger.error(f"[API]获取群子目录文件列表失败: {e}")
        return False


async def get_group_file_url(websocket, group_id, file_id):
    """
    获取群文件资源链接
    """
    try:
        payload = {
            "action": "get_group_file_url",
            "params": {"group_id": group_id, "file_id": file_id},
            "echo": "get_group_file_url",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群文件资源链接")
        return True
    except Exception as e:
        logger.error(f"[API]获取群文件资源链接失败: {e}")
        return False


async def get_group_list(websocket, no_cache):
    """
    获取群列表
    """
    try:
        payload = {
            "action": "get_group_list",
            "params": {"no_cache": no_cache},
            "echo": "get_group_list",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群列表")
        return True
    except Exception as e:
        logger.error(f"[API]获取群列表失败: {e}")
        return False


async def get_group_member_info(websocket, group_id, user_id, no_cache):
    """
    获取群成员信息
    """
    try:
        payload = {
            "action": "get_group_member_info",
            "params": {"group_id": group_id, "user_id": user_id, "no_cache": no_cache},
            "echo": "get_group_member_info",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群成员信息")
        return True
    except Exception as e:
        logger.error(f"[API]获取群成员信息失败: {e}")
        return False


async def get_group_member_list(websocket, group_id, no_cache=False, note=""):
    """
    获取群成员列表

    参数:
        websocket: WebSocket连接
        group_id (str): 群号,必需
        no_cache (bool): 是否不使用缓存,可选
        note (str): 附加说明，用于在响应处理中获取结果
    返回:
        bool: 操作是否成功
    """
    try:
        payload = {
            "action": "get_group_member_list",
            "params": {"group_id": group_id, "no_cache": no_cache},
            "echo": f"get_group_member_list-group_id={group_id}-{note}",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群 {group_id} 成员列表，note={note}")
        return True
    except Exception as e:
        logger.error(f"[API]获取群成员列表失败: {e}")
        return False


async def get_group_honor_info(websocket, group_id):
    """
    获取群荣誉信息
    """
    try:
        payload = {
            "action": "get_group_honor_info",
            "params": {"group_id": group_id},
            "echo": "get_group_honor_info",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群荣誉信息")
        return True
    except Exception as e:
        logger.error(f"[API]获取群荣誉信息失败: {e}")
        return False


async def get_group_at_all_remain(websocket, group_id):
    """
    获取群at剩余次数
    """
    try:
        payload = {
            "action": "get_group_at_all_remain",
            "params": {"group_id": group_id},
            "echo": "get_group_at_all_remain",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群at剩余次数")
        return True
    except Exception as e:
        logger.error(f"[API]获取群at剩余次数失败: {e}")
        return False


async def get_group_ignored_notifies(websocket, group_id):
    """
    获取群过滤系统消息
    """
    try:
        payload = {
            "action": "get_group_ignored_notifies",
            "params": {"group_id": group_id},
            "echo": "get_group_ignored_notifies",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取群过滤系统消息")
        return True
    except Exception as e:
        logger.error(f"[API]获取群被禁言成员列表失败: {e}")
        return False


async def set_group_sign(websocket, group_id):
    """
    设置群打卡
    """
    try:
        payload = {
            "action": "set_group_sign",
            "params": {"group_id": group_id},
            "echo": "set_group_sign",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置群打卡")
        return True
    except Exception as e:
        logger.error(f"[API]设置群打卡失败: {e}")
        return False


async def send_group_sign(websocket, group_id):
    """
    发送群打卡
    """
    try:
        payload = {
            "action": "send_group_sign",
            "params": {"group_id": group_id},
            "echo": "send_group_sign",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行发送群打卡")
        return True
    except Exception as e:
        logger.error(f"[API]发送群打卡失败: {e}")
        return False


async def get_ai_characters(websocket, group_id, chat_type):
    """
    获取ai语音人物
    """
    try:
        payload = {
            "action": "get_ai_characters",
            "params": {"group_id": group_id, "chat_type": chat_type},
            "echo": "get_ai_characters",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取ai语音人物")
        return True
    except Exception as e:
        logger.error(f"[API]获取ai语音人物失败: {e}")
        return False


async def send_group_ai_record(websocket, group_id, character_id, text):
    """
    发送群ai语音
    """
    try:
        payload = {
            "action": "send_group_ai_record",
            "params": {
                "group_id": group_id,
                "character_id": character_id,
                "text": text,
            },
            "echo": "send_group_ai_record",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行发送群ai语音")
        return True
    except Exception as e:
        logger.error(f"[API]发送群ai语音失败: {e}")
        return False


async def get_ai_record(websocket, group_id, character, text):
    """
    获取ai语音
    """
    try:
        payload = {
            "action": "get_ai_record",
            "params": {"group_id": group_id, "character": character, "text": text},
            "echo": "get_ai_record",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取ai语音")
        return True
    except Exception as e:
        logger.error(f"[API]获取群ai语音失败: {e}")
        return False

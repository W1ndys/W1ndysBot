import json
import logger


async def set_group_kick(websocket, group_id, user_id, reject_add_request=False):
    """
    设置群踢人
    """
    try:
        message = {
            "action": "set_group_kick",
            "params": {
                "group_id": group_id,
                "user_id": user_id,
                "reject_add_request": reject_add_request,
            },
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "set_group_ban",
            "params": {"group_id": group_id, "user_id": user_id, "duration": duration},
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行群禁言")
        return True
    except Exception as e:
        logger.error(f"[API]群禁言失败: {e}")
        return False


async def get_group_system_msg(websocket, group_id):
    """
    获取群系统消息
    """
    try:
        message = {
            "action": "get_group_system_msg",
            "params": {"group_id": group_id},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "get_essence_msg_list",
            "params": {"group_id": group_id},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "set_group_whole_ban",
            "params": {"group_id": group_id, "enable": enable},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "set_group_portrait",
            "params": {"group_id": group_id, "file_path": file_path},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "set_group_admin",
            "params": {"group_id": group_id, "user_id": user_id, "enable": enable},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "set_group_essence_msg",
            "params": {"group_id": group_id, "message_id": message_id},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "set_group_card",
            "params": {"group_id": group_id, "user_id": user_id, "card": card},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "delete_group_essence_msg",
            "params": {"group_id": group_id, "message_id": message_id},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "set_group_name",
            "params": {"group_id": group_id, "group_name": group_name},
        }
        await websocket.send(json.dumps(message))
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
        message = {"action": "set_group_leave", "params": {"group_id": group_id}}
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "_send_group_notice",
            "params": {
                "group_id": group_id,
                "content": content,
                "image_path": image_path,
            },
        }
        await websocket.send(json.dumps(message))
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
        message = {"action": "_get_group_notice", "params": {"group_id": group_id}}
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "set_group_special_title",
            "params": {
                "group_id": group_id,
                "user_id": user_id,
                "special_title": special_title,
            },
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "upload_group_file",
            "params": {
                "group_id": group_id,
                "file": file,
                "name": name,
                "folder_id": folder_id,
            },
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行上传群文件")
        return True
    except Exception as e:
        logger.error(f"[API]上传群文件失败: {e}")
        return False


async def set_group_add_request(websocket, flag, approve, reason):
    """
    处理加群请求
    """
    try:
        message = {
            "action": "set_group_add_request",
            "params": {"flag": flag, "approve": approve, "reason": reason},
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行处理加群请求")
        return True
    except Exception as e:
        logger.error(f"[API]处理加群请求失败: {e}")
        return False


async def get_group_info(websocket, group_id):
    """
    获取群信息
    """
    try:
        message = {"action": "get_group_info", "params": {"group_id": group_id}}
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取群信息")
        return True
    except Exception as e:
        logger.error(f"[API]获取群信息失败: {e}")
        return False


async def get_group_info_ex(websocket, group_id):
    """
    获取群信息
    """
    try:
        message = {"action": "get_group_info_ex", "params": {"group_id": group_id}}
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "create_group_file_folder",
            "params": {"group_id": group_id, "folder_name": folder_name},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "delete_group_file",
            "params": {"group_id": group_id, "file_id": file_id},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "delete_group_folder",
            "params": {"group_id": group_id, "folder_id": folder_id},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "get_group_file_system_info",
            "params": {"group_id": group_id},
        }
        await websocket.send(json.dumps(message))
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
        message = {"action": "get_group_root_files", "params": {"group_id": group_id}}
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "get_group_files_by_folder",
            "params": {
                "group_id": group_id,
                "folder_id": folder_id,
                "file_count": file_count,
            },
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "get_group_file_url",
            "params": {"group_id": group_id, "file_id": file_id},
        }
        await websocket.send(json.dumps(message))
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
        message = {"action": "get_group_list", "params": {"no_cache": no_cache}}
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "get_group_member_info",
            "params": {"group_id": group_id, "user_id": user_id, "no_cache": no_cache},
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取群成员信息")
        return True
    except Exception as e:
        logger.error(f"[API]获取群成员信息失败: {e}")
        return False


async def get_group_member_list(websocket, group_id, no_cache):
    """
    获取群成员列表
    """
    try:
        message = {
            "action": "get_group_member_list",
            "params": {"group_id": group_id, "no_cache": no_cache},
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取群成员列表")
        return True
    except Exception as e:
        logger.error(f"[API]获取群成员列表失败: {e}")
        return False


async def get_group_honor_info(websocket, group_id):
    """
    获取群荣誉信息
    """
    try:
        message = {"action": "get_group_honor_info", "params": {"group_id": group_id}}
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "get_group_at_all_remain",
            "params": {"group_id": group_id},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "get_group_ignored_notifies",
            "params": {"group_id": group_id},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "set_group_sign",
            "params": {"group_id": group_id},
        }
        await websocket.send(json.dumps(message))
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
        message = {"action": "send_group_sign", "params": {"group_id": group_id}}
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "get_ai_characters",
            "params": {"group_id": group_id, "chat_type": chat_type},
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "send_group_ai_record",
            "params": {
                "group_id": group_id,
                "character_id": character_id,
                "text": text,
            },
        }
        await websocket.send(json.dumps(message))
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
        message = {
            "action": "get_ai_record",
            "params": {"group_id": group_id, "character": character, "text": text},
        }
        await websocket.send(json.dumps(message))
        logger.info(f"[API]已执行获取ai语音")
        return True
    except Exception as e:
        logger.error(f"[API]获取群ai语音失败: {e}")
        return False

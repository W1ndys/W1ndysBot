import json
import logger


async def set_qq_profile(websocket, nickname, personal_note, sex):
    """
    设置账号信息
    """
    try:
        payload = {
            "action": "set_qq_profile",
            "params": {
                "nickname": nickname,
                "personal_note": personal_note,
                "sex": sex,
            },
            "echo": "set_qq_profile",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置账号信息")
        return True
    except Exception as e:
        logger.error(f"[API]设置账号信息失败: {e}")
        return False


async def ArkSharePeer(websocket, group_id, user_id, phoneNumber):
    """
    获取推荐好友/群聊卡片
    """
    try:
        payload = {
            "action": "ArkSharePeer",
            "params": {
                "group_id": group_id,
                "user_id": user_id,
                "phoneNumber": phoneNumber,
            },
            "echo": "ArkSharePeer",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取推荐好友/群聊卡片")
        return True
    except Exception as e:
        logger.error(f"[API]获取推荐好友/群聊卡片失败: {e}")
        return False


async def ArkShareGroup(websocket, group_id):
    """
    获取推荐群聊卡片
    """
    try:
        payload = {
            "action": "ArkShareGroup",
            "params": {"group_id": group_id},
            "echo": "ArkShareGroup",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取推荐群聊卡片")
        return True
    except Exception as e:
        logger.error(f"[API]获取推荐群聊卡片失败: {e}")
        return False


async def set_online_status(websocket, status, ext_status, battery_status):
    """
    设置在线状态
    """
    try:
        payload = {
            "action": "set_online_status",
            "params": {
                "status": status,
                "ext_status": ext_status,
                "battery_status": battery_status,
            },
            "echo": "set_online_status",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置在线状态")
        return True
    except Exception as e:
        logger.error(f"[API]设置在线状态失败: {e}")
        return False


async def get_friends_with_category(websocket):
    """
    获取好友分组列表
    """
    try:
        payload = {
            "action": "get_friends_with_category",
            "echo": "get_friends_with_category",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取好友分组列表")
        return True
    except Exception as e:
        logger.error(f"[API]获取好友分组列表失败: {e}")
        return False


async def set_qq_avatar(websocket, file):
    """
    设置头像
    """
    try:
        payload = {
            "action": "set_qq_avatar",
            "params": {"file": file},
            "echo": "set_qq_avatar",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置头像")
        return True
    except Exception as e:
        logger.error(f"[API]设置头像失败: {e}")
        return False


async def send_like(websocket, user_id, times=1):
    """
    点赞
    """
    try:
        payload = {
            "action": "send_like",
            "params": {"user_id": user_id, "times": times},
            "echo": "send_like",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行点赞")
        return True
    except Exception as e:
        logger.error(f"[API]点赞失败: {e}")
        return False


async def create_collection(websocket, raw_data, brief):
    """
    创建收藏
    """
    try:
        payload = {
            "action": "create_collection",
            "params": {"rawData": raw_data, "brief": brief},
            "echo": "create_collection",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行创建收藏")
        return True
    except Exception as e:
        logger.error(f"[API]创建收藏失败: {e}")
        return False


async def set_friend_add_request(websocket, flag, approve, remark=""):
    """
    处理好友请求
    参数:
        flag (string): 请求id，必需
        approve (boolean): 是否同意，必需
        remark (string): 好友备注，必需
    """
    try:
        payload = {
            "action": "set_friend_add_request",
            "params": {"flag": flag, "approve": approve, "remark": remark},
            "echo": "set_friend_add_request",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行处理好友请求")
        return True
    except Exception as e:
        logger.error(f"[API]处理好友请求失败: {e}")
        return False


async def set_group_add_request(websocket, flag, approve, reason=""):
    """
    处理群请求
    参数:
        flag (string): 请求id，必需
        approve (boolean): 是否同意，必需
        reason (string): 拒绝理由，可选
    """
    try:
        payload = {
            "action": "set_group_add_request",
            "params": {"flag": flag, "approve": approve, "reason": reason},
            "echo": "set_group_add_request",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行处理群请求")
        return True
    except Exception as e:
        logger.error(f"[API]处理群请求失败: {e}")
        return False


async def set_self_longnick(websocket, long_nick):
    """
    设置个性签名
    """
    try:
        payload = {
            "action": "set_self_longnick",
            "params": {"longNick": long_nick},
            "echo": "set_self_longnick",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行设置个性签名")
        return True
    except Exception as e:
        logger.error(f"[API]设置个性签名失败: {e}")
        return False


async def get_stranger_info(websocket, user_id):
    """
    获取账号信息
    """
    try:
        payload = {
            "action": "get_stranger_info",
            "params": {"user_id": user_id},
            "echo": "get_stranger_info",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取账号信息")
        return True
    except Exception as e:
        logger.error(f"[API]获取账号信息失败: {e}")
        return False


async def get_friend_list(websocket, no_cache=False):
    """
    获取好友列表
    """
    try:
        payload = {
            "action": "get_friend_list",
            "params": {"no_cache": no_cache},
            "echo": "get_friend_list",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取好友列表")
        return True
    except Exception as e:
        logger.error(f"[API]获取好友列表失败: {e}")
        return False


async def get_like_list(websocket):
    """
    获取点赞列表
    """
    try:
        payload = {"action": "get_like_list", "echo": "get_like_list"}
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取点赞列表")
        return True
    except Exception as e:
        logger.error(f"[API]获取点赞列表失败: {e}")
        return False


async def get_collection_list(websocket):
    """
    获取收藏列表
    """
    try:
        payload = {"action": "get_collection_list", "echo": "get_collection_list"}
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取收藏列表")
        return True
    except Exception as e:
        logger.error(f"[API]获取收藏列表失败: {e}")
        return False


async def get_collection_emoji(websocket):
    """
    获取收藏表情
    """
    try:
        payload = {"action": "get_collection_emoji", "echo": "get_collection_emoji"}
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取收藏表情")
        return True
    except Exception as e:
        logger.error(f"[API]获取收藏表情失败: {e}")
        return False


async def upload_private_file(websocket, user_id, file, name):
    """
    上传私聊文件
    """
    try:
        payload = {
            "action": "upload_private_file",
            "params": {"user_id": user_id, "file": file, "name": name},
            "echo": "upload_private_file",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行上传私聊文件")
        return True
    except Exception as e:
        logger.error(f"[API]上传私聊文件失败: {e}")
        return False


async def delete_friend(
    websocket, user_id, friend_id, temp_block=False, temp_both_del=False
):
    """
    删除好友
    """
    try:
        payload = {
            "action": "delete_friend",
            "params": {
                "user_id": user_id,
                "friend_id": friend_id,
                "temp_block": temp_block,
                "temp_both_del": temp_both_del,
            },
            "echo": "delete_friend",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行删除好友")
        return True
    except Exception as e:
        logger.error(f"[API]删除好友失败: {e}")
        return False


async def get_user_status(websocket, user_id):
    """
    获取用户状态
    """
    try:
        payload = {
            "action": "get_user_status",
            "params": {"user_id": user_id},
            "echo": "get_user_status",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取用户状态")
        return True
    except Exception as e:
        logger.error(f"[API]获取用户状态失败: {e}")
        return False


async def get_mini_app_card(websocket, app_id):
    """
    获取小程序卡片
    """
    try:
        payload = {
            "action": "get_mini_app_card",
            "params": {"app_id": app_id},
            "echo": "get_mini_app_card",
        }
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行获取小程序卡片")
        return True
    except Exception as e:
        logger.error(f"[API]获取小程序卡片失败: {e}")
        return False

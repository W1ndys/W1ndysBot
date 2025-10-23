import json
from logger import logger


async def nc_get_rkey(websocket):
    """
    nc获取rkey
    """
    try:
        payload = {"action": "nc_get_rkey", "params": {}, "echo": "nc_get_rkey"}
        await websocket.send(json.dumps(payload))
        logger.info(f"[API]已执行nc获取rkey")
        return True
    except Exception as e:
        logger.error(f"[API]nc获取rkey失败: {e}")
        return False

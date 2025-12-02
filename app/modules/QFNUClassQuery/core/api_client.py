import aiohttp
from aiohttp import ClientTimeout
from logger import logger
from .. import MODULE_NAME

API_BASE_URL = "http://localhost:8001"


class QFNUClassApiClient:
    """曲奇教务 Web API 客户端"""

    @staticmethod
    async def _get(endpoint: str, params: dict):
        url = f"{API_BASE_URL}{endpoint}"
        try:
            timeout = ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(
                            f"[{MODULE_NAME}] API请求失败: {url} status={response.status}"
                        )
                        return None
                    return await response.json()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] API请求异常: {e}")
            return None

    @classmethod
    async def query_free_classroom(cls, query_text: str):
        """
        查询空教室
        :param query_text: 自然语言查询描述，如 "明天综合楼"
        """
        endpoint = "/api/free-classroom"
        params = {"query": query_text}
        return await cls._get(endpoint, params)

    @classmethod
    async def query_classroom_schedule(cls, query_text: str):
        """
        查询教室课表
        :param query_text: 自然语言查询描述
        """
        endpoint = "/api/classroom-schedule"
        params = {"query": query_text}
        return await cls._get(endpoint, params)

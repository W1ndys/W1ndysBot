import aiohttp
from aiohttp import ClientTimeout
from logger import logger
from .. import MODULE_NAME

API_BASE_URL = "http://localhost:8001"


class QFNUClassApiClient:
    """曲奇教务 Web API 客户端"""

    @staticmethod
    async def _request(method, endpoint, params=None, json=None):
        url = f"{API_BASE_URL}{endpoint}"
        try:
            timeout = ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if method.upper() == "GET":
                    response = await session.get(url, params=params)
                else:
                    response = await session.post(url, json=json)

                async with response:
                    if response.status != 200:
                        try:
                            content = await response.text()
                            import json

                            try:
                                data = json.loads(content)
                                # 尝试解析常见错误结构
                                if isinstance(data, dict):
                                    error_obj = data.get("error")
                                    if isinstance(error_obj, dict):
                                        error_text = error_obj.get(
                                            "message", str(error_obj)
                                        )
                                    elif error_obj:
                                        error_text = str(error_obj)
                                    else:
                                        # 如果没有 error 字段，尝试直接使用 content，但做一下转码处理显示中文
                                        error_text = json.dumps(
                                            data, ensure_ascii=False
                                        )
                                else:
                                    error_text = content
                            except json.JSONDecodeError:
                                error_text = content
                        except Exception:
                            error_text = "无法读取响应内容"

                        logger.error(
                            f"[{MODULE_NAME}] API请求失败: {url} status={response.status} response={error_text}"
                        )
                        return {
                            "success": False,
                            "error": f"API请求失败: HTTP {response.status} - {error_text}",
                        }
                    return await response.json()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] API请求异常: {e}")
            return {"success": False, "error": f"系统异常: {str(e)}"}

    @classmethod
    async def query_free_classroom(cls, query_text, key=None):
        """
        查询空教室
        :param query_text: 自然语言查询描述，如 "明天综合楼"
        :param key: API鉴权key
        """
        endpoint = "/api/free-classroom"
        params = {"query": query_text}
        if key:
            params["key"] = key
        return await cls._request("GET", endpoint, params=params)

    @classmethod
    async def query_classroom_schedule(cls, query_text, key=None):
        """
        查询教室课表
        :param query_text: 自然语言查询描述
        :param key: API鉴权key
        """
        endpoint = "/api/classroom-schedule"
        params = {"query": query_text}
        if key:
            params["key"] = key
        return await cls._request("GET", endpoint, params=params)

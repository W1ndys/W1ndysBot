import aiohttp
from aiohttp import ClientTimeout
from logger import logger
from .. import MODULE_NAME

API_BASE_URL = "http://127.0.0.1:8000"


class QFNUClassApiClient:
    """曲奇教务 Web API 客户端"""

    @staticmethod
    async def _request(method, endpoint, params=None, json=None):
        url = f"{API_BASE_URL}{endpoint}"
        try:
            timeout = ClientTimeout(total=10)
            headers = {"W1NDYS": "W1NDYS"}
            async with aiohttp.ClientSession(
                timeout=timeout, headers=headers
            ) as session:
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
    async def query_empty_classroom(
        cls, building: str, start_section: int, end_section: int, date_offset: int = 0
    ):
        """
        查询空教室

        :param building: 教学楼名称（如 "1号教学楼"、"综合实验楼"）
        :param start_section: 开始节次，范围 1-13
        :param end_section: 结束节次，范围 1-13
        :param date_offset: 日期偏移量，默认 0（今天），1 表示明天，-1 表示昨天
        :return: API 响应数据
        """
        endpoint = "/api/empty-classroom/query"
        params = {
            "building": building,
            "start_section": start_section,
            "end_section": end_section,
            "date_offset": date_offset,
        }
        return await cls._request("GET", endpoint, params=params)

    @classmethod
    async def get_semester_info(cls):
        """
        获取当前学期和周次信息

        :return: API 响应数据，包含 semester 和 week 字段
        """
        endpoint = "/api/empty-classroom/info"
        return await cls._request("GET", endpoint)

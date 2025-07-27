import aiohttp  # 使用 aiohttp
import asyncio
import json  # 导入 json
from logger import logger


class ElectricityQuery:
    BASE_URL = "http://wechat.sdkdch.cn/wx/api/user/get"

    # def __init__(self, openID):
    #     self.openID = openID

    async def _get_data(self, url):
        """执行异步的GET请求"""
        timeout = aiohttp.ClientTimeout(total=10)  # 设置超时对象
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:  # timeout移到session创建时
                    response.raise_for_status()  # 检查HTTP错误
                    # 确保使用正确的编码读取响应体
                    return await response.json(encoding="utf-8")
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching data from {url}: {e}")
            return {"code": 500, "msg": f"请求API失败: {e}"}  # 返回统一错误格式
        except asyncio.TimeoutError:
            logger.error(f"Timeout error fetching data from {url}")
            return {"code": 504, "msg": "请求API超时"}
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON response from {url}")
            return {"code": 500, "msg": "API响应格式错误"}

    async def get_query(self, openID):
        """根据openID获取原始查询结果"""
        if not openID:
            return {"code": 400, "msg": "openID不能为空"}
        url = f"{self.BASE_URL}?openId={openID}"
        return await self._get_data(url)

    async def parse_result(self, openID):
        """根据openID查询并解析结果，返回格式化的信息或错误信息"""
        result = await self.get_query(openID)

        if result.get("code") != 200:
            # 如果code不是200，直接返回包含错误码和消息的字典
            return {
                "code": result.get("code", 500),
                "message": result.get("msg", "查询失败，未知错误"),
            }

        if result.get("total", 0) == 0 or not result.get("rows"):
            return {
                "code": 404,
                "message": "未找到电费信息，可能是你未绑定新校区宿舍户号信息，相关信息在物业提供的表格里",
            }  # 使用不同的code表示未找到

        user_info = result["rows"][0]
        # 格式化输出，确保余额只保留两位小数
        try:
            balance = float(user_info.get("balance", "0"))
            formatted_balance = f"{balance:.2f}"
        except (ValueError, TypeError):
            formatted_balance = "无效值"

        message = (
            f"查询成功！\n"
            # f"用户编号: {user_info.get('userNumber', '无')}\n"
            # f"用户名: {user_info.get('userName', '无')}\n"
            f"余额: {formatted_balance}\n"
            # f"地址: {user_info.get('address', '无')}\n"
            # f"客户名称: {user_info.get('customerName', '无')}"
        )

        return {"code": 200, "message": message}

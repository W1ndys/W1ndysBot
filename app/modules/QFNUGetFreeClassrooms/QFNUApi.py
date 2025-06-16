import logger
import aiohttp
import asyncio
from typing import Dict, Any


class QFNUApiManager:
    """
    曲阜师范大学教务系统API管理器。

    使用一个cookies来执行具体的API请求。
    """

    BASE_URL = "http://zhjw.qfnu.edu.cn/jsxsd"

    def __init__(self, cookies: dict):
        """
        初始化API管理器。

        :param session: 一个已经包含登录Cookies的 aiohttp.ClientSession 对象。
                        这个session应该由 QFNULoginManager 提供。
        """
        self.cookies = cookies

    async def get_classroom_schedule(
        self,
        xnxqh: str,
        week: int,
        day: int,
        start_period: str,
        end_period: str,
        building_name: str = "",
    ) -> Dict[str, Any]:
        """
        请求空闲教室数据API。
        该函数对应原项目中的 get_room_classtable 功能。

        :param xnxqh: 学年学期号, 例如 "2024-2025-1"
        :param week: 周次 (整数)
        :param day: 星期几 (1-7)
        :param start_period: 开始节次, 例如 "01"
        :param end_period: 结束节次, 例如 "02"
        :param building_name: 教学楼名称 (可选)
        :return: 一个包含API原始响应的字典，或在失败时返回包含 'error' 键的字典。
        """
        api_url = f"{self.BASE_URL}/kbcx/kbxx_classroom_fty_query"

        headers = {
            "Referer": f"{self.BASE_URL}/kbcx/kbxx_classroom_fty",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }

        # API请求的表单数据 (字段名根据实际抓包情况可能需要调整)
        payload = {
            "xnxqh": xnxqh,
            "jsmc": building_name,  # 教室名称
            "zc": str(week),  # 周次
            "xqj": str(day),  # 星期几
            "jcd1": start_period,  # 节次段1
            "jcd2": end_period,  # 节次段2
        }

        try:
            async with aiohttp.ClientSession(cookies=self.cookies) as session:
                async with session.post(
                    api_url,
                    headers=headers,
                    data=payload,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as response:
                    if response.status == 200:
                        try:
                            # 返回解析后的JSON数据
                            return await response.json()
                        except aiohttp.ContentTypeError:
                            logger.error("API响应不是有效的JSON格式。")
                            return {"error": "API响应格式错误，无法解析。"}
                    else:
                        logger.error(f"API请求失败，HTTP状态码: {response.status}")
                        return {"error": f"服务器返回错误，状态码 {response.status}"}
        except asyncio.TimeoutError:
            logger.error("API请求超时。")
            return {"error": "请求超时，请稍后再试。"}
        except Exception as e:
            logger.error(f"API请求时发生未知错误: {e}")
            return {"error": f"发生未知网络错误: {e}"}


# --- 最终协同工作示例 ---
# (此处省略 QFNULoginManager 和 ClassroomDataManager 的完整代码)
# 假设它们已经被定义


class ClassroomDataManager:
    def format_free_classrooms_message(self, api_result, query_params):
        if "error" in api_result:
            return f"查询失败: {api_result['error']}"
        # ... (省略之前的完整格式化逻辑)
        free_rooms = ["格物楼A102", "致知楼B201", "综合教学楼C301"]  # 模拟计算结果
        building_prefix = query_params["building_prefix"]
        message = f"【空闲教室查询结果 for {building_prefix}】\n\n"
        message += ", ".join(free_rooms)
        return message


async def main_workflow():
    print("--- 演示三个类如何协同工作 ---")

    # 模拟一个已经登录成功的 LoginManager，它持有一个包含有效cookies的session
    # 在真实场景中，你会调用 login_manager.ensure_login()
    mock_cookies = {"JSESSIONID": "MOCK_SESSION_ID_12345"}
    mock_session = aiohttp.ClientSession(cookies=mock_cookies)
    print("步骤 1: (模拟)登录成功，获取到包含Cookies的Session。")

    # 步骤 2: 使用已登录的session初始化ApiManager
    api_manager = QFNUApiManager(cookies=mock_cookies)
    print("步骤 2: 使用Session初始化ApiManager。")

    # 步骤 3: 准备查询参数并发起API请求
    query_params = {
        "xnxqh": "2024-2025-1",
        "building_prefix": "格物楼",
        "week": 12,
        "day": 3,
        "start_period": "03",
        "end_period": "04",
    }
    print("\n步骤 3: 调用ApiManager获取原始数据...")
    raw_api_data = await api_manager.get_classroom_schedule(
        xnxqh=query_params["xnxqh"],
        week=query_params["week"],
        day=query_params["day"],
        start_period=query_params["start_period"],
        end_period=query_params["end_period"],
        building_name=query_params["building_prefix"],
    )
    print("API返回的原始数据:", raw_api_data)

    # 步骤 4: 检查API请求是否成功，如果成功，则用DataManager处理数据
    if "error" in raw_api_data:
        final_message = f"处理API请求失败: {raw_api_data['error']}"
    else:
        print("\n步骤 4: API请求成功，使用DataManager处理原始数据...")
        data_manager = ClassroomDataManager()  # 假设classroom.json已配置
        final_message = data_manager.format_free_classrooms_message(
            api_result=raw_api_data, query_params=query_params
        )

    # 步骤 5: 得到最终要发送给用户的消息
    print("\n步骤 5: 得到最终格式化好的消息:")
    print("=" * 30)
    print(final_message)
    print("=" * 30)


if __name__ == "__main__":
    asyncio.run(main_workflow())

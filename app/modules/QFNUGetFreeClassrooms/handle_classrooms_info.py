import os
import json
import logger
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from . import CLASSROOMS_JSON_PATH

# 确保 classrooms.txt 文件存在 (用于演示)
if not os.path.exists(CLASSROOMS_JSON_PATH):
    sample_data = (
        "格物楼A101\n格物楼A102\n致知楼B201\n致知楼B202\n综合教学楼C301\n综合教学楼C302"
    )
    with open(CLASSROOMS_JSON_PATH, "w", encoding="utf-8") as f:
        f.write(sample_data)

# --- 封装的教室数据处理类 ---


def extract_classroom_names(html_content: str) -> str:
    """
    从提供的HTML课表内容中解析并提取所有教室的名称。

    Args:
        html_content: 包含课表信息的HTML字符串。

    Returns:
        一个字符串，其中包含所有不重复的教室名称，每个名称占一行。
    """
    # 使用'html.parser'作为解析器初始化BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # 查找ID为'kbtable'的表格
    table = soup.find("table", id="kbtable")
    if not table:
        return "错误：未在HTML中找到ID为 'kbtable' 的表格。"

    classroom_names = []
    # 查找表格中所有在 <thead> 标签之后的 <tr> 标签（即表格内容行）
    # 这种方法可以有效避免处理表头行
    for row in table.find("thead").find_next_siblings("tr"):  # type: ignore
        # 教室名称位于每行的第一个 <td> 单元格中
        first_cell = row.find("td")  # type: ignore
        # 确保单元格存在，并且其中包含 <nobr> 标签
        if first_cell and first_cell.nobr:  # type: ignore
            # 提取 <nobr> 标签内的文本，并使用 strip=True 清除前后多余的空白字符
            name = first_cell.nobr.get_text(strip=True)  # type: ignore
            # 确保提取到的名称不为空
            if name:
                classroom_names.append(name)

    # 将提取到的教室名称列表用换行符连接成一个字符串
    return "\n".join(classroom_names)


async def get_classrooms_info(session, xnxqh: str) -> bool:
    """
    获取本学期所有教室名字并保存到本地文件

    Args:
        session: aiohttp会话对象
        xnxqh: 学年学期号,如 2024-2025-2

    Returns:
        str: 教室列表
    """
    url = "http://zhjw.qfnu.edu.cn/jsxsd/kbcx/kbxx_classroom_ifr"

    data = {
        "xnxqh": xnxqh,
        "kbjcmsid": "94786EE0ABE2D3B2E0531E64A8C09931",
        "skyx": "",
        "xqid": "",
        "jzwid": "",
        "skjsid": "",
        "skjs": "",
        "zc1": "",
        "zc2": "",
        "skxq1": "",
        "skxq2": "",
        "jc1": "",
        "jc2": "",
    }

    async with session.post(url, data=data) as response:
        response.raise_for_status()
        html_content = await response.text()
        classroom_names = extract_classroom_names(html_content)
        with open(f"{xnxqh}-{CLASSROOMS_JSON_PATH}", "w", encoding="utf-8") as f:
            f.write(classroom_names)
        return True


class ClassroomDataManager:
    """
    教室数据处理器。

    负责加载、解析、筛选和格式化教室数据。
    """

    WEEKDAY_NAMES = {
        1: "星期一",
        2: "星期二",
        3: "星期三",
        4: "星期四",
        5: "星期五",
        6: "星期六",
        7: "星期日",
    }

    def __init__(self, classrooms_json_path: str = CLASSROOMS_JSON_PATH):
        """
        初始化教室数据处理器。

        :param classrooms_json_path: 包含所有教室列表的JSON文件路径。
        """
        self.all_classrooms = self._load_all_classrooms(classrooms_json_path)

    def _load_all_classrooms(self, file_path: str) -> list[str]:
        """从JSON文件加载所有教室的列表。"""
        if not os.path.exists(file_path):
            logger.error(f"教室配置文件不存在: {file_path}")
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                classrooms = data.get("classrooms", [])
                logger.info(f"成功从 {file_path} 加载 {len(classrooms)} 个教室。")
                return classrooms
        except Exception as e:
            logger.error(f"读取教室配置文件 {file_path} 出错: {e}")
            return []

    def get_filtered_classrooms(self, building_prefix: str | None = None) -> list[str]:
        """
        根据教学楼前缀筛选教室列表。

        :param building_prefix: 教学楼名称或前缀, 如 "格物楼", "综合"。
        :return: 筛选后的教室列表。
        """
        if not building_prefix:
            return self.all_classrooms

        # 增加对常见简称的处理
        if building_prefix == "综合楼":
            building_prefix = "综合教学楼"
        elif building_prefix and re.match(r"J[A-Z]楼", building_prefix.upper()):
            building_prefix = "J" + building_prefix.upper()[1]

        return [
            room
            for room in self.all_classrooms
            if room.startswith(building_prefix) or building_prefix in room
        ]

    def _extract_occupied_rooms(self, api_result: dict) -> set[str]:
        """
        从教务系统API返回的JSON结果中提取被占用的教室。

        :param api_result: get_room_classtable 函数返回的字典。
        :return: 一个包含被占用教室名称的集合。
        """
        occupied_rooms = set()
        if "data" in api_result and api_result["data"]:
            for room_data in api_result["data"]:
                room_name = room_data.get("name", "")
                if room_name:
                    occupied_rooms.add(room_name)
        return occupied_rooms

    def _group_rooms_by_building(self, rooms: list[str]) -> dict[str, list[str]]:
        """将教室列表按教学楼名称分组。"""
        buildings = {}
        for room in rooms:
            # 使用正则表达式匹配教学楼名称部分
            match = re.match(r"(.*?)[A-Z]?\d+", room)
            if match:
                building_name = match.group(1)
                if building_name not in buildings:
                    buildings[building_name] = []
                buildings[building_name].append(room)
            else:
                # 如果无法匹配，则归类到"其他"
                if "其他" not in buildings:
                    buildings["其他"] = []
                buildings["其他"].append(room)
        return buildings

    def format_free_classrooms_message(
        self,
        api_result: dict,
        query_params: dict,
        user_id: str,
        # 假设的邀请管理器，用于获取剩余次数
        invitation_manager=None,
    ) -> str:
        """
        处理API结果并格式化为空闲教室查询消息。

        :param api_result: 来自教务系统的原始API响应数据。
        :param query_params: 包含查询参数的字典，如 xnxqh, week, day, jc1, jc2, building_prefix 等。
        :param user_id: 查询用户的ID。
        :param invitation_manager: 邀请管理器实例，用于扣减和显示次数。
        :return: 格式化后的完整消息字符串。
        """
        building_prefix = query_params.get("building_prefix", "")

        # 1. 根据查询条件筛选出目标教学楼的所有教室
        target_classrooms = self.get_filtered_classrooms(building_prefix)

        # 2. 从API结果中提取出已被占用的教室
        occupied_rooms = self._extract_occupied_rooms(api_result)

        # 3. 计算空闲教室
        free_rooms = sorted(
            [room for room in target_classrooms if room not in occupied_rooms]
        )

        # --- 4. 构建消息字符串 ---
        # 构建消息头
        days_ahead = query_params.get("days_ahead", 0)
        target_date = datetime.now() + timedelta(days=days_ahead)
        formatted_date = target_date.strftime("%Y-%m-%d")
        jc_str = f"{int(query_params['jc1'])}-{int(query_params['jc2'])}节"
        day_str = self.WEEKDAY_NAMES.get(query_params["day"], "未知")

        day_suffix = ""
        if days_ahead == 1:
            day_suffix = "（明天）"
        elif days_ahead == 2:
            day_suffix = "（后天）"
        elif days_ahead > 2:
            day_suffix = f"（{days_ahead}天后）"

        message = "【空闲教室查询结果】\n\n"
        message += f"学期: {query_params['xnxqh']}\n"
        message += f"查询条件: 第{query_params['week']}周 {day_str}{day_suffix} {formatted_date} {jc_str} {building_prefix or '所有教学楼'}\n\n"

        # 构建消息主体
        if free_rooms:
            grouped_free_rooms = self._group_rooms_by_building(free_rooms)
            for building, rooms in sorted(grouped_free_rooms.items()):
                message += f"📍 {building}:\n"
                message += ", ".join(rooms) + "\n\n"
        else:
            message += f"🤷 在指定条件下未找到空闲教室。\n\n"
            message += f"🤔 可能原因：\n"
            message += f"1. 该时段确实没有空闲教室。\n"
            message += f"2. 教学楼名称 ('{building_prefix}') 输入有误或不存在。\n"
            message += "💡 请检查参数或尝试其他条件。\n"

        # --- 5. 处理用户次数 (示例) ---
        if invitation_manager and user_id:
            invitation_manager.decrease_usage_count(user_id)  # 扣除次数
            current_count = invitation_manager.get_available_count(
                user_id
            )  # 获取剩余次数
            message += f"(当前剩余{current_count}次)\n\n"

        message += f"🕒 查询时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return message


# --- 使用示例 ---
# 假设这是在您的主逻辑文件中（例如 main.py）
async def run_example_query():

    # 假设这是从 get_room_classtable 得到的模拟API结果
    mock_api_result = {
        "data": [{"name": "格物楼A101"}, {"name": "致知楼B202"}],
        "message": "success",
    }

    # 假设这是用户输入的查询参数
    mock_query_params = {
        "xnxqh": "2024-2025-1",
        "building_prefix": "格物楼",
        "week": 12,
        "day": 3,  # 星期三
        "jc1": "03",
        "jc2": "04",
        "days_ahead": 2,
    }

    mock_user_id = "123456789"

    # 1. 初始化数据处理器
    data_manager = ClassroomDataManager()

    # 2. 调用核心方法处理数据并格式化消息
    # (在真实场景中，invitation_manager 需要被实例化并传入)
    final_message = data_manager.format_free_classrooms_message(
        api_result=mock_api_result,
        query_params=mock_query_params,
        user_id=mock_user_id,
        invitation_manager=None,  # 此处为演示，传入None
    )

    # 3. 打印最终要发送给用户的消息
    print("--- 生成的消息如下 ---")
    print(final_message)

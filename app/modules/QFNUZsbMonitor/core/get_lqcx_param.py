from .QFNUZsbClient import QfnuAdmissionsClient

# from QFNUZsbClient import QfnuAdmissionsClient
import time


class GetLqcx(QfnuAdmissionsClient):
    """
    用于请求曲阜师范大学招生信息网录取查询参数的客户端。
    继承自QfnuAdmissionsClient，复用会话管理和请求功能。
    """

    def __init__(self):
        """
        初始化客户端。
        """
        super().__init__()
        base_url = "https://zsb.qfnu.edu.cn"
        # 录取查询相关的URL配置
        self.lqcx_page_url = f"{base_url}/static/front/qfnu/basic/html_web/lqcx.html"
        self.csrf_token_url = f"{base_url}/f/ajax_token"
        self.lqcx_param_url = f"{base_url}/f/ajax_lqcx_param"

        # 状态映射
        self.status_map = {
            "0": "录取未开始",
            "1": "录取开始阅档中",
            "2": "可网上查询结果",
            "3": "通知书已寄出",
        }

    def get_lqcx_param(self):
        """
        获取录取查询参数。
        """

        current_timestamp = str(int(time.time() * 1000))

        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Csrf-Token": self.csrf_token,
            "X-Requested-Time": current_timestamp,
            "Origin": "https://zsb.qfnu.edu.cn",
            "Referer": "https://zsb.qfnu.edu.cn/static/front/qfnu/basic/html_web/lqcx.html",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
        }

        params = {"ts": current_timestamp}

        response = self.session.post(
            self.lqcx_param_url, params=params, headers=headers, timeout=2
        )
        response.raise_for_status()
        return response.json()

    def parse_zsstate_data(self, response_data):
        """
        解析招生状态数据，返回每个省份每种类别的进度信息。

        Args:
            response_data: API响应的完整数据

        Returns:
            dict: 格式化后的省份招生状态信息
        """
        if not response_data.get("data") or not response_data["data"].get("zsState"):
            return {"error": "没有找到招生状态数据"}

        zs_state = response_data["data"]["zsState"]

        if len(zs_state) < 2:
            return {"error": "招生状态数据格式不正确"}

        # 获取表头（类别名称）
        headers = zs_state[0]
        categories = headers[1:]  # 跳过"省份"列

        # 解析数据
        result = {
            "year": response_data["data"].get("nf", "未知年份"),
            "school_name": response_data["data"].get("schoolName", "未知学校"),
            "can_query": response_data["data"].get("canLqcx", False),
            "provinces": {},
        }

        # 遍历每个省份的数据
        for row in zs_state[1:]:
            if len(row) != len(headers):
                continue

            province = row[0]
            province_data = {}

            # 解析每个类别的状态
            for i, category in enumerate(categories):
                status_code = row[i + 1]  # +1 因为跳过了省份列

                if status_code and status_code.strip():
                    status_text = self.status_map.get(
                        status_code, f"未知状态({status_code})"
                    )
                    province_data[category] = {
                        "status_code": status_code,
                        "status_text": status_text,
                    }
                else:
                    province_data[category] = {
                        "status_code": "",
                        "status_text": "暂无信息",
                    }

            result["provinces"][province] = province_data

        return result

    def get_formatted_zsstate(self):
        """
        获取并格式化招生状态信息。

        Returns:
            dict: 包含格式化招生状态信息的字典
        """
        try:
            raw_data = self.get_lqcx_param()
            return self.parse_zsstate_data(raw_data)
        except Exception as e:
            return {"error": f"获取招生状态失败: {str(e)}"}


if __name__ == "__main__":
    client = GetLqcx()
    print(client.get_lqcx_param())
    print(client.get_formatted_zsstate())

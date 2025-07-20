import requests
import time
from urllib.parse import quote


class QfnuAdmissionsClient:
    """
    一个模拟请求曲阜师范大学招生计划数据的客户端。
    """

    def __init__(self):
        self.csrf_token_url = "https://zsb.qfnu.edu.cn/f/ajax_get_csrfToken"
        self.html_page_url = (
            "https://zsb.qfnu.edu.cn/static/front/qfnu/basic/html_web/lqcx.html"
        )
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        # Session对象会自动处理Cookie的获取和发送
        self.session = requests.Session()
        self.session.headers.update(self.base_headers)

        self.csrf_token = None

        # 初始化会话，获取Cookie和CSRF Token
        self._initialize_session()

    def _initialize_session(self):
        """
        初始化会话：
        1. 访问页面获取Cookie
        2. 获取CSRF Token
        """
        try:
            print("正在初始化会话...")

            # 1. 访问目标页面获取Cookie
            response = self.session.get(self.html_page_url, timeout=3)
            response.raise_for_status()

            print(f"访问页面后的Cookie: {self.session.cookies}")

            if not self.session.cookies:
                print("警告：未获取到Cookie，尝试访问主页...")
                main_response = self.session.get("https://zsb.qfnu.edu.cn/", timeout=3)
                print(f"访问主页后的Cookie: {self.session.cookies}")

            # 2. 获取CSRF Token
            self._get_csrf_token()

        except requests.exceptions.RequestException as e:
            print(f"初始化会话失败: {e}")
            raise

    def _get_csrf_token(self):
        """
        获取CSRF Token
        """
        try:
            current_timestamp = str(int(time.time() * 1000))

            csrf_headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-Time": current_timestamp,
                "Origin": "https://zsb.qfnu.edu.cn",
                "Referer": self.html_page_url,
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
            }

            csrf_params = {"ts": current_timestamp}
            csrf_payload = "n=3"

            print("正在获取CSRF Token...")
            response = self.session.post(
                self.csrf_token_url,
                params=csrf_params,
                headers=csrf_headers,
                data=csrf_payload,
                timeout=3,
            )
            response.raise_for_status()

            response_json = response.json()

            if response_json.get("state") == 1:
                token_data = response_json.get("data", "")
                self._original_token_data = token_data
                print(f"获取到新的CSRF Token: {token_data}")

                if "," in token_data:
                    token_parts = token_data.split(",")
                    self.csrf_token = token_parts[0] if token_parts else token_data
                    print(f"使用第一个片段作为CSRF Token: {self.csrf_token}")
                else:
                    self.csrf_token = token_data

                return True
            else:
                print(f"获取CSRF Token失败: {response_json.get('msg', '未知错误')}")
                return False

        except Exception as e:
            print(f"获取CSRF Token时发生错误: {e}")
            return False

import requests
import json
import time
from urllib.parse import quote


class QFNUZsbClient:
    """
    通用HTTP客户端类，提供会话管理、Cookie处理、CSRF Token获取等功能
    """

    def __init__(self, base_url=None, headers=None):
        """
        初始化HTTP客户端

        Args:
            base_url (str): 基础URL
            headers (dict): 默认请求头
        """
        self.base_url = base_url
        self.default_headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        # 创建会话对象
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)

        # CSRF Token相关
        self.csrf_token = None
        self._original_token_data = None

    def visit_page(self, url, timeout=10):
        """
        访问页面以获取Cookie

        Args:
            url (str): 要访问的URL
            timeout (int): 超时时间

        Returns:
            bool: 是否成功访问
        """
        try:
            print(f"正在访问页面: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            print(f"访问成功，获取到Cookie: {self.session.cookies}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"访问页面失败: {e}")
            return False

    def get_csrf_token(self, token_url, payload="n=3", method="POST"):
        """
        获取CSRF Token

        Args:
            token_url (str): 获取Token的URL
            payload (str): 请求载荷
            method (str): 请求方法

        Returns:
            bool: 是否成功获取Token
        """
        try:
            current_timestamp = str(int(time.time() * 1000))

            csrf_headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-Time": current_timestamp,
                "Origin": self.base_url,
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
            }

            params = {"ts": current_timestamp}

            print("正在获取CSRF Token...")

            if method.upper() == "POST":
                response = self.session.post(
                    token_url,
                    params=params,
                    headers=csrf_headers,
                    data=payload,
                    timeout=10,
                )
            else:
                response = self.session.get(
                    token_url,
                    params=params,
                    headers=csrf_headers,
                    timeout=10,
                )

            response.raise_for_status()
            response_json = response.json()

            if response_json.get("state") == 1:
                token_data = response_json.get("data", "")
                self._original_token_data = token_data
                print(f"获取到CSRF Token: {token_data}")

                # 处理包含逗号的Token
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

    def make_request(
        self,
        url,
        method="GET",
        data=None,
        params=None,
        headers=None,
        include_csrf=False,
        referer=None,
        timeout=30,
    ):
        """
        发送HTTP请求

        Args:
            url (str): 请求URL
            method (str): 请求方法
            data (str|dict): POST数据
            params (dict): URL参数
            headers (dict): 额外的请求头
            include_csrf (bool): 是否包含CSRF Token
            referer (str): Referer头
            timeout (int): 超时时间

        Returns:
            dict|None: 响应的JSON数据，失败返回None
        """
        try:
            current_timestamp = str(int(time.time() * 1000))

            # 构建请求头
            request_headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-Time": current_timestamp,
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
            }

            if self.base_url:
                request_headers["Origin"] = self.base_url

            if referer:
                request_headers["Referer"] = referer

            if include_csrf and self.csrf_token:
                request_headers["Csrf-Token"] = self.csrf_token

            if headers:
                request_headers.update(headers)

            # 构建参数
            if not params:
                params = {}
            params["ts"] = current_timestamp

            print(f"正在发送{method}请求: {url}")
            if include_csrf:
                print(f"使用CSRF Token: {self.csrf_token}")

            # 发送请求
            if method.upper() == "POST":
                response = self.session.post(
                    url,
                    params=params,
                    headers=request_headers,
                    data=data,
                    timeout=timeout,
                )
            else:
                response = self.session.get(
                    url,
                    params=params,
                    headers=request_headers,
                    timeout=timeout,
                )

            response.raise_for_status()

            try:
                response_json = response.json()
                return response_json
            except json.JSONDecodeError as e:
                print(f"响应不是有效的JSON格式: {e}")
                print(f"响应内容: {response.text[:500]}")
                return None

        except Exception as e:
            print(f"请求过程中发生错误: {e}")
            return None

    def url_encode_params(self, params_dict):
        """
        将参数字典编码为URL编码格式的字符串

        Args:
            params_dict (dict): 参数字典

        Returns:
            str: URL编码后的字符串
        """
        encoded_params = []
        for key, value in params_dict.items():
            encoded_key = quote(str(key))
            encoded_value = quote(str(value))
            encoded_params.append(f"{encoded_key}={encoded_value}")

        return "&".join(encoded_params)

    def initialize_session(self, page_urls, csrf_config=None):
        """
        初始化会话：访问页面获取Cookie并获取CSRF Token

        Args:
            page_urls (str|list): 要访问的页面URL，可以是单个URL或URL列表
            csrf_config (dict): CSRF Token配置，包含url, payload, method等

        Returns:
            bool: 是否初始化成功
        """
        try:
            print("正在初始化会话...")

            # 访问页面获取Cookie
            if isinstance(page_urls, str):
                page_urls = [page_urls]

            for url in page_urls:
                if not self.visit_page(url):
                    print(f"访问页面 {url} 失败")
                    return False

            # 获取CSRF Token（如果提供了配置）
            if csrf_config:
                token_url = csrf_config.get("url")
                payload = csrf_config.get("payload", "n=3")
                method = csrf_config.get("method", "POST")

                if token_url:
                    if not self.get_csrf_token(token_url, payload, method):
                        print("获取CSRF Token失败")
                        return False

            print("会话初始化成功")
            return True

        except Exception as e:
            print(f"初始化会话失败: {e}")
            return False

    def get_session_info(self):
        """
        获取当前会话信息

        Returns:
            dict: 会话信息
        """
        return {
            "cookies": dict(self.session.cookies),
            "csrf_token": self.csrf_token,
            "original_token_data": self._original_token_data,
            "headers": dict(self.session.headers),
        }

    def close_session(self):
        """
        关闭会话
        """
        if self.session:
            self.session.close()
            print("会话已关闭")

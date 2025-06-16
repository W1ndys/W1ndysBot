import base64
import logger
import time
import asyncio
from io import BytesIO
import aiohttp
from PIL import Image
from captcha_ocr import get_ocr_res
from .data_manager import DataManager


class LoginHandler:
    """
    处理曲阜师范大学教务系统登录的类。

    通过此类可以模拟登录并获取包含 cookies 的 session 对象。

    属性:
        LOGIN_URL (str): 登录页面的URL。
        CAPTCHA_URL (str): 验证码图片的URL。
        HOME_URL (str): 教务系统主页的URL。
        HEADERS (dict): 登录时使用的请求头。
    """

    LOGIN_URL = "http://zhjw.qfnu.edu.cn/jsxsd/xk/LoginToXkLdap"
    CAPTCHA_URL = "http://zhjw.qfnu.edu.cn/jsxsd/verifycode.servlet"
    HOME_URL = "http://zhjw.qfnu.edu.cn/jsxsd/"

    HEADERS = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Origin": "http://zhjw.qfnu.edu.cn",
        "Referer": "http://zhjw.qfnu.edu.cn/",
    }

    def __init__(self, user_account: str, user_password: str):
        """
        初始化登录处理器。

        Args:
            user_account (str): 用户的学号/账号。
            user_password (str): 用户的密码。
        """
        if not user_account or not user_password:
            raise ValueError("账号和密码不能为空")

        self.user_account = user_account
        self.user_password = user_password
        self.session = None
        self.cookies = {}

    async def _get_captcha_code(self, session) -> str:
        """
        获取并识别验证码。

        Args:
            session (aiohttp.ClientSession): 当前的会话对象

        Returns:
            str: 识别出的验证码字符串。

        Raises:
            Exception: 如果请求验证码失败或无法处理图像。
        """
        logger.info("正在请求验证码...")
        try:
            async with session.get(
                self.CAPTCHA_URL, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()  # 如果状态码不是 2xx, 则引发 HTTPError
                content = await response.read()

            image = Image.open(BytesIO(content))
            captcha_code = get_ocr_res(image)
            if captcha_code:
                logger.info(f"成功识别验证码: {captcha_code}")
                return str(captcha_code)  # 确保返回字符串类型
            return ""  # 添加默认返回值

        except aiohttp.ClientError as e:
            logger.error(f"请求验证码失败: {e}")
            raise Exception(f"请求验证码失败: {e}") from e
        except Exception as e:
            logger.error(f"无法识别验证码图像: {e}")
            raise Exception(f"无法识别验证码图像: {e}") from e

    def _generate_encoded_string(self) -> str:
        """
        生成登录所需的 encoded 字符串。
        (账号base64)%%% (密码base64)

        Returns:
            str: 编码后的字符串。
        """
        account_b64 = base64.b64encode(self.user_account.encode()).decode()
        password_b64 = base64.b64encode(self.user_password.encode()).decode()
        encoded = f"{account_b64}%%%{password_b64}"
        logger.info("已生成加密凭证 (encoded string)。")
        return encoded

    async def login(self, max_retries: int = 3) -> dict:
        """
        执行完整的登录流程。

        首先访问首页以初始化会话，然后循环尝试登录，直到成功或达到最大重试次数。

        Args:
            max_retries (int): 验证码错误时的最大重试次数。

        Returns:
            dict: 包含登录后 cookies 的字典。

        Raises:
            Exception: 如果在多次尝试后登录仍然失败。
        """
        # 创建异步会话
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            # 1. 访问教务系统首页，获取初始化的 session cookie
            try:
                logger.info(f"正在访问教务系统首页: {self.HOME_URL}")
                async with session.get(
                    self.HOME_URL, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    # 保存初始cookies
                    self.cookies.update(
                        {k: v.value for k, v in response.cookies.items()}
                    )
            except aiohttp.ClientError as e:
                logger.error("无法访问教务系统首页，请检查网络或URL。")
                raise Exception("无法访问教务系统首页") from e

            # 2. 生成加密凭证
            encoded_creds = self._generate_encoded_string()

            # 3. 循环尝试登录
            for attempt in range(max_retries):
                logger.info(
                    f"--- 正在进行第 {attempt + 1}/{max_retries} 次登录尝试 ---"
                )

                # 获取验证码
                captcha_code = await self._get_captcha_code(session)
                if not captcha_code:
                    logger.warning("未能获取验证码，稍后重试...")
                    await asyncio.sleep(1)
                    continue

                # 准备POST数据
                data = {
                    "userAccount": "",
                    "userPassword": "",
                    "RANDOMCODE": captcha_code,
                    "encoded": encoded_creds,
                }

                try:
                    # 发送登录请求
                    async with session.post(
                        self.LOGIN_URL,
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as response:
                        response.raise_for_status()
                        text = await response.text()

                        # 更新cookies
                        self.cookies.update(
                            {k: v.value for k, v in response.cookies.items()}
                        )

                        # 检查登录结果
                        if "验证码错误" in text:
                            logger.warning(
                                f"验证码识别错误，即将重试 (剩余 {max_retries - attempt - 1} 次)..."
                            )
                            await asyncio.sleep(1)
                            continue

                        if "密码错误" in text or "用户名不存在" in text:
                            logger.error("登录失败：用户名或密码错误。")
                            raise Exception("用户名或密码错误")

                        # 通过检查响应中是否包含特定标识来确认成功，例如跳转到主页
                        # 这里假设只要不报错且不提示验证码或密码错误，就是成功
                        logger.info("✅ 登录成功！")

                        # 保存cookies
                        with DataManager() as dm:
                            dm.update_cookies(self.cookies)
                        return self.cookies

                except aiohttp.ClientError as e:
                    logger.error(f"登录请求期间发生网络错误: {e}")
                    raise Exception(f"登录请求失败: {e}") from e

            raise Exception(f"登录失败：在尝试 {max_retries} 次后，验证码依然错误。")

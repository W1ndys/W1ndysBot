import aiohttp
import asyncio
import os
import json
from . import DIFY_API_KEY_FILE, MODULE_NAME
import logger


class DifyClient:
    """Dify API 客户端类"""

    def __init__(self):
        """
        初始化 Dify 客户端

        Args:
            api_keys_dir: API 密钥存储目录，如果为 None 则使用默认目录
        """
        self.api_keys_dir = DIFY_API_KEY_FILE

        self.api_url = "https://api.dify.ai/v1/chat-messages"

    def get_api_key(self):
        """
        从文件中获取API密钥

        Returns:
            str: API 密钥，如果获取失败返回空字符串
        """
        try:
            # 如果文件不存在，返回空字符串
            if not os.path.exists(self.api_keys_dir):
                logger.error(
                    f"[{MODULE_NAME}]Dify API密钥文件不存在: {self.api_keys_dir}"
                )
                return ""

            with open(self.api_keys_dir, "r", encoding="utf-8") as f:
                api_key = f.read().strip()

            return api_key
        except Exception as e:
            print(f"获取API密钥失败: {e}")
            return ""

    async def send_request(self, user_id, message, conversation_id=""):
        """
        发送请求到 Dify API

        Args:
            user_id (str): 用户ID
            message (str): 要发送的消息
            conversation_id (str): 对话ID，默认为空字符串

        Returns:
            str: API 响应的 JSON 字符串
        """
        # 获取API密钥
        api_key = self.get_api_key()

        # 如果没有API密钥，返回错误信息
        if not api_key:
            logger.error(f"[{MODULE_NAME}]Dify API密钥为空")
            return ""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "inputs": {},
            "query": message,
            "conversation_id": conversation_id,
            "response_mode": "blocking",
            "user": user_id,
            "files": [],
        }

        # 设置重试次数
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 设置超时时间
                timeout = aiohttp.ClientTimeout(total=60, connect=10)

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    logger.info(f"[{MODULE_NAME}]尝试第 {attempt + 1} 次请求 Dify API")
                    async with session.post(
                        self.api_url, headers=headers, json=data
                    ) as response:
                        if response.status == 200:
                            result = await response.text()
                            logger.info(f"[{MODULE_NAME}]Dify API 请求成功")
                            return result
                        else:
                            logger.error(
                                f"[{MODULE_NAME}]API 返回状态码: {response.status}"
                            )

            except asyncio.TimeoutError:
                logger.error(
                    f"[{MODULE_NAME}]请求超时 (尝试 {attempt + 1}/{max_retries})"
                )
                if attempt == max_retries - 1:
                    return json.dumps(
                        {
                            "answer": "请求超时，请稍后重试",
                            "metadata": {
                                "usage": {
                                    "total_tokens": 0,
                                    "total_price": 0,
                                    "currency": "USD",
                                }
                            },
                        }
                    )

            except aiohttp.ClientConnectorError as e:
                logger.error(
                    f"[{MODULE_NAME}]连接错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                )
                if attempt == max_retries - 1:
                    return json.dumps(
                        {
                            "answer": "网络连接失败，请检查网络设置",
                            "metadata": {
                                "usage": {
                                    "total_tokens": 0,
                                    "total_price": 0,
                                    "currency": "USD",
                                }
                            },
                        }
                    )

            except Exception as e:
                logger.error(
                    f"[{MODULE_NAME}]请求失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                )
                if attempt == max_retries - 1:
                    return json.dumps(
                        {
                            "answer": f"请求失败: {str(e)}",
                            "metadata": {
                                "usage": {
                                    "total_tokens": 0,
                                    "total_price": 0,
                                    "currency": "USD",
                                }
                            },
                        }
                    )

            # 如果不是最后一次尝试，等待一段时间再重试
            if attempt < max_retries - 1:
                await asyncio.sleep(2**attempt)  # 指数退避：2, 4, 8 秒

        return json.dumps(
            {
                "answer": "所有重试尝试都失败了",
                "metadata": {
                    "usage": {"total_tokens": 0, "total_price": 0, "currency": "USD"}
                },
            }
        )

    @staticmethod
    def parse_response(response_text):
        """
        解析 Dify API 返回的响应

        Args:
            response_text (str): API 响应的 JSON 字符串

        Returns:
            tuple: (answer, total_tokens, total_price, currency)
        """
        try:
            response = json.loads(response_text)
            return (
                response.get("answer", ""),
                response.get("metadata", {}).get("usage", {}).get("total_tokens", 0),
                response.get("metadata", {}).get("usage", {}).get("total_price", 0),
                response.get("metadata", {}).get("usage", {}).get("currency", "USD"),
            )
        except json.JSONDecodeError as e:
            print(f"解析响应失败: {e}")
            return ("解析响应失败", 0, 0, "USD")


async def main():
    """示例用法"""
    client = DifyClient()
    response = await client.send_request("abc-123", "你好")
    print("原始响应:", response)

    answer, tokens, price, currency = client.parse_response(response)
    print(f"回答: {answer}")
    print(f"Token数: {tokens}")
    print(f"价格: {price} {currency}")


if __name__ == "__main__":
    asyncio.run(main())

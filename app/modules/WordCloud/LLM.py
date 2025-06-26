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

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, headers=headers, json=data
                ) as response:
                    return await response.text()
        except Exception as e:
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

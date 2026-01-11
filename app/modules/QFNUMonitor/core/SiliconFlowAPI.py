"""
硅基流动大模型 API 客户端
使用 aiohttp 进行异步请求
用于生成公告内容的智能摘要
"""

import os
import aiohttp
from typing import Optional
from logger import logger
from .. import MODULE_NAME


class SiliconFlowAPI:
    """硅基流动大模型 API 客户端"""

    API_URL = "https://api.siliconflow.cn/v1/chat/completions"
    DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
    TIMEOUT = 60

    def __init__(self):
        self.api_key = os.getenv("SILICONFLOW_API_KEY", "")
        if not self.api_key:
            logger.warning(
                f"[{MODULE_NAME}] 未配置 SILICONFLOW_API_KEY 环境变量，摘要功能将不可用"
            )

    def is_available(self) -> bool:
        """检查 API 是否可用"""
        return bool(self.api_key)

    async def generate_summary(
        self,
        content: str,
        max_length: int = 200,
        model: Optional[str] = None,
    ) -> Optional[str]:
        """
        生成内容摘要

        Args:
            content: 需要摘要的内容
            max_length: 摘要最大长度
            model: 使用的模型，默认为 Qwen/Qwen2.5-7B-Instruct

        Returns:
            生成的摘要文本，失败返回 None
        """
        if not self.is_available():
            logger.warning(f"[{MODULE_NAME}] 硅基流动 API 不可用")
            return None

        if not content:
            return None

        # 截取内容，避免过长
        if len(content) > 4000:
            content = content[:4000] + "..."

        model = model or self.DEFAULT_MODEL

        system_prompt = """你是一个专业的通知公告摘要助手。你的任务是将学校的通知公告内容进行简洁的摘要。
要求：
1. 摘要应该简明扼要，突出关键信息
2. 保留重要的时间、地点、事项等关键信息
3. 使用简洁的语言，不要使用过于复杂的句式
4. 摘要长度控制在200字以内
5. 如果是报名通知，务必提取报名时间、考试时间等关键日期
6. 直接输出摘要内容，不要添加"摘要："等前缀"""

        user_prompt = f"请对以下通知公告内容进行摘要：\n\n{content}"

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 512,
            }

            timeout = aiohttp.ClientTimeout(total=self.TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.API_URL, json=payload, headers=headers
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"[{MODULE_NAME}] 硅基流动 API 调用失败，状态码: {response.status}"
                        )
                        text = await response.text()
                        logger.error(f"[{MODULE_NAME}] 响应内容: {text}")
                        return None

                    result = await response.json()
                    summary = (
                        result.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )

                    if summary:
                        # 截取到最大长度
                        if len(summary) > max_length:
                            summary = summary[:max_length] + "..."
                        logger.info(f"[{MODULE_NAME}] 成功生成摘要，长度: {len(summary)}")
                        return summary.strip()

                    return None

        except TimeoutError:
            logger.error(f"[{MODULE_NAME}] 硅基流动 API 调用超时")
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 硅基流动 API 调用异常: {e}")

        return None

    async def summarize_url_content(
        self,
        title: str,
        content: str,
        url: str,
    ) -> Optional[str]:
        """
        针对 URL 内容生成摘要（用于群消息链接摘要）

        Args:
            title: 页面标题
            content: 页面内容
            url: 页面 URL

        Returns:
            生成的摘要文本
        """
        if not self.is_available():
            return None

        if not content:
            return None

        # 截取内容
        if len(content) > 3000:
            content = content[:3000] + "..."

        system_prompt = """你是一个专业的网页内容摘要助手。你的任务是将曲阜师范大学相关网页的内容进行简洁的摘要。
要求：
1. 摘要应该简明扼要，突出关键信息
2. 保留重要的时间、地点、事项等关键信息
3. 使用简洁的语言
4. 摘要长度控制在150字以内
5. 直接输出摘要内容，不要添加任何前缀"""

        user_prompt = f"标题：{title}\n\n内容：{content}"

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.DEFAULT_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 300,
            }

            timeout = aiohttp.ClientTimeout(total=self.TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.API_URL, json=payload, headers=headers
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"[{MODULE_NAME}] 硅基流动 API 调用失败，状态码: {response.status}"
                        )
                        return None

                    result = await response.json()
                    summary = (
                        result.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )

                    if summary:
                        logger.info(
                            f"[{MODULE_NAME}] 成功生成 URL 摘要，长度: {len(summary)}"
                        )
                        return summary.strip()

                    return None

        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 生成 URL 摘要异常: {e}")

        return None


# 测试代码
if __name__ == "__main__":
    import asyncio

    async def test():
        api = SiliconFlowAPI()
        if api.is_available():
            test_content = """
            根据教育部教育考试院统一安排，山东省2026年3月全国计算机等级考试（NCRE）定于3月28日至29日进行。
            报名时间：1月7日9：00至1月13日17：00。
            考试科目包括一级、二级、三级、四级多个科目。
            报名费用：一级、二级、三级每人每科目72元，四级每人每科目112元。
            """
            summary = await api.generate_summary(test_content)
            print(f"摘要: {summary}")
        else:
            print("API 不可用，请配置 SILICONFLOW_API_KEY 环境变量")

    asyncio.run(test())

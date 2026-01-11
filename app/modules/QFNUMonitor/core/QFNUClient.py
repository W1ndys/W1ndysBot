"""
曲阜师范大学教务处公告抓取客户端
使用 aiohttp 进行异步请求
"""

import aiohttp
import ssl
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
from logger import logger
from .. import MODULE_NAME


@dataclass
class Announcement:
    """公告数据类"""

    id: str  # 公告ID，从链接中提取
    title: str  # 公告标题
    url: str  # 公告链接
    date: str  # 发布日期
    summary: str  # 公告摘要


class QFNUClient:
    """曲阜师范大学教务处公告客户端"""

    BASE_URL = "https://jwc.qfnu.edu.cn"
    LIST_URL = f"{BASE_URL}/tz_j_.htm"
    TIMEOUT = 30

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        # 创建不验证 SSL 的上下文
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def _extract_id_from_url(self, url: str) -> str:
        """从URL中提取公告ID"""
        # URL格式: info/1119/7560.htm -> 1119_7560
        try:
            parts = url.replace(".htm", "").split("/")
            if len(parts) >= 2:
                return f"{parts[-2]}_{parts[-1]}"
            return url
        except Exception:
            return url

    async def get_announcements(self, max_count: int = 10) -> list[Announcement]:
        """
        获取公告列表

        Args:
            max_count: 最大获取数量

        Returns:
            公告列表
        """
        announcements = []
        try:
            timeout = aiohttp.ClientTimeout(total=self.TIMEOUT)
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)

            async with aiohttp.ClientSession(
                timeout=timeout, connector=connector
            ) as session:
                async with session.get(
                    self.LIST_URL, headers=self.headers
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"[{MODULE_NAME}] 获取公告列表失败，状态码: {response.status}"
                        )
                        return announcements

                    html = await response.text(encoding="utf-8")
                    soup = BeautifulSoup(html, "html.parser")

                    # 查找所有公告项
                    items = soup.select("ul.n_listxx1 li")

                    for item in items[:max_count]:
                        try:
                            # 提取标题和链接
                            title_elem = item.select_one("h2 a")
                            if not title_elem:
                                continue

                            title = title_elem.get("title", "") or title_elem.get_text(
                                strip=True
                            )
                            href = title_elem.get("href", "")

                            # 构建完整URL
                            if href.startswith("info/"):
                                url = f"{self.BASE_URL}/{href}"
                            elif href.startswith("/"):
                                url = f"{self.BASE_URL}{href}"
                            else:
                                url = href

                            # 提取日期
                            date_elem = item.select_one("span.time")
                            date = date_elem.get_text(strip=True) if date_elem else ""

                            # 提取摘要
                            summary_elem = item.select_one("p")
                            summary = ""
                            if summary_elem:
                                summary = summary_elem.get_text(strip=True)
                                # 移除末尾的 [详细] 链接
                                if summary.endswith("[详细]"):
                                    summary = summary[:-4].strip()

                            # 提取ID
                            announcement_id = self._extract_id_from_url(href)

                            announcement = Announcement(
                                id=announcement_id,
                                title=title,
                                url=url,
                                date=date,
                                summary=summary,
                            )
                            announcements.append(announcement)

                        except Exception as e:
                            logger.warning(f"[{MODULE_NAME}] 解析单条公告失败: {e}")
                            continue

                    logger.info(f"[{MODULE_NAME}] 成功获取 {len(announcements)} 条公告")

        except TimeoutError:
            logger.error(f"[{MODULE_NAME}] 获取公告列表超时")
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 获取公告列表异常: {e}")

        return announcements

    async def get_announcement_content(self, url: str) -> Optional[str]:
        """
        获取公告详情内容

        Args:
            url: 公告详情页URL

        Returns:
            公告内容文本，失败返回None
        """
        try:
            timeout = aiohttp.ClientTimeout(total=self.TIMEOUT)
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)

            async with aiohttp.ClientSession(
                timeout=timeout, connector=connector
            ) as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(
                            f"[{MODULE_NAME}] 获取公告详情失败，状态码: {response.status}"
                        )
                        return None

                    html = await response.text(encoding="utf-8")
                    soup = BeautifulSoup(html, "html.parser")

                    # 提取正文内容
                    content_div = soup.select_one("div#vsb_content")
                    if not content_div:
                        content_div = soup.select_one("div.v_news_content")

                    if content_div:
                        # 移除脚本和样式
                        for script in content_div.find_all(["script", "style"]):
                            script.decompose()

                        # 获取纯文本
                        text = content_div.get_text(separator="\n", strip=True)
                        # 清理多余的空行
                        lines = [
                            line.strip() for line in text.split("\n") if line.strip()
                        ]
                        return "\n".join(lines)

                    return None

        except TimeoutError:
            logger.error(f"[{MODULE_NAME}] 获取公告详情超时: {url}")
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 获取公告详情异常: {e}")

        return None


# 测试代码
if __name__ == "__main__":
    import asyncio

    async def test():
        client = QFNUClient()
        announcements = await client.get_announcements(5)
        for ann in announcements:
            print(f"ID: {ann.id}")
            print(f"标题: {ann.title}")
            print(f"日期: {ann.date}")
            print(f"链接: {ann.url}")
            print(f"摘要: {ann.summary[:100]}...")
            print("-" * 50)

    asyncio.run(test())

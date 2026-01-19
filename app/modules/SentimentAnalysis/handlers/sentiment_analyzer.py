import aiohttp
import asyncio
import os
from datetime import datetime
from logger import logger
from ..config import (
    SIJI_BASE_URL,
    SIJI_API_KEY,
    SIJI_MODEL_NAME,
    NEGATIVE_SENTIMENT_THRESHOLD,
    REQUEST_TIMEOUT
)
from .. import DATA_DIR
from .data_manager import SentimentDataManager


class SentimentAnalyzer:
    """
    情绪分析器，用于调用硅基流动API进行情绪分析
    """
    
    def __init__(self):
        self.base_url = SIJI_BASE_URL
        self.api_key = SIJI_API_KEY
        self.model_name = SIJI_MODEL_NAME
        self.timeout = REQUEST_TIMEOUT
        # 创建日志文件路径
        self.log_file = os.path.join(DATA_DIR, "sentiment_analysis_log.txt")

    def _write_log(self, log_entry):
        """
        将分析结果写入日志文件
        
        Args:
            log_entry (str): 日志条目
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            
            # 写入日志文件，追加模式
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {log_entry}\n")
        except Exception as e:
            logger.error(f"[SentimentAnalysis] 写入日志文件失败: {e}")

    async def analyze_sentiment(self, text, group_id=None, user_id=None, user_name=None):
        """
        分析文本情绪
        
        Args:
            text (str): 待分析的文本
            group_id: 群号，用于获取特定阈值
            user_id: 用户ID，用于日志记录
            user_name: 用户名，用于日志记录
            
        Returns:
            dict: 包含情绪分析结果的字典
                {
                    "is_negative": bool,  # 是否为负面情绪
                    "confidence": float,  # 负面情绪置信度
                    "details": dict       # 详细分析结果
                }
        """
        if not text or not text.strip():
            result = {
                "is_negative": False,
                "confidence": 0.0,
                "details": {}
            }
            # 记录日志
            log_entry = f"群 {group_id} 用户 {user_id}({user_name}): '{text}' - 空消息或无效消息"
            self._write_log(log_entry)
            return result

        try:
            # 构建请求URL (使用聊天补全API而不是预测API)
            url = f"{self.base_url}/chat/completions"
            
            # 构建请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建请求体 (构造一个用于情绪分析的提示)
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system", 
                        "content": "你是一个情绪分析专家。请分析用户消息的情绪倾向，只需回答'positive'（积极）、'negative'（消极）或'neutral'（中性），并给出0-1之间的置信度分数，1表示非常确定。例如：negative,0.85"
                    },
                    {
                        "role": "user", 
                        "content": text
                    }
                ],
                "temperature": 0.1,  # 使用较低的温度以获得更一致的结果
                "max_tokens": 50
            }
            
            # 创建异步HTTP客户端
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # 发送POST请求
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # 获取阈值
                        data_manager = SentimentDataManager(group_id)
                        threshold = data_manager.get_threshold(group_id)
                        
                        # 解析结果
                        sentiment_result = self._parse_sentiment_result(result, threshold)
                        
                        # 记录日志
                        log_entry = f"群 {group_id} 用户 {user_id}({user_name}): '{text}' - 情绪: {'负面' if sentiment_result['is_negative'] else '非负面'}, 置信度: {sentiment_result['confidence']:.2f}"
                        self._write_log(log_entry)
                        
                        return sentiment_result
                    else:
                        error_text = await response.text()
                        logger.error(f"[SentimentAnalysis] API请求失败: {response.status} - {error_text}")
                        
                        # 记录错误日志
                        log_entry = f"群 {group_id} 用户 {user_id}({user_name}): '{text}' - API请求失败: {response.status}"
                        self._write_log(log_entry)
                        
                        return {
                            "is_negative": False,
                            "confidence": 0.0,
                            "details": {"error": f"API请求失败: {response.status}"}
                        }
                        
        except asyncio.TimeoutError:
            logger.error(f"[SentimentAnalysis] API请求超时: {text}")
            
            # 记录超时日志
            log_entry = f"群 {group_id} 用户 {user_id}({user_name}): '{text}' - API请求超时"
            self._write_log(log_entry)
            
            return {
                "is_negative": False,
                "confidence": 0.0,
                "details": {"error": "请求超时"}
            }
        except Exception as e:
            logger.error(f"[SentimentAnalysis] 情绪分析异常: {e}")
            
            # 记录异常日志
            log_entry = f"群 {group_id} 用户 {user_id}({user_name}): '{text}' - 情绪分析异常: {str(e)}"
            self._write_log(log_entry)
            
            return {
                "is_negative": False,
                "confidence": 0.0,
                "details": {"error": str(e)}
            }

    def _parse_sentiment_result(self, api_result, threshold):
        """
        解析API返回的情绪分析结果
        
        Args:
            api_result (dict): API返回的结果
            threshold (float): 判断阈值
            
        Returns:
            dict: 解析后的情绪分析结果
        """
        try:
            # 根据硅基流动聊天补全API的实际返回格式调整解析逻辑
            # 返回格式类似于:
            # {
            #   "choices": [
            #     {
            #       "message": {
            #         "content": "negative,0.85"
            #       }
            #     }
            #   ]
            # }
            
            choices = api_result.get("choices", [])
            if not choices:
                return {
                    "is_negative": False,
                    "confidence": 0.0,
                    "details": api_result
                }
            
            # 获取模型回复内容
            content = choices[0].get("message", {}).get("content", "").strip()
            if not content:
                return {
                    "is_negative": False,
                    "confidence": 0.0,
                    "details": api_result
                }
            
            # 解析回复内容 (格式: "情绪类型,置信度")
            parts = content.split(",")
            if len(parts) != 2:
                return {
                    "is_negative": False,
                    "confidence": 0.0,
                    "details": {"error": "无法解析模型输出", "raw_result": api_result}
                }
            
            sentiment_label = parts[0].strip().lower()
            try:
                confidence = float(parts[1].strip())
            except ValueError:
                return {
                    "is_negative": False,
                    "confidence": 0.0,
                    "details": {"error": "无法解析置信度分数", "raw_result": api_result}
                }
            
            # 判断是否为负面情绪
            is_negative = (sentiment_label == "negative" and confidence >= threshold)
            
            return {
                "is_negative": is_negative,
                "confidence": confidence,
                "details": api_result
            }
                
        except Exception as e:
            logger.error(f"[SentimentAnalysis] 解析情绪分析结果异常: {e}")
            return {
                "is_negative": False,
                "confidence": 0.0,
                "details": {"error": str(e), "raw_result": api_result}
            }
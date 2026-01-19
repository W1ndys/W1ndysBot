# 硅基流动API配置文件
# 用于舆情监控的情绪分析模块

import os
from dotenv import load_dotenv

# 获取模块目录路径
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# 从模块目录加载 .env
load_dotenv(os.path.join(MODULE_DIR, ".env"))

# API基础配置
SIJI_BASE_URL = os.getenv("SIJI_BASE_URL", "https://api.siliconflow.cn/v1")  # 硅基流动API基础URL
SIJI_API_KEY = os.getenv("SIJI_API_KEY", "")  # API密钥，从环境变量加载
SIJI_MODEL_NAME = os.getenv("SIJI_MODEL_NAME", "Qwen/Qwen3-Omni-30B-A3B-Thinking")  # 使用的模型名称

# 情绪判断阈值
NEGATIVE_SENTIMENT_THRESHOLD = float(os.getenv("NEGATIVE_SENTIMENT_THRESHOLD", "0.7"))  # 负面情绪阈值，超过此值认为是负面情绪

# 请求超时设置（秒）
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# 消息处理配置
AUTO_DELETE_NEGATIVE_MSG = os.getenv("AUTO_DELETE_NEGATIVE_MSG", "True").lower() in ("true", "1", "yes")  # 是否自动删除判定为负面的消息
ADMIN_NOTIFICATION = os.getenv("ADMIN_NOTIFICATION", "True").lower() in ("true", "1", "yes")  # 是否通知管理员

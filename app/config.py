# ==================== 配置项 ====================

import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 机器人顶级管理员QQ，必填
OWNER_ID = os.getenv("OWNER_ID")

# 连接到NapCatQQ的WebSocket连接地址，默认使用3001端口
WS_URL = os.getenv("WS_URL")

# 连接到NapCatQQ的机器人Token
TOKEN = os.getenv("TOKEN")

# 飞书机器人URL，选填，掉线时使用
FEISHU_BOT_URL = os.getenv("FEISHU_BOT_URL")

# 飞书机器人Secret，选填，掉线时使用
FEISHU_BOT_SECRET = os.getenv("FEISHU_BOT_SECRET")

# ==================== 配置项结束 ====================

# config.py

import os

owner_id = [2769731875]  # 机器人root管理员 QQ 号

if os.getenv("DOCKER_ENV") == "true":
    ws_url = "ws://host.docker.internal:3001"  # napcatQQ 监听的 WebSocket API 地址
else:
    ws_url = "ws://127.0.0.1:3001"  # 本地环境的 WebSocket API 地址

token = None  # 如果需要认证，请填写认证 token

"""
开关系统配置常量
"""

import os

# 开关命令
SWITCH_COMMAND = "switch"

# 数据根目录
DATA_ROOT_DIR = "data"

# 数据库文件路径
DATABASE_PATH = os.path.join(DATA_ROOT_DIR, "Core", "switches.db")

# 确保数据目录存在
os.makedirs(DATA_ROOT_DIR, exist_ok=True)

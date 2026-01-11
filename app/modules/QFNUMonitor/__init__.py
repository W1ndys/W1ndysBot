"""
QFNUMonitor - 曲阜师范大学通知公告监控模块

功能：
1. 定期检查教务处公告，发现新公告时推送到启用的群聊
2. 识别群消息中的 qfnu.edu.cn 链接，自动生成智能摘要
3. 使用硅基流动大模型 API 生成公告摘要

使用方式：
- 发送开关名称切换模块开关（仅管理员）
- 开启后自动监控公告并推送
- 开启后自动为曲师大链接生成摘要
"""

import os
from dotenv import load_dotenv

load_dotenv(".env")

# 模块名称
MODULE_NAME = "QFNUMonitor"

# 模块开关名称
SWITCH_NAME = "qfnum"

# 模块描述
MODULE_DESCRIPTION = "曲阜师范大学教务处通知公告监控"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块命令定义
# ------------------------------------------------------------

# 开关命令说明
SWITCH_COMMAND_DESC = f"发送 {SWITCH_NAME} 切换模块开关（仅管理员）"

# 命令字典
COMMANDS = {
    SWITCH_NAME: SWITCH_COMMAND_DESC,
}
# ------------------------------------------------------------

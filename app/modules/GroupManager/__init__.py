import os


# 模块名称
MODULE_NAME = "GroupManager"

# 模块描述
MODULE_DESCRIPTION = "群组管理模块"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

GROUP_MUTE_COMMAND = "禁言"  # 禁言命令
GROUP_UNMUTE_COMMAND = "解禁"  # 解禁命令
GROUP_KICK_COMMAND = "踢出"  # 踢出命令
GROUP_ALL_MUTE_COMMAND = "全员禁言"  # 全员禁言命令
GROUP_ALL_UNMUTE_COMMAND = "全员解禁"  # 全员解禁命令
GROUP_RECALL_COMMAND = "撤回"  # 撤回消息命令
# ------------------------------------------------------------

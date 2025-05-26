import os


# 模块名称
MODULE_NAME = "InviteTreeRecord"

# 模块开关名称
SWITCH_NAME = "ITR"

# 模块描述
MODULE_DESCRIPTION = "邀请树记录"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
VIEW_INVITE_RECORD = "查询邀请树"
KICK_INVITE_RECORD = "踢出邀请树"
# ------------------------------------------------------------

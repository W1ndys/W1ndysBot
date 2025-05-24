import os


# 模块名称
MODULE_NAME = "BlackList"

# 模块开关名称
SWITCH_NAME = ""

# 模块描述
MODULE_DESCRIPTION = "黑名单模块"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
BLACKLIST_ADD_COMMAND = "加黑"  # 添加黑名单命令
BLACKLIST_REMOVE_COMMAND = "去黑"  # 移除黑名单命令
BLACKLIST_LIST_COMMAND = "看黑"  # 查看黑名单命令
BLACKLIST_CLEAR_COMMAND = "清黑"  # 清空黑名单命令
# ------------------------------------------------------------

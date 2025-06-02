import os


# 模块名称
MODULE_NAME = "GroupNickNameLock"

# 模块开关名称
SWITCH_NAME = "GNNL"

# 模块描述
MODULE_DESCRIPTION = "群昵称锁定，检测群用户昵称是否符合正则，支持正则表达式，支持对单个用户锁定"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
# COMMANDS1 = "命令1"
# COMMANDS2 = "命令2"
# COMMANDS3 = "命令3"
# ------------------------------------------------------------

# 管理命令常量
CMD_SET_REGEX = "设置正则"
CMD_GET_REGEX = "查询正则"
CMD_DEL_REGEX = "删除正则"
CMD_SET_DEFAULT = "设置默认名"
CMD_GET_DEFAULT = "查询默认名"
CMD_SET_LOCK = "锁定昵称"
CMD_GET_LOCK = "查询锁定"
CMD_DEL_LOCK = "删除锁定"

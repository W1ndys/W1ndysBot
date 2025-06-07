import os


# 模块名称
MODULE_NAME = "GroupNickNameLock"

# 模块开关名称
SWITCH_NAME = "GNNL"

# 模块描述
MODULE_DESCRIPTION = (
    "群昵称锁定，检测群用户昵称是否符合正则，支持正则表达式，支持对单个用户锁定"
)

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 管理命令常量
CMD_SET_REGEX = "设置群昵称正则"
CMD_GET_REGEX = "查询群昵称正则"
CMD_DEL_REGEX = "删除群昵称正则"
CMD_SET_DEFAULT = "设置默认群昵称"
CMD_GET_DEFAULT = "查询默认群昵称"
CMD_SET_LOCK = "设置群昵称锁定"
CMD_GET_LOCK = "查询群昵称锁定"
CMD_DEL_LOCK = "删除群昵称锁定"


MENU_COMMAND = "menu"

COMMANDS = {
    CMD_SET_REGEX: "设置群昵称正则",
    CMD_GET_REGEX: "查询群昵称正则",
    CMD_DEL_REGEX: "删除群昵称正则",
    CMD_SET_DEFAULT: "设置默认群昵称",
    CMD_GET_DEFAULT: "查询默认群昵称",
    CMD_SET_LOCK: "设置群昵称锁定",
    CMD_GET_LOCK: "查询群昵称锁定",
    CMD_DEL_LOCK: "删除群昵称锁定",
}

# 昵称提醒时间间隔（秒）
NICKNAME_REMINDER_INTERVAL_SECONDS = 300

import os


# 模块名称
MODULE_NAME = "QFNUGetFreeClassrooms"

# 模块开关名称
SWITCH_NAME = "qfnugrc"

# 模块描述
MODULE_DESCRIPTION = "曲阜师范大学空教室查询模块，便于同学们寻找无课教室自习"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)

# 教室列表文件的路径
CLASSROOMS_JSON_PATH = os.path.join(DATA_DIR, "classrooms.txt")


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

GET_FREE_CLASS_ROOM_COMMAND = "查空教室"  # 查空教室命令
"""查空教室命令，用于查询空教室，方便同学们寻找无课教室自习"""


SAVE_JW_ACCOUNT_COMMAND = "存储教务账号密码"
"""存储教务账号密码的命令，用于存储教务账号密码，方便后续查询空教室"""


COMMANDS = {
    GET_FREE_CLASS_ROOM_COMMAND: "查空教室命令，用法：查空教室+教室全称（必须与教务系统一致）+节次范围（数字-数字）+向后的天数\n示例：查空教室 格物楼101 1-2 1",
    SAVE_JW_ACCOUNT_COMMAND: "存储教务账号密码命令，仅系统管理员私聊可用（需要是好友关系），用法：存储教务账号密码+教务账号+教务密码\n示例：存储教务账号密码 123456 123456",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

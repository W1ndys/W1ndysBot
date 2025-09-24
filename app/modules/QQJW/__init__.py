import os


# 模块名称
MODULE_NAME = "QQJW"

# 模块开关名称
SWITCH_NAME = "qqjw"

# 模块描述
MODULE_DESCRIPTION = "群管理模块"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
# 管理员命令

START_JW = "教务"

# -----------------------------------------管理员命令--------------
ADD_ENABLE_GROUP = f"{START_JW}启用群"
REMOVE_ENABLE_GROUP = f"{START_JW}禁用群"

# 中转群群号常量（字符串类型）
FORWARD_GROUP_ID = "1053432087"


COMMANDS = {
    ADD_ENABLE_GROUP: f"添加启用群，用法：{ADD_ENABLE_GROUP} 群号",
    REMOVE_ENABLE_GROUP: f"禁用启用群，用法：{REMOVE_ENABLE_GROUP} 群号",
}

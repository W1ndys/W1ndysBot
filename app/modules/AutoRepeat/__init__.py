import os


# 模块名称
MODULE_NAME = "AutoRepeat"

# 模块开关名称
SWITCH_NAME = "ar"

# 模块描述
MODULE_DESCRIPTION = "一个随机复读上一条消息的模块，随机戳一戳上一个说话的人"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
MENU_COMMAND = "menu"  # 菜单命令

COMMANDS = {}
# ------------------------------------------------------------

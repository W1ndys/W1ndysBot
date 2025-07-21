import os


# 模块名称
MODULE_NAME = "GroupWelcome"

# 模块开关名称
SWITCH_NAME = "gw"

# 模块描述
MODULE_DESCRIPTION = "入群欢迎退群提醒模块"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

BASE_COMMAND = "/gw"  # 基础命令
GWSET = f"{BASE_COMMAND}set"  # 设置入群欢迎信息命令

COMMANDS = {
    BASE_COMMAND: f"开启入群欢迎退群提醒，用法：{BASE_COMMAND}",
    GWSET: f"设置入群欢迎信息，用法：{GWSET}+空格+欢迎信息",
}
# ------------------------------------------------------------

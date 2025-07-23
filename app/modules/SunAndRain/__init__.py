import os


# 模块名称
MODULE_NAME = "SunAndRain"

# 模块开关名称
SWITCH_NAME = "sar"

# 模块描述
MODULE_DESCRIPTION = "阳光和雨滴，新生军训特色文字游戏"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

SIGN_IN_COMMAND = "签到"  # 签到命令
GOOD_MORNING_COMMAND1 = "早安"  # 早安命令1
GOOD_MORNING_COMMAND2 = "早"  # 早安命令2


COMMANDS = {
    SIGN_IN_COMMAND: "签到，用法：签到",
    GOOD_MORNING_COMMAND1: "早安，用法：早安",
    GOOD_MORNING_COMMAND2: "早，用法：早",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

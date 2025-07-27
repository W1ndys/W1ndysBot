import os


# 模块名称
MODULE_NAME = "SunAndRain"

# 模块开关名称
SWITCH_NAME = "sar"

# 模块描述
MODULE_DESCRIPTION = "阳光和雨露，新生军训特色文字游戏"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

SELECT_COMMAND = "选择"  # 选择命令，用于选择阳光和雨露
SIGN_IN_COMMAND = "签到"  # 签到命令


COMMANDS = {
    f"{SIGN_IN_COMMAND}": "随机奖励1-5个(阳光/雨露)，用法：签到",
    f"{SELECT_COMMAND}": "选择阳光和雨露，用法：选择+空格+阳光/雨露",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

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
QUERY_COMMAND = "查询"  # 查询命令，查看当前数值


COMMANDS = {
    f"{SELECT_COMMAND}": "选择类型，用法：选择 阳光 / 选择 雨露",
    f"{SIGN_IN_COMMAND}": "每日签到获得奖励，连续签到有额外奖励",
    f"{QUERY_COMMAND}": "查询当前拥有的数值，用法：查询",
    "发言奖励": "每次发言随机获得1-5个数值（需先选择类型）",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

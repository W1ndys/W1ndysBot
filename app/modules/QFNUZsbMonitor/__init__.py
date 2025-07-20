import os


# 模块名称
MODULE_NAME = "QFNUZsbMonitor"

# 模块开关名称
SWITCH_NAME = "qzm"

# 模块描述
MODULE_DESCRIPTION = "曲阜师范大学招生状态监控"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

# 查询招生状态
QUERY_ADMISSION_STATUS_COMMAND = "招生状态"

COMMANDS = {
    QUERY_ADMISSION_STATUS_COMMAND: "招生状态，用法：招生状态+空格+省份",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

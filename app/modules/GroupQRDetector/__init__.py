import os


# 模块名称
MODULE_NAME = "GroupQRDetector"

# 模块开关名称
SWITCH_NAME = "gqd"

# 模块描述
MODULE_DESCRIPTION = "群二维码检测模块，支持检测群内图片或视频中有无二维码并进行处理"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

EXAMPLE_COMMAND = "示例命令"  # 示例命令

COMMANDS = {
    EXAMPLE_COMMAND: "示例命令，用法：示例命令",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

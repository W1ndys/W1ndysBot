import os


# 模块名称
MODULE_NAME = "KeywordsReply"

# 模块开关名称
SWITCH_NAME = "KR"

# 模块描述
MODULE_DESCRIPTION = "关键词回复模块，完全匹配关键词后回复，只回复存储的内容，不添加其他内容，是FAQ系统的补充"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
# COMMANDS1 = "命令1"
# COMMANDS2 = "命令2"
# COMMANDS3 = "命令3"
# ------------------------------------------------------------

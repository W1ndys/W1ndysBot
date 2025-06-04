import os


# 模块名称
MODULE_NAME = "WordCloud"

# 模块开关名称
SWITCH_NAME = "wordcloud"

# 模块描述
MODULE_DESCRIPTION = "词云模块"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
GENERATE_WORD_CLOUD = "生成词云"
"""生成词云的命令"""

MENU_COMMAND = "menu"
"""菜单命令"""

COMMANDS = {
    GENERATE_WORD_CLOUD: "生成词云",
}
# ------------------------------------------------------------

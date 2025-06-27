import os


# 模块名称
MODULE_NAME = "WordCloud"

# 模块开关名称
SWITCH_NAME = "wc"

# 模块描述
MODULE_DESCRIPTION = "词云模块"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)
DIFY_API_KEY_FILE = os.path.join(DATA_DIR, "dify_api_key.txt")

# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
GENERATE_WORD_CLOUD = "生成词云"
"""生成词云的命令"""

SET_DIFY_API_KEY = "设置Dify密钥"
"""设置Dify API密钥的命令"""

SUMMARIZE_CHAT = "总结聊天"
"""总结聊天的命令"""

COMMANDS = {
    GENERATE_WORD_CLOUD: "生成词云",
    SET_DIFY_API_KEY: "设置Dify密钥",
    SUMMARIZE_CHAT: "总结聊天",
}
# ------------------------------------------------------------

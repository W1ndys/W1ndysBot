import os


# 模块名称
MODULE_NAME = "KeywordsReply"

# 模块开关名称
SWITCH_NAME = "kr"

# 模块描述
MODULE_DESCRIPTION = "关键词回复模块，完全匹配，只回复内容，不会回复其他多余文字，是 FAQ 系统的补充，不设置权限，任何人都可以添加关键词回复，但只有管理员可以删除关键词回复"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------


ADD_COMMAND = "添加关键词"  # 添加关键词回复
DELETE_COMMAND = "删除关键词"  # 删除关键词回复
LIST_COMMAND = "查看关键词"  # 查看关键词回复
CLEAR_COMMAND = "清空关键词"  # 清空关键词回复


COMMANDS = {
    ADD_COMMAND: "添加关键词回复，用法：添加关键词 关键词 回复内容",
    DELETE_COMMAND: "删除关键词回复，用法：删除关键词 关键词",
    LIST_COMMAND: "查看关键词回复，用法：查看关键词",
    CLEAR_COMMAND: "清空关键词回复，用法：清空关键词",
}
# ------------------------------------------------------------

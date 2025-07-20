import os


# 模块名称
MODULE_NAME = "GroupMemDup"

# 模块开关名称
SWITCH_NAME = "gmd"

# 模块描述
MODULE_DESCRIPTION = "群成员重复检测模块"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

# 关联群号命令：将若干群号关联为一组，进行成员去重检测
ASSOCIATE_GROUPS_COMMAND = "关联群号"
# 删除群号命令：从某一组中删除若干群号
REMOVE_GROUPS_COMMAND = "删除群号"
# 添加群号命令：向某个组添加若干群号
ADD_GROUPS_COMMAND = "添加群号"

# 群发命令：向某个组群发消息
SEND_MESSAGE_COMMAND = "群发"

COMMANDS = {
    ASSOCIATE_GROUPS_COMMAND: "关联群号，用法：关联群号 组名 群号1 群号2 ...",
    REMOVE_GROUPS_COMMAND: "删除群号，用法：删除群号 组名 群号1 群号2 ...",
    ADD_GROUPS_COMMAND: "添加群号，用法：添加群号 组名 群号1 群号2 ...",
    SEND_MESSAGE_COMMAND: "群发，用法：群发 组名 消息",
}

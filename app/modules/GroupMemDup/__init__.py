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
# 查看群号命令：查看某个组中的群号
VIEW_GROUPS_COMMAND = "查看群号"
# 查看群组命令：查看所有群组
VIEW_GROUPS_LIST_COMMAND = "查看群组"
# 删除群组命令：删除某个群组下的所有群号
DELETE_GROUP_COMMAND = "删除群组"

# 群发命令：向某个组群发消息
SEND_MESSAGE_COMMAND = "群发"

# 白名单管理命令
ADD_WHITELIST_COMMAND = "gmd添加白名单"
REMOVE_WHITELIST_COMMAND = "gmd删除白名单"
VIEW_WHITELIST_COMMAND = "gmd查看白名单"

COMMANDS = {
    ASSOCIATE_GROUPS_COMMAND: "关联群号，用法：关联群号 组名 群号1 群号2 ...",
    REMOVE_GROUPS_COMMAND: "删除群号，用法：删除群号 组名 群号1 群号2 ...",
    ADD_GROUPS_COMMAND: "添加群号，用法：添加群号 组名 群号1 群号2 ...",
    VIEW_GROUPS_COMMAND: "查看群号，用法：查看群号 组名",
    VIEW_GROUPS_LIST_COMMAND: "查看群组，用法：查看群组",
    DELETE_GROUP_COMMAND: "删除群组，用法：删除群组 组名",
    SEND_MESSAGE_COMMAND: "群发，用法：群发 组名 消息",
    ADD_WHITELIST_COMMAND: f"添加白名单，用法：{ADD_WHITELIST_COMMAND} QQ号1 QQ号2 ...",
    REMOVE_WHITELIST_COMMAND: f"删除白名单，用法：{REMOVE_WHITELIST_COMMAND} QQ号1 QQ号2 ...",
    VIEW_WHITELIST_COMMAND: f"查看白名单，用法：{VIEW_WHITELIST_COMMAND}",
    "其他说明": "群发消息时，消息中可以包含settodo，表示设为待办，包含atall，表示@全体成员",
}

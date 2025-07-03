import os


# 模块名称
MODULE_NAME = "BlackList"

# 模块开关名称
SWITCH_NAME = "BL"

# 模块描述
MODULE_DESCRIPTION = "黑名单模块"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
BLACKLIST_ADD_COMMAND = "拉黑"  # 添加黑名单命令
BLACKLIST_REMOVE_COMMAND = "解黑"  # 移除黑名单命令
BLACKLIST_LIST_COMMAND = "看黑"  # 查看黑名单命令
BLACKLIST_CLEAR_COMMAND = "清黑"  # 清空黑名单命令
# 新增全局黑名单命令
GLOBAL_BLACKLIST_ADD_COMMAND = "全局拉黑"  # 添加全局黑名单命令
GLOBAL_BLACKLIST_REMOVE_COMMAND = "全局解黑"  # 移除全局黑名单命令
GLOBAL_BLACKLIST_LIST_COMMAND = "全局看黑"  # 查看全局黑名单命令
GLOBAL_BLACKLIST_CLEAR_COMMAND = "全局清黑"  # 清空全局黑名单命令
# 私聊专用命令（等同于全局命令）
PRIVATE_BLACKLIST_ADD_COMMAND = "拉黑"  # 私聊中的拉黑命令（等同于全局拉黑）
PRIVATE_BLACKLIST_REMOVE_COMMAND = "解黑"  # 私聊中的解黑命令（等同于全局解黑）
PRIVATE_BLACKLIST_LIST_COMMAND = "看黑"  # 私聊中的看黑命令（等同于全局看黑）
PRIVATE_BLACKLIST_CLEAR_COMMAND = "清黑"  # 私聊中的清黑命令（等同于全局清黑）
# ------------------------------------------------------------

# 使用变量构建 COMMANDS，确保键的唯一性同时引用常量
COMMANDS = {
    # 群聊命令（显示实际命令）
    f"群聊-{BLACKLIST_ADD_COMMAND}": f"添加群黑名单，命令：{BLACKLIST_ADD_COMMAND}，支持at和纯QQ号，例如：{BLACKLIST_ADD_COMMAND}[CQ:at,qq=1234567890] 或 {BLACKLIST_ADD_COMMAND} 1234567890，支持多个QQ号",
    f"群聊-{BLACKLIST_REMOVE_COMMAND}": f"移除群黑名单，命令：{BLACKLIST_REMOVE_COMMAND}",
    f"群聊-{BLACKLIST_LIST_COMMAND}": f"查看群黑名单，命令：{BLACKLIST_LIST_COMMAND}",
    f"群聊-{BLACKLIST_CLEAR_COMMAND}": f"清空群黑名单，命令：{BLACKLIST_CLEAR_COMMAND}",
    # 全局命令（显示实际命令）
    GLOBAL_BLACKLIST_ADD_COMMAND: f"添加全局黑名单，命令：{GLOBAL_BLACKLIST_ADD_COMMAND}，支持at和纯QQ号，例如：{GLOBAL_BLACKLIST_ADD_COMMAND}[CQ:at,qq=1234567890] 或 {GLOBAL_BLACKLIST_ADD_COMMAND} 1234567890，支持多个QQ号",
    GLOBAL_BLACKLIST_REMOVE_COMMAND: f"移除全局黑名单，命令：{GLOBAL_BLACKLIST_REMOVE_COMMAND}",
    GLOBAL_BLACKLIST_LIST_COMMAND: f"查看全局黑名单，命令：{GLOBAL_BLACKLIST_LIST_COMMAND}",
    GLOBAL_BLACKLIST_CLEAR_COMMAND: f"清空全局黑名单，命令：{GLOBAL_BLACKLIST_CLEAR_COMMAND}",
    # 私聊命令说明（显示实际命令）
    f"私聊-{PRIVATE_BLACKLIST_ADD_COMMAND}": f"私聊中的拉黑（等同于全局拉黑），命令：{PRIVATE_BLACKLIST_ADD_COMMAND}，支持at和纯QQ号",
    f"私聊-{PRIVATE_BLACKLIST_REMOVE_COMMAND}": f"私聊中的解黑（等同于全局解黑），命令：{PRIVATE_BLACKLIST_REMOVE_COMMAND}",
    f"私聊-{PRIVATE_BLACKLIST_LIST_COMMAND}": f"私聊中的看黑（等同于全局看黑），命令：{PRIVATE_BLACKLIST_LIST_COMMAND}",
    f"私聊-{PRIVATE_BLACKLIST_CLEAR_COMMAND}": f"私聊中的清黑（等同于全局清黑），命令：{PRIVATE_BLACKLIST_CLEAR_COMMAND}",
}

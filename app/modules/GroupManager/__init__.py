import os


# 模块名称
MODULE_NAME = "GroupManager"

# 模块开关名称
SWITCH_NAME = "GM"

# 模块描述
MODULE_DESCRIPTION = (
    "群组管理模块，支持群组禁言、解禁、踢出、全员禁言、全员解禁、撤回消息等操作。"
)

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

GROUP_BAN_COMMAND = "ban"  # 禁言命令
GROUP_UNBAN_COMMAND = "unban"  # 解禁命令
GROUP_KICK_COMMAND = "kick"  # 踢出命令
GROUP_ALL_BAN_COMMAND = "banall"  # 全员禁言命令
GROUP_ALL_UNBAN_COMMAND = "unbanall"  # 全员解禁命令
GROUP_RECALL_COMMAND = "recall"  # 撤回消息命令
GROUP_BAN_ME_COMMAND = "banme"  # 封禁自己命令
GROUP_BAN_RANK_COMMAND = "banrank"  # 禁言排行榜命令
# ------------------------------------------------------------

COMMANDS = {
    GROUP_BAN_COMMAND: "禁言，封禁用户，支持at和QQ号，使用命令：ban+艾特或QQ号+禁言时长，空格隔开，支持批量操作，例如：ban 1234567890 1234567891 1234567892 10",
    GROUP_UNBAN_COMMAND: "解禁，解封用户，支持at和QQ号，使用命令：unban+艾特或QQ号，空格隔开，支持批量操作，例如：unban 1234567890 1234567891 1234567892",
    GROUP_KICK_COMMAND: "踢出，踢出用户，支持at和QQ号，使用命令：kick+艾特或QQ号，空格隔开，支持批量操作，例如：kick 1234567890 1234567891 1234567892",
    GROUP_ALL_BAN_COMMAND: "禁言全体成员",
    GROUP_ALL_UNBAN_COMMAND: "全员解禁",
    GROUP_RECALL_COMMAND: "撤回消息，直接回复需要被撤回的消息该命令即可",
    GROUP_BAN_ME_COMMAND: "封禁自己一段随机时间",
    GROUP_BAN_RANK_COMMAND: "查看禁言排行榜，展示个人和群内禁言记录",
}

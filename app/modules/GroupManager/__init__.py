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
SCAN_INACTIVE_USER_COMMAND = "警告未活跃用户"  # 警告未活跃用户
GROUP_SET_CURFEW_COMMAND = "设置宵禁"  # 设置宵禁命令
GROUP_CANCEL_CURFEW_COMMAND = "取消宵禁"  # 取消宵禁命令
GROUP_TOGGLE_CURFEW_COMMAND = "切换宵禁"  # 切换宵禁开关命令
GROUP_QUERY_CURFEW_COMMAND = "查询宵禁"  # 查询宵禁状态命令
GROUP_TOGGLE_AUTO_APPROVE_COMMAND = "切换同意入群"  # 切换自动同意入群命令


# ------------------------------------------------------------

COMMANDS = {
    GROUP_BAN_COMMAND: "禁言，支持at和QQ号，ban+对象+时长，空格隔开，支持批量，下同。例如：ban 1234567890 1234567891 10",
    GROUP_UNBAN_COMMAND: "解禁，unban+对象，空格隔开，支持批量，下同。例如：unban 1234567890 1234567891",
    GROUP_KICK_COMMAND: "踢出，kick+对象，空格隔开，支持批量，下同。例如：kick 1234567890 1234567891",
    GROUP_ALL_BAN_COMMAND: "禁言全体成员",
    GROUP_ALL_UNBAN_COMMAND: "全员解禁",
    GROUP_RECALL_COMMAND: "撤回消息，回复需要撤回的消息并发送该命令",
    GROUP_BAN_ME_COMMAND: "封禁自己一段随机时间",
    GROUP_BAN_RANK_COMMAND: "查看禁言排行榜，展示个人和群内禁言记录",
    SCAN_INACTIVE_USER_COMMAND: "警告未活跃用户，格式：警告未活跃用户+天数。例如：警告未活跃用户 30",
    GROUP_SET_CURFEW_COMMAND: f"设置宵禁时间，格式：{GROUP_SET_CURFEW_COMMAND} 开始时间 结束时间（24小时制），如 {GROUP_SET_CURFEW_COMMAND} 23:00 06:00，宵禁期间自动禁言全体成员，结束后自动解除。",
    GROUP_CANCEL_CURFEW_COMMAND: "取消当前群的宵禁设置，将删除所有宵禁配置",
    GROUP_TOGGLE_CURFEW_COMMAND: "切换宵禁功能的开启/关闭状态，不删除配置",
    GROUP_QUERY_CURFEW_COMMAND: "查询当前群的宵禁设置和状态",
    GROUP_TOGGLE_AUTO_APPROVE_COMMAND: "切换自动同意入群功能的开启/关闭状态",
}

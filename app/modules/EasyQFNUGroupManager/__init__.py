import os


# 模块名称
MODULE_NAME = "EasyQFNUGroupManager"

# 模块是否启用（默认开启）
MODULE_ENABLED = True

# 模块开关名称
SWITCH_NAME = "eqgm"

# 模块描述
MODULE_DESCRIPTION = "EasyQFNU群管理工具 - 入群验证管理"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# ============ 配置参数 ============

# 验证超时时间（小时）
TIMEOUT_HOURS = 1

# 提醒开始时间（小时）- 入群多长时间后开始发送提醒
REMIND_START_HOURS = 0.5

# 验证命令前缀
VERIFY_COMMAND = "通过"

# 查看待验证列表命令
PENDING_LIST_COMMAND = "待验证"

# 查看无记录成员列表命令
UNRECORDED_LIST_COMMAND = "无记录"

# 踢出通告消息
KICK_NOTICE_MESSAGE = f"由于您在入群后超过{TIMEOUT_HOURS}小时未完成验证，现已被移出群聊。如有需要请重新申请加群。"

# 提醒消息（使用{hours}占位符显示当前已入群小时数）
REMIND_MESSAGE_TEMPLATE = "您已入群超过{hours}小时仍未完成验证，请尽快联系群主进行验证。如超过{timeout}小时未验证将被自动移出群聊。"


# ============ 命令定义 ============

BASE_COMMAND = "通过"  # 主命令

COMMANDS = {
    f"{BASE_COMMAND}+QQ号": "验证指定用户通过，例如：通过123456",
    f"{BASE_COMMAND}+@用户": "验证被艾特的用户通过",
    f"{BASE_COMMAND}+多个QQ号": "批量验证通过，QQ号用空格/换行分隔",
    "待验证": "查看当前群内待验证用户列表",
    "无记录": "查看数据库中无记录但在群内的成员列表",
}

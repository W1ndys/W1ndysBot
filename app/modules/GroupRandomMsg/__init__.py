import os


# 模块名称
MODULE_NAME = "GroupRandomMsg"

# 模块开关名称
SWITCH_NAME = "grm"

# 模块描述
MODULE_DESCRIPTION = "群随机消息，每隔半小时随机从数据库中获取一条消息发送"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)

# 配置参数
SILENCE_MINUTES = 20  # 群静默时间（分钟），只有超过这个时间没有人发言才会发送随机消息

# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

ADD_GROUP_RANDOM_MSG = "添加群随机消息"
DELETE_GROUP_RANDOM_MSG = "删除群随机消息"

COMMANDS = {
    ADD_GROUP_RANDOM_MSG: "添加群随机消息，用法：添加群随机消息+空格+内容，例如：添加群随机消息 你好",
    DELETE_GROUP_RANDOM_MSG: "删除群随机消息，用法：删除群随机消息+空格+ID，例如：删除群随机消息 1",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

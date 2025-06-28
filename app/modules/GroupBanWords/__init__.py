import os


# 模块名称
MODULE_NAME = "GroupBanWords"

# 模块开关名称
SWITCH_NAME = "GBW"

# 模块描述
MODULE_DESCRIPTION = "基于权重的违禁词监控模块，支持自定义违禁词"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
BAN_WORD_WEIGHT_MAX = 100  # 违禁词封顶权重，超过视为违规
BAN_WORD_DURATION = 30 * 24 * 60 * 60  # 违禁词封禁时长，单位：秒

ADD_BAN_WORD_COMMAND = "添加违禁词"  # 添加违禁词命令
DELETE_BAN_WORD_COMMAND = "删除违禁词"  # 删除违禁词命令
ADD_GLOBAL_BAN_WORD_COMMAND = "添加全局违禁词"  # 添加全局违禁词命令
DELETE_GLOBAL_BAN_WORD_COMMAND = "删除全局违禁词"  # 删除全局违禁词命令
UNBAN_WORD_COMMAND = "解封违禁词"  # 解封被封禁用户命令
KICK_BAN_WORD_COMMAND = "踢出违禁词"  # 踢出被封禁用户命令
COPY_BAN_WORD_COMMAND = "复制违禁词"  # 复制违禁词命令

COMMANDS = {
    ADD_BAN_WORD_COMMAND: f"添加违禁词，用法：{ADD_BAN_WORD_COMMAND} 违禁词 权重(0-100，默认10)，例如：{ADD_BAN_WORD_COMMAND} sb 10",
    DELETE_BAN_WORD_COMMAND: f"删除违禁词，用法：{DELETE_BAN_WORD_COMMAND} 违禁词，例如：{DELETE_BAN_WORD_COMMAND} sb",
    ADD_GLOBAL_BAN_WORD_COMMAND: f"添加全局违禁词，用法：{ADD_GLOBAL_BAN_WORD_COMMAND} 违禁词 权重(0-100，默认10)，例如：{ADD_GLOBAL_BAN_WORD_COMMAND} sb 10",
    DELETE_GLOBAL_BAN_WORD_COMMAND: f"删除全局违禁词，用法：{DELETE_GLOBAL_BAN_WORD_COMMAND} 违禁词，例如：{DELETE_GLOBAL_BAN_WORD_COMMAND} sb",
    COPY_BAN_WORD_COMMAND: f"复制违禁词，用法：私聊：{COPY_BAN_WORD_COMMAND} 来源群号 目标群号，群聊：{COPY_BAN_WORD_COMMAND} 来源群号(复制到当前群)，全局词库群号为0",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

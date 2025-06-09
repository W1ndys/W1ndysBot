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

COMMANDS = {
    ADD_BAN_WORD_COMMAND: "添加违禁词，用法：添加违禁词 违禁词 权重(0-100，默认10)，例如：添加违禁词 sb 10，权重越大，违禁词风险越高",
    DELETE_BAN_WORD_COMMAND: "删除违禁词，用法：删除违禁词 违禁词，例如：删除违禁词 sb",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

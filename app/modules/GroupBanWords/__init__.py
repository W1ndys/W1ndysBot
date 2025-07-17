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

ADD_BAN_WORD_COMMAND = "添加违禁词"  # 添加违禁词命令（群聊添加群专属，私聊添加全局）
DELETE_BAN_WORD_COMMAND = "删除违禁词"  # 删除违禁词命令（群聊删除群专属，私聊删除全局）
ADD_GLOBAL_BAN_WORD_COMMAND = (
    "添加全局违禁词"  # 添加全局违禁词命令（已废弃，保留兼容性）
)
DELETE_GLOBAL_BAN_WORD_COMMAND = (
    "删除全局违禁词"  # 删除全局违禁词命令（已废弃，保留兼容性）
)
UNBAN_WORD_COMMAND = "解禁"  # 解禁被封禁用户命令
KICK_BAN_WORD_COMMAND = "踢出"  # 踢出被封禁用户命令
COPY_BAN_WORD_COMMAND = "复制违禁词"  # 复制违禁词命令

# 添加新的命令常量
ADD_BAN_SAMPLE_COMMAND = "添加违禁样本"
DELETE_BAN_SAMPLE_COMMAND = "删除违禁样本"
LIST_BAN_SAMPLES_COMMAND = "查看违禁样本"

# 相似度阈值配置（独立于违禁词权重阈值）
SIMILARITY_THRESHOLD = 80  # 相似度阈值，达到此阈值即判定为违规

COMMANDS = {
    ADD_BAN_WORD_COMMAND: f"添加违禁词，用法：群聊中使用添加群专属违禁词，私聊中使用添加全局违禁词，格式：{ADD_BAN_WORD_COMMAND} 违禁词 权重(0-100，默认10)，例如：{ADD_BAN_WORD_COMMAND} sb 10",
    DELETE_BAN_WORD_COMMAND: f"删除违禁词，用法：群聊中删除群专属违禁词，私聊中删除全局违禁词，格式：{DELETE_BAN_WORD_COMMAND} 违禁词，例如：{DELETE_BAN_WORD_COMMAND} sb",
    ADD_GLOBAL_BAN_WORD_COMMAND: f"[已废弃] 添加全局违禁词，请在私聊中使用'{ADD_BAN_WORD_COMMAND}'命令",
    DELETE_GLOBAL_BAN_WORD_COMMAND: f"[已废弃] 删除全局违禁词，请在私聊中使用'{DELETE_BAN_WORD_COMMAND}'命令",
    COPY_BAN_WORD_COMMAND: f"复制违禁词，用法：私聊：{COPY_BAN_WORD_COMMAND} 来源群号 目标群号，群聊：{COPY_BAN_WORD_COMMAND} 来源群号(复制到当前群)，全局词库群号为0",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

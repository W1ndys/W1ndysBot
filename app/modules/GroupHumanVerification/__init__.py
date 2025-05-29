import os


# 模块名称
MODULE_NAME = "GroupHumanVerification"

# 模块开关名称
SWITCH_NAME = "GHV"

# 模块描述
MODULE_DESCRIPTION = "入群人机验证"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
SCAN_VERIFICATION = "扫描验证"
"""扫描验证命令"""
APPROVE_VERIFICATION = "同意入群验证"
"""同意入群验证命令"""
REJECT_VERIFICATION = "拒绝入群验证"
"""拒绝入群验证命令"""

# 入群验证相关配置
MAX_ATTEMPTS: int = 3  # 最大验证次数
"""用户在进行入群验证时的最大尝试次数，超过此次数将被禁言"""

MAX_WARNINGS: int = 3  # 最大警告次数
"""用户在验证过程中收到的最大警告次数，超过此次数将被禁言"""

BAN_TIME: int = 30 * 24 * 60 * 60  # 入群禁言时间
"""用户验证失败后的禁言时长（以秒为单位），默认为30天"""

# ------------------------------------------------------------

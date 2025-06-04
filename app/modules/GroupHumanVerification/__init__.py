import os


# 模块名称
MODULE_NAME = "GroupHumanVerification"

# 模块开关名称
SWITCH_NAME = "GHV"

# 模块描述
MODULE_DESCRIPTION = "基于验证码的入群验证模块"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
SCAN_VERIFICATION = "扫描入群验证"
"""扫描入群验证命令"""

WARNING_COUNT = 3
"""剩余警告次数"""

BAN_TIME = 30 * 24 * 60 * 60
"""禁言时间"""

# 各种验证状态

STATUS_VERIFIED = "已验证"
"""已验证"""

STATUS_REJECTED = "管理员已拒绝"
"""管理员已拒绝"""

STATUS_UNVERIFIED = "未验证"
"""未验证"""

STATUS_LEFT = "已主动退群"
"""已主动退群"""

STATUS_KICKED = "管理员已踢出"
"""管理员已踢出"""

STATUS_UNMUTED = "管理员已解禁"
"""管理员已解禁"""


# ------------------------------------------------------------

MENU_COMMAND = "menu"

COMMANDS = {
    SCAN_VERIFICATION: "扫描入群验证",
}

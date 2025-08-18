import os


# 模块名称
MODULE_NAME = "SunAndRain"

# 模块开关名称
SWITCH_NAME = "sar"

# 模块描述
MODULE_DESCRIPTION = "阳光和雨露，新生军训特色文字游戏（按年份存储数据）"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# ============== 数值常量配置 ==============

# 签到奖励配置
CHECKIN_BASE_REWARD_MIN = 5  # 签到基础奖励最小值
CHECKIN_BASE_REWARD_MAX = 15  # 签到基础奖励最大值

# 发言奖励配置
SPEECH_REWARD_MIN = 1  # 发言奖励最小值
SPEECH_REWARD_MAX = 5  # 发言奖励最大值
DAILY_SPEECH_REWARD_LIMIT = 50  # 每日发言奖励上限数值

# 邀请奖励配置
INVITE_REWARD = 50  # 邀请入群奖励数值

# 连续签到奖励配置
CONSECUTIVE_BONUS_CONFIG = {
    3: 10,  # 连续3天奖励10个
    7: 50,  # 连续7天奖励50个
    15: 100,  # 连续15天奖励100个
    30: 200,  # 连续30天奖励200个
}

# 里程碑提示配置
MILESTONE_VALUES = [10, 25, 50, 200, 300, 500, 1000]  # 特定里程碑数值
MILESTONE_NOTIFY_INTERVAL = 100  # 每100个数值提示一次


ANNOUNCEMENT_MESSAGE = "\n\n发送‘sarmenu’，查看菜单，游戏bug反馈请联系QQ2769731875"


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

SELECT_COMMAND = "选择"  # 选择命令，用于选择阳光和雨露
SIGN_IN_COMMAND = "签到"  # 签到命令
QUERY_COMMAND = "查询"  # 查询命令，查看当前数值
RANKING_COMMAND = "排行榜"  # 排行榜命令
LOTTERY_COMMAND = "抽"  # 抽奖命令，抽阳光/抽雨露

# 抽奖配置
LOTTERY_COST = 10  # 抽奖花费
LOTTERY_REWARD_MIN = 1  # 抽奖最小奖励
LOTTERY_REWARD_MAX = 20  # 抽奖最大奖励

# 倍率抽奖配置
MULTIPLIER_MAX = 10  # 最大允许倍率
MULTIPLIER_MIN = 1  # 最小倍率（等于不使用倍率）


COMMANDS = {
    f"{SELECT_COMMAND}": "选择类型，用法：选择 阳光 / 选择 雨露",
    f"{SIGN_IN_COMMAND}": "每日签到获得奖励，连续签到有额外奖励",
    f"{QUERY_COMMAND}": "查询当前拥有的数值，用法：查询",
    f"{RANKING_COMMAND}": "查看排行榜，用法：排行榜 / 排行榜 阳光 / 排行榜 雨露",
    f"{LOTTERY_COMMAND}阳光/{LOTTERY_COMMAND}雨露": f"抽奖功能，花费{LOTTERY_COST}个数值，随机获得{LOTTERY_REWARD_MIN}-{LOTTERY_REWARD_MAX}个数值，支持倍率：抽阳光 10（每群每用户每分钟限1次）",
    "发言奖励": f"每次发言随机获得{SPEECH_REWARD_MIN}-{SPEECH_REWARD_MAX}个数值，每日上限{DAILY_SPEECH_REWARD_LIMIT}个（需先选择类型）",
    "邀请奖励": f"邀请好友获得奖励{INVITE_REWARD}个数值",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

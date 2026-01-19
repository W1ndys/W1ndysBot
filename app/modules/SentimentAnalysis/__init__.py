import os

# 模块名称
MODULE_NAME = "SentimentAnalysis"


# 模块是否启用（默认开启）
MODULE_ENABLED = True
# 模块开关名称
SWITCH_NAME = "SA"

# 模块描述
MODULE_DESCRIPTION = "舆情监控模块，使用LTP+BERT模型进行情绪分析"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)

# 模块命令定义
SET_SENTIMENT_THRESHOLD_COMMAND = "设置情绪阈值"

COMMANDS = {
    SET_SENTIMENT_THRESHOLD_COMMAND: "设置负面情绪判断阈值，例如：设置情绪阈值 0.7"
}

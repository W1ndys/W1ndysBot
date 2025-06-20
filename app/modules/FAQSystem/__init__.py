import os


# 模块名称
MODULE_NAME = "FAQSystem"

# 模块开关名称
SWITCH_NAME = "FAQ"

# 模块描述
MODULE_DESCRIPTION = "基于 TF-IDF、编辑距离与倒排索引的中文智能问答系统，支持自定义问答对的存储与高效检索，适用于 FAQ、知识库等场景"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
ADD_FAQ = "添加问答"
DELETE_FAQ = "删除问答"
GET_FAQ = "获取问答"
# ------------------------------------------------------------
HIGH_THRESHOLD = 0.8  # 高阈值：直接回复答案
LOW_THRESHOLD = 0.4  # 低阈值：显示相关问题引导
MAX_SUGGESTIONS = 10  # 最大建议问题数量
RKEY_DIR = os.path.join("data", "Core", "nc_get_rkey.json")  # 获取rkey的文件路径
DELETE_TIME = 300  # 消息撤回延迟时间

COMMANDS = {
    ADD_FAQ: "添加问答，格式: 添加问答 问题 答案，支持引用消息添加，例如，引用回复某条消息+添加问答+问题，会自动提取被引用的消息作为答案，同时支持批量添加，一行一个问答对，例如：\n添加问答\n问题1 答案1\n问题2 答案2\n问题3 答案3",
    DELETE_FAQ: "删除问答，格式: 删除问答 问题ID",
    GET_FAQ: "获取问答，格式: 获取问答 问题ID",
}

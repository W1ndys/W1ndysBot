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
ADD_FAQ = "添加问答对"
DELETE_FAQ = "删除问答对"
# ------------------------------------------------------------

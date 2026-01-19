import os


# 模块名称
MODULE_NAME = "QFNUFreshmanQuestionQuery"


# 模块是否启用（默认开启）
MODULE_ENABLED = True
# 模块开关名称
SWITCH_NAME = "qfnufqq"

# 模块描述
MODULE_DESCRIPTION = "曲阜师范大学新生题库查询模块，自动匹配题目并显示答案"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块命令说明
# ------------------------------------------------------------
COMMANDS = {
    "直接发送题目关键词": "自动匹配题库中的题目，返回选项和正确答案（✅正确 ❌错误）",
}
# ------------------------------------------------------------

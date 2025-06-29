import os


# 模块名称
MODULE_NAME = "SageSayings"

# 模块开关名称
SWITCH_NAME = "ss"

# 模块描述
MODULE_DESCRIPTION = "记录群友的经典语录"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

ADD_SAYING_COMMAND = "入典"  # 入典命令
DELETE_SAYING_COMMAND = "删典"  # 删典命令
GET_SAYING_COMMAND = "爆典"  # 爆典命令

COMMANDS = {
    ADD_SAYING_COMMAND: "入典，用法：入典+名字+图片，用空格分隔，或引用回复要入典的图片回复“入典+名字”",
    DELETE_SAYING_COMMAND: "删典，用法：删典+名字+ID，删除指定名字指定ID的语录",
    GET_SAYING_COMMAND: "爆典，用法：爆典+名字，随机爆出指定名字的语录",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

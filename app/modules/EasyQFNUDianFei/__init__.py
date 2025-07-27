import os


# 模块名称
MODULE_NAME = "EasyQFNUDianFei"

# 模块开关名称
SWITCH_NAME = "eqdf"

# 模块描述
MODULE_DESCRIPTION = "曲阜师范大学新校区电费查询模块"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# 一个主命令，其余子命令都以主命令开头，便于不同模块的命令区分
# ------------------------------------------------------------

BASE_COMMAND = "/eqdf"  # 主命令
# 绑定链接的命令
BIND_COMMAND = f"{BASE_COMMAND}绑定"  # 绑定命令
# 查询电费命令
QUERY_COMMAND = f"{BASE_COMMAND}查询"  # 查询命令

COMMANDS = {
    BIND_COMMAND: f"绑定命令，用法：{BIND_COMMAND}+空格+电费链接，电费链接可以在微信公众号“Qsd学生公寓”查询缴费的页面链接就是，形如 http://wechat.sdkdch.cn/h5/?openId=xxxxxxxxx",
    QUERY_COMMAND: f"查询命令，用法：{QUERY_COMMAND}",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

import os

# 模块名称
MODULE_NAME = "Reporter"

# 模块开关名称
SWITCH_NAME = "rp"

# 模块描述
MODULE_DESCRIPTION = "主要用于把私聊bot、加bot为好友，邀请bot入群等操作的通知报告"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

# 转发消息给owner的标志，用于响应函数提取
FORWARD_MESSAGE_TO_OWNER = "forward_message_to_owner"

AUTO_AGREE_FRIEND_VERIFY = "自动同意好友验证"
TEST_COMMAND = "测试"

COMMANDS = {
    AUTO_AGREE_FRIEND_VERIFY: f"开启自动同意好友验证，用法：{AUTO_AGREE_FRIEND_VERIFY}",
    TEST_COMMAND: f"测试，用法：{TEST_COMMAND}",
}
# ------------------------------------------------------------

import os


MODULE_NAME = "ISCCSubmit"
MODULE_ENABLED = True
SWITCH_NAME = "iscc"
MODULE_DESCRIPTION = (
    "ISCC 平台自动提交 flag 模块，同时支持擂台赛提交监控（按心跳轮询指定 team_id，新提交通知管理员）"
)

DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)

BASE_URL = "https://iscc.isclab.org.cn"

# ---------- 自动提交相关 ----------
CONFIG_COMMAND = "iscc配置"
HELP_COMMAND = "iscc帮助"
SESSION_COMMAND = "isccsession"
NONCE_COMMAND = "isccnonce"
REFRESH_COMMAND = "iscc刷新"
# 不再要求消息以 ISCC{ 开头/结尾，只要消息里包含一段 ISCC{...} 就识别成 flag 提交，
# 提高对客户端转发、引用、上下文带前后缀场景的容错。
# 同时允许在 flag 后面跟一个空白 + 方向（题目分类），用于按方向批量提交，例如
# `ISCC{xxxx} web` 表示该 flag 仅提交到 web 方向的未解题目。方向匹配在客户端
# 侧不区分大小写，并采用子串模糊匹配。
FLAG_PATTERN = r"ISCC\{[^{}]+\}(?:[ \t]+([^\s{}]+))?"

# 每日自动刷新 session 的北京时间（24 小时制）
DAILY_REFRESH_HOUR = 7
DAILY_REFRESH_MINUTE = 50

# ---------- 擂台赛监控相关 ----------
# 所有监控命令统一以 isccm 开头，和模块主开关 iscc 保持同一前缀
MONITOR_ADD_COMMAND = "isccm添加"
MONITOR_REMOVE_COMMAND = "isccm删除"
MONITOR_LIST_COMMAND = "isccm列表"
MONITOR_CHECK_COMMAND = "isccm检测"

COMMANDS = {
    SWITCH_NAME: "系统管理员开关 ISCC 自动提交与擂台赛监控模块",
    CONFIG_COMMAND: "配置 ISCC 账号，用法：iscc配置 <账号> <密码>",
    "ISCC{xxxxx}": "提交 flag 到 ISCC 平台未解题目（消息中可包含多个 ISCC{...}，会并发提交，无需独立成行）",
    "ISCC{xxxxx} <方向>": "在 flag 后跟空格加方向（如 web、misc），仅向匹配方向的未解题目批量提交，方向不区分大小写并支持模糊匹配",
    SESSION_COMMAND: "查询当前 ISCC session",
    NONCE_COMMAND: "查询当前 ISCC 练武题和擂台题 nonce",
    REFRESH_COMMAND: "立即刷新练武题/擂台题未解题目缓存",
    MONITOR_ADD_COMMAND: "添加监控的擂台赛 team id，用法：isccm添加 <team_id> [备注]",
    MONITOR_REMOVE_COMMAND: "删除监控的擂台赛 team id，用法：isccm删除 <team_id>",
    MONITOR_LIST_COMMAND: "查看当前监控的擂台赛 team id 列表",
    MONITOR_CHECK_COMMAND: "立即手动触发一次擂台赛监控轮询",
    HELP_COMMAND: "查看 ISCC 自动提交与擂台赛监控帮助",
}

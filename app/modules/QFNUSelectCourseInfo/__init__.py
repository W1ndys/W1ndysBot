import os


# 模块名称
MODULE_NAME = "QFNUSelectCourseInfo"

# 模块开关名称
SWITCH_NAME = "qfnusci"

# 模块描述
MODULE_DESCRIPTION = (
    "曲阜师范大学预选课信息自助查询，接入教务系统，可查课余量、课程ID、节次、上课地点等"
)

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------

SELECT_COURSE_INFO = "选课查询"  # 查询命令

COMMANDS = {
    SELECT_COURSE_INFO: "查询命令，用法：选课查询 课程名",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------

"""
开关存储
每个模块的开关群记录和数据都存储在data/module_name目录下
开关文件为switch.json，存储结构为：
//群聊开关
{
    "group": {
        "群号1": True,
        "群号2": False
    },
    "private": True
}
"""

import os
import json
import logger
from utils.generate import generate_reply_message, generate_text_message
from api.message import send_private_msg, send_group_msg
from utils.auth import is_system_admin, is_group_admin

SWITCH_COMMAND = "switch"

# 数据根目录
DATA_ROOT_DIR = "data"


# 确保数据目录存在
os.makedirs(DATA_ROOT_DIR, exist_ok=True)


# 是否开启群聊开关
def is_group_switch_on(group_id, MODULE_NAME):
    """
    判断群聊开关是否开启，默认关闭
    group_id: 群号
    MODULE_NAME: 模块名称
    返回值:
    True: 开启
    False: 关闭
    """
    switch = load_switch(MODULE_NAME)
    return switch["group"].get(group_id, False)


# 是否开启私聊开关
def is_private_switch_on(MODULE_NAME):
    """
    判断私聊开关是否开启，默认关闭
    MODULE_NAME: 模块名称
    返回值:
    True: 开启
    False: 关闭
    """
    switch = load_switch(MODULE_NAME)
    return switch.get("private", False)


# 切换群聊开关
def toggle_group_switch(group_id, MODULE_NAME):
    try:
        switch_status = toggle_switch(
            switch_type="group", group_id=group_id, MODULE_NAME=MODULE_NAME
        )
        logger.info(f"[{MODULE_NAME}]群聊开关已切换为【{switch_status}】")
        return switch_status
    except Exception as e:
        logger.error(f"[{MODULE_NAME}]切换群聊开关失败: {e}")
        return False


# 切换私聊开关
def toggle_private_switch(MODULE_NAME):
    try:
        switch_status = toggle_switch(switch_type="private", MODULE_NAME=MODULE_NAME)
        logger.info(f"[{MODULE_NAME}]私聊开关已切换为【{switch_status}】")
        return switch_status
    except Exception as e:
        logger.error(f"[{MODULE_NAME}]切换私聊开关失败: {e}")
        return False


def load_switch(MODULE_NAME):
    """
    加载某模块的开关
    """
    try:
        SWITCH_PATH = os.path.join(DATA_ROOT_DIR, MODULE_NAME, "switch.json")
        os.makedirs(os.path.dirname(SWITCH_PATH), exist_ok=True)
        if os.path.exists(SWITCH_PATH):
            with open(SWITCH_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # 如果文件不存在，则创建一个默认的开关文件
            switch = {"group": {}, "private": False}
            with open(SWITCH_PATH, "w", encoding="utf-8") as f:
                json.dump(switch, f, ensure_ascii=False, indent=4)
            return switch
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"[{MODULE_NAME}]加载开关文件失败: {e}")
        # 如果文件出错或不存在，则创建一个默认的开关文件
        switch = {"group": {}, "private": False}
        with open(SWITCH_PATH, "w", encoding="utf-8") as f:
            json.dump(switch, f, ensure_ascii=False, indent=4)
        return switch


def save_switch(switch, MODULE_NAME):
    """
    保存某模块的开关
    """
    try:
        SWITCH_PATH = os.path.join(DATA_ROOT_DIR, MODULE_NAME, "switch.json")
        os.makedirs(os.path.dirname(SWITCH_PATH), exist_ok=True)
        with open(SWITCH_PATH, "w", encoding="utf-8") as f:
            json.dump(switch, f, ensure_ascii=False, indent=4)
    except IOError as e:
        logger.error(f"[{MODULE_NAME}]保存开关文件失败: {e}")


def toggle_switch(switch_type, MODULE_NAME, group_id="0"):
    """
    切换某模块的开关
    switch_type: 开关类型，group或private
    group_id: 群号，仅当switch_type为group时有效
    MODULE_NAME: 模块名称
    """
    try:
        switch = load_switch(MODULE_NAME)
        if switch_type == "group":
            # 如果没有群号键则直接写入
            if group_id not in switch["group"]:
                switch["group"][group_id] = True
            else:
                switch["group"][group_id] = not switch["group"][group_id]
            result = switch["group"][group_id]
        elif switch_type == "private":
            switch["private"] = not switch["private"]
            result = switch["private"]
        save_switch(switch, MODULE_NAME)
        return result
    except Exception as e:
        logger.error(f"[{MODULE_NAME}]切换开关失败: {e}")
        return False


def load_group_all_switch(group_id):
    """
    获取某群组所有模块的开关
    返回格式为：
    {
        "group_id": {
            "module_name1": True,
            "module_name2": False
        }
    }
    """
    switch = {group_id: {}}
    # 遍历所有数据目录，100次遍历大概消耗0.02秒
    for module_name in os.listdir(DATA_ROOT_DIR):
        try:
            switch_data = load_switch(module_name)
            if group_id in switch_data.get("group", {}):
                switch[group_id][module_name] = switch_data["group"][group_id]
        except Exception as e:
            logger.error(f"加载模块 {module_name} 的开关数据失败: {e}")
    return switch


def get_all_enabled_groups(MODULE_NAME):
    """
    获取某模块所有已开启的群聊列表
    MODULE_NAME: 模块名称
    返回值: 开启的群号列表
    """
    switch = load_switch(MODULE_NAME)
    return [group_id for group_id, status in switch.get("group", {}).items() if status]


async def handle_module_private_switch(MODULE_NAME, websocket, user_id, message_id):
    """
    处理模块私聊开关命令
    """
    try:
        switch_status = toggle_private_switch(MODULE_NAME)
        switch_status = "开启" if switch_status else "关闭"
        reply_message = generate_reply_message(message_id)
        text_message = generate_text_message(
            f"[{MODULE_NAME}]私聊开关已切换为【{switch_status}】"
        )
        await send_private_msg(
            websocket,
            user_id,
            [reply_message, text_message],
            note="del_msg=10",
        )
    except Exception as e:
        logger.error(f"[{MODULE_NAME}]处理模块私聊开关命令失败: {e}")


async def handle_module_group_switch(MODULE_NAME, websocket, group_id, message_id):
    """
    处理模块群聊开关命令
    """
    try:
        switch_status = toggle_group_switch(group_id, MODULE_NAME)
        switch_status = "开启" if switch_status else "关闭"
        reply_message = generate_reply_message(message_id)
        text_message = generate_text_message(
            f"[{MODULE_NAME}]群聊开关已切换为【{switch_status}】"
        )
        await send_group_msg(
            websocket,
            group_id,
            [reply_message, text_message],
            note="del_msg=10",
        )
        return switch_status
    except Exception as e:
        logger.error(f"[{MODULE_NAME}]处理模块群聊开关命令失败: {e}")


async def handle_events(websocket, message):
    """
    统一处理 switch 命令，支持群聊
    用来扫描本群已开启的模块
    """
    try:
        # 只处理文本消息
        if message.get("post_type") != "message":
            return
        raw_message = message.get("raw_message", "").lower()
        if raw_message != SWITCH_COMMAND:
            return

        # 获取基本信息
        user_id = str(message.get("user_id", ""))
        message_type = message.get("message_type", "")
        role = message.get("sender", {}).get("role", "")

        # 鉴权 - 根据消息类型进行不同的权限检查
        if message_type == "group":
            group_id = str(message.get("group_id", ""))
            # 群聊中需要是系统管理员或群管理员
            if not is_system_admin(user_id) and not is_group_admin(role):
                return

        message_id = message.get("message_id", "")
        reply_message = generate_reply_message(message_id)

        if message_type == "group":
            # 扫描本群已开启的模块
            enabled_modules = []
            for module_name in os.listdir(DATA_ROOT_DIR):
                if is_group_switch_on(group_id, module_name):
                    enabled_modules.append(module_name)

            if enabled_modules:
                switch_text = f"本群（{group_id}）已开启的模块：\n"
                for i, module_name in enumerate(enabled_modules, 1):
                    switch_text += f"{i}. 【{module_name}】\n"
                switch_text += f"\n共计 {len(enabled_modules)} 个模块"
            else:
                switch_text = f"本群（{group_id}）暂未开启任何模块"

            text_message = generate_text_message(switch_text)
            await send_group_msg(
                websocket,
                group_id,
                [reply_message, text_message],
                note="del_msg=30",
            )

    except Exception as e:
        logger.error(f"[SwitchManager]处理开关查询命令失败: {e}")

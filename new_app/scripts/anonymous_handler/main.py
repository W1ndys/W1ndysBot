import json
import logging
import random
import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api import send_group_msg, send_private_msg

anon_id_map = []  # 存储匿名ID和真实QQ的映射
welcome_map = []  # 存储已发送欢迎词的用户，格式为列表
admin_list = []  # 存储管理员列表
mute_list = []  # 存储被禁言的匿名ID
group_anon_chat_enabled = {}  # 存储群是否允许匿名聊天的状态
private_anon_chat_enabled = {}  # 存储私聊是否允许匿名聊天的状态


# 加载本地存储的匿名ID映射
async def load_anon_id_map():
    global anon_id_map
    if os.path.exists("data/anon_id_map.json"):
        logging.info("发现data/anon_id_map.json文件，开始加载匿名ID映射")
        with open("data/anon_id_map.json", "r") as f:
            anon_id_map = json.load(f)
            logging.info(f"加载成功，匿名ID映射内容: {anon_id_map}")
            return anon_id_map
    else:
        logging.info("未发现data/anon_id_map.json文件，创建新的匿名ID映射文件")
        with open("data/anon_id_map.json", "w") as f:
            f.write("[]")
        logging.info("创建成功，返回空的匿名ID映射")
        return []


# 加载本地存储的欢迎词映射
async def load_welcome_map():
    global welcome_map
    if os.path.exists("data/welcome_map.json"):
        logging.info("发现data/welcome_map.json文件，开始加载欢迎词映射")
        try:
            with open("data/welcome_map.json", "r") as f:
                welcome_map = json.load(f)
                logging.info(f"加载成功，欢迎词映射内容: {welcome_map}")
        except json.JSONDecodeError:
            logging.error("data/welcome_map.json文件内容无效，初始化为空列表")
            welcome_map = []
        return welcome_map
    else:
        logging.info("未发现data/welcome_map.json文件，创建新的欢迎词映射文件")
        with open("data/welcome_map.json", "w") as f:
            f.write("[]")
        logging.info("创建成功，返回空的欢迎词映射")
        return []


# 加载本地存储的管理员列表
async def load_admin_list():
    global admin_list
    if os.path.exists("data/admin_list.txt"):
        logging.info("发现data/admin_list.txt文件，开始加载管理员列表")
        with open("data/admin_list.txt", "r") as f:
            admin_list = f.read().splitlines()
            logging.info(f"加载成功，管理员列表内容: {admin_list}")
    else:
        logging.info("未发现data/admin_list.txt文件，创建新的管理员列表文件")
        with open("data/admin_list.txt", "w") as f:
            f.write("")
        logging.info("创建成功，返回空的管理员列表")
        admin_list = []


# 加载本地存储的群匿名聊天状态
async def load_group_anon_chat_enabled():
    global group_anon_chat_enabled
    if os.path.exists("data/group_anon_chat_enabled.json"):
        logging.info(
            "发现data/group_anon_chat_enabled.json文件，开始加载群匿名聊天状态"
        )
        with open("data/group_anon_chat_enabled.json", "r") as f:
            group_anon_chat_enabled = json.load(f)
            logging.info(f"加载成功，群匿名聊天状态: {group_anon_chat_enabled}")
    else:
        logging.info(
            "未发现data/group_anon_chat_enabled.json文件，创建新的群匿名聊天状态文件"
        )
        with open("data/group_anon_chat_enabled.json", "w") as f:
            f.write("{}")
        logging.info("创建成功，返回空的群匿名聊天状态")
        group_anon_chat_enabled = {}


# 加载本地存储的私聊匿名聊天状态
async def load_private_anon_chat_enabled():
    global private_anon_chat_enabled
    if os.path.exists("data/private_anon_chat_enabled.json"):
        logging.info(
            "发现data/private_anon_chat_enabled.json文件，开始加载私聊匿名聊天状态"
        )
        with open("data/private_anon_chat_enabled.json", "r") as f:
            private_anon_chat_enabled = json.load(f)
            logging.info(f"加载成功，私聊匿名聊天状态: {private_anon_chat_enabled}")
    else:
        logging.info(
            "未发现data/private_anon_chat_enabled.json文件，创建新的私聊匿名聊天状态文件"
        )
        with open("data/private_anon_chat_enabled.json", "w") as f:
            f.write("{}")
        logging.info("创建成功，返回空的私聊匿名聊天状态")
        private_anon_chat_enabled = {}


# 保存欢迎词映射到本地文件
async def save_welcome_map():
    with open("data/welcome_map.json", "w") as f:
        json.dump(welcome_map, f)
    logging.info(f"保存欢迎词映射: {welcome_map}")


# 保存群匿名聊天状态到本地文件
async def save_group_anon_chat_enabled():
    with open("data/group_anon_chat_enabled.json", "w") as f:
        json.dump(group_anon_chat_enabled, f)
    logging.info(f"保存群匿名聊天状态: {group_anon_chat_enabled}")


# 保存私聊匿名消息状态到本地文件
async def save_private_anon_chat_enabled():
    with open("data/private_anon_chat_enabled.json", "w") as f:
        json.dump(private_anon_chat_enabled, f)
    logging.info(f"保存私聊匿名聊天状态: {private_anon_chat_enabled}")


# 已知QQ号获取匿名ID
async def get_anon_id_by_user_id(user_id, group_id):
    logging.info(f"正在获取{user_id}在群{group_id}的匿名ID映射")
    if os.path.exists("data/anon_id_map.json"):
        with open("data/anon_id_map.json", "r") as f:
            anon_id_map = json.load(f)
        for record in anon_id_map:
            if str(record["user_id"]) == str(user_id) and str(
                record["group_id"]
            ) == str(group_id):
                logging.info(
                    f"找到匿名ID: {record['anon_id']} 对应的用户ID: {user_id} 在群: {group_id}"
                )
                return record["anon_id"]
    logging.info(f"未找到用户ID: {user_id} 在群: {group_id} 的匿名ID映射")
    return None


# 已知匿名ID获取QQ号
async def get_user_id_by_anon_id(anon_id, group_id):
    logging.info(f"正在获取匿名ID: {anon_id} 在群: {group_id} 的用户ID映射")
    if os.path.exists("data/anon_id_map.json"):
        logging.info("data/anon_id_map.json文件存在，开始读取文件内容")
        with open("data/anon_id_map.json", "r") as f:
            anon_id_map = json.load(f)
        logging.debug(f"anon_id_map内容: {anon_id_map}")
        for record in anon_id_map:
            logging.debug(f"检查记录: {record}")
            if str(record["anon_id"]) == str(anon_id) and str(
                record["group_id"]
            ) == str(group_id):
                logging.info(
                    f"找到用户ID: {record['user_id']} 对应的匿名ID: {anon_id} 在群: {group_id}"
                )
                return record["user_id"]
        logging.info(f"未找到匿名ID: {anon_id} 在群: {group_id} 的用户ID映射")
        return None


# 保存匿名ID映射到本地文件
async def save_anon_id_map():
    with open("data/anon_id_map.json", "w") as f:
        json.dump(anon_id_map, f)
    logging.info(f"保存匿名ID映射: {anon_id_map}")


# 随机生成一个本地文件没有的ID，并把ID和真实QQ键值对保存到本地文件
async def generate_unique_anon_id(user_id, group_id):
    while True:
        anon_id = random.randint(1000, 9999)
        logging.info(f"生成的随机匿名ID: {anon_id}")
        if not any(
            record["anon_id"] == str(anon_id) and record["group_id"] == str(group_id)
            for record in anon_id_map
        ):
            logging.info(f"匿名ID {anon_id} 未在现有映射中找到，添加新的映射")
            anon_id_map.append(
                {
                    "user_id": str(user_id),
                    "group_id": str(group_id),
                    "anon_id": str(anon_id),
                }
            )
            await save_anon_id_map()
            logging.info(f"已保存新的匿名ID映射: {anon_id_map[-1]}")
            return str(anon_id)


# 匿名发送给管理员
async def send_anonymous_to_admin(websocket, user_id, content, group_id):
    logging.info(f"用户 {user_id} 发送匿名消息给管理员在群 {group_id}")
    anon_id = await get_anon_id_by_user_id(user_id, group_id)
    if anon_id is None:
        anon_id = await generate_unique_anon_id(user_id, group_id)
    content = f"[群{group_id}]的[匿名{anon_id}] 给管理员的消息：\n{content}"
    if admin_list:
        await send_private_msg(websocket, admin_list[0], content)
        logging.info(f"已发送匿名消息给管理员: {content}")
    else:
        logging.warning("管理员列表为空，无法发送匿名消息")


# 检查并发送欢迎词
async def check_and_send_welcome(websocket, user_id):
    logging.info(f"检查用户 {user_id} 是否已发送欢迎词")
    if str(user_id) in welcome_map or user_id in welcome_map:
        logging.info(f"用户 {user_id} 已发送过欢迎词")
        return False  # 返回 False 表示已发送过欢迎词
    welcome_map.append(str(user_id))
    await save_welcome_map()
    logging.info(f"用户 {user_id} 未发送过欢迎词，已添加到 welcome_map 并保存")
    if os.path.exists("data/welcome_message.txt"):
        logging.info("发现 data/welcome_message.txt 文件，读取欢迎词")
        with open("data/welcome_message.txt", "r") as f:
            welcome_message = f.read().strip()
    else:
        logging.info("未发现 data/welcome_message.txt 文件，使用默认欢迎词")
        welcome_message = "欢迎使用匿名系统！"
    await send_private_msg(websocket, user_id, welcome_message)
    logging.info(f"已发送欢迎词给用户 {user_id}")
    return True  # 返回 True 表示发送了欢迎词


# 检查用户是否为管理员
def is_admin(user_id):
    return str(user_id) in admin_list


# 检查用户是否被禁言
async def is_user_muted(anon_id, group_id):
    if os.path.exists("data/mute_list.json"):
        with open("data/mute_list.json", "r") as f:
            mute_list = json.load(f)
        return any(
            str(mute["anon_id"]) == str(anon_id)
            and str(mute["group_id"]) == str(group_id)
            and mute.get("muted", True)  # 检查是否被禁言
            for mute in mute_list
        )
    return False


# 禁言某匿名ID
async def mute_anon_id(websocket, user_id, anon_id, group_id):
    if not is_admin(user_id):
        logging.error(f"用户 {user_id} 不是管理员，无法执行禁言操作")
        await send_private_msg(websocket, user_id, "你没有权限执行此操作")
        return False
    logging.info(f"管理员 {user_id} 正在匿名禁言ID {anon_id} 在群 {group_id}")
    mute_list.append({"anon_id": anon_id, "group_id": group_id, "muted": True})
    await save_mute_list()  # 保存禁言列表到本地文件
    await send_private_msg(
        websocket, user_id, f"匿名ID {anon_id} 在群 {group_id} 已被禁言"
    )
    # 通知被禁言的用户
    target_user_id = await get_user_id_by_anon_id(anon_id, group_id)
    if target_user_id:
        await send_private_msg(
            websocket, target_user_id, f"你在群 {group_id} 的匿名ID {anon_id} 已被禁言"
        )
    return True


# 解禁某匿名ID
async def unmute_anon_id(websocket, user_id, anon_id, group_id):
    if not is_admin(user_id):
        logging.error(f"用户 {user_id} 不是管理员，无法执行解禁操作")
        await send_private_msg(websocket, user_id, "你没有权限执行此操作")
        return False
    logging.info(f"管理员 {user_id} 正在匿名解禁ID {anon_id} 在群 {group_id}")
    for mute in mute_list:
        if mute["anon_id"] == anon_id and mute["group_id"] == group_id:
            mute["muted"] = False
    await save_mute_list()  # 保存禁言列表到本地文件
    await send_private_msg(
        websocket, user_id, f"匿名ID {anon_id} 在群 {group_id} 已被解禁"
    )
    # 通知被解禁的用户
    target_user_id = await get_user_id_by_anon_id(anon_id, group_id)
    if target_user_id:
        await send_private_msg(
            websocket, target_user_id, f"你在群 {group_id} 的匿名ID {anon_id} 已被解禁"
        )
        # 确认消息已发送
        logging.info(
            f"已通知用户 {target_user_id} 其匿名ID {anon_id} 在群 {group_id} 已被解禁"
        )
    else:
        logging.error(f"未找到匿名ID {anon_id} 在群 {group_id} 对应的用户")
    return True


async def save_mute_list():
    with open("data/mute_list.json", "w") as f:
        json.dump(mute_list, f)
    logging.info(f"保存禁言列表: {mute_list}")


# 匿名发送私聊消息
async def send_private_anonymous_message(websocket, user_id, target_user_id, content):
    logging.info(f"用户 {user_id} 发送匿名消息给用户 {target_user_id}")
    anon_id = await get_anon_id_by_user_id(user_id, "private")
    if anon_id is None:
        anon_id = await generate_unique_anon_id(user_id, "private")
    content = f"收到[匿名{anon_id}]的消息\n{content}"
    await send_private_msg(websocket, target_user_id, content)
    response_message = f"已发送至{target_user_id}，你本日匿名为{anon_id}"
    await send_private_msg(websocket, user_id, response_message)
    logging.info(f"已发送匿名消息给用户 {target_user_id}: {content}")


# 查看对方QQ号
async def get_target_user_id_by_anon_id(websocket, user_id, anon_id):
    logging.info(f"用户 {user_id} 请求查看匿名ID {anon_id} 对应的QQ号")
    target_user_id = await get_user_id_by_anon_id(anon_id, "private")
    if target_user_id:
        await send_private_msg(
            websocket, user_id, f"匿名ID {anon_id} 对应的QQ号为 {target_user_id}"
        )
        logging.info(f"匿名ID {anon_id} 对应的QQ号为 {target_user_id}")
    else:
        await send_private_msg(websocket, user_id, f"未找到匿名ID {anon_id} 对应的QQ号")
        logging.error(f"未找到匿名ID {anon_id} 对应的QQ号")


# 匿名系统处理消息的主函数
async def handle_anonymous_message(websocket, user_id, raw_message):
    await load_anon_id_map()  # 加载匿名ID映射
    await load_welcome_map()  # 加载欢迎词映射
    await load_admin_list()  # 加载管理员列表
    await load_group_anon_chat_enabled()  # 加载群匿名聊天状态
    await load_private_anon_chat_enabled()  # 加载私聊匿名聊天状态
    sent_welcome = await check_and_send_welcome(websocket, user_id)  # 检查并发送欢迎词

    # 如果已发送过欢迎词，继续处理消息
    if not sent_welcome:
        logging.info(f"用户 {user_id} 已发送过欢迎词，继续处理消息")

    # 处理命令
    if raw_message.startswith("-匿名消息到"):
        match = re.match(r"-匿名消息到(\d+)回复(\d+)(.*)", raw_message, re.DOTALL)
        if match:
            logging.info(f"收到回复命令")
            target_group_id = match.group(1)
            target_anon_id = match.group(2)
            content = match.group(3)
            anon_id = await get_anon_id_by_user_id(user_id, target_group_id)

            if anon_id == None:
                anon_id = await generate_unique_anon_id(user_id, target_group_id)

            # 检查用户是否被禁言
            if await is_user_muted(anon_id, target_group_id):
                logging.info(
                    f"用户 {user_id} 的匿名ID {anon_id} 在群 {target_group_id} 已被禁言"
                )
                await send_private_msg(
                    websocket,
                    user_id,
                    f"你在群{target_group_id}已被禁言，无法发送消息",
                )
                return

            if await get_user_id_by_anon_id(target_anon_id, target_group_id) == None:
                logging.error(f"未找到群{target_group_id}内的匿名ID {target_anon_id} ")
                await send_private_msg(
                    websocket,
                    user_id,
                    f"未找到群{target_group_id}内的匿名ID {target_anon_id} ",
                )
                return
            content = f"[匿名{anon_id}] 回复{target_anon_id}：\n{content}"
            response_raw_message = f"已通知到[匿名{target_anon_id}]，且已发布在[群{target_group_id}]，你今日在本群内id为{anon_id}。"
            await send_private_msg(websocket, user_id, response_raw_message)
            await send_group_msg(websocket, target_group_id, content)

            logging.info(
                f"开始查找群 {target_group_id} 内匿名ID {target_anon_id} 对应的用户ID"
            )
            target_user_id = await get_user_id_by_anon_id(
                target_anon_id, target_group_id
            )
            logging.info(f"查找结果: 用户ID {target_user_id}")

            if target_user_id:
                await send_private_msg(
                    websocket,
                    target_user_id,
                    f"你有一条新消息来自[群{target_group_id}]的[匿名{anon_id}]",
                )
            else:
                logging.error(
                    f"未找到群 {target_group_id} 内的匿名ID {target_anon_id} 对应的QQ号"
                )
        elif re.match(r"-匿名消息到(\d+)(.*)", raw_message, re.DOTALL):
            # 匹配一般的匿名消息命令
            match = re.match(r"-匿名消息到(\d+)(.*)", raw_message, re.DOTALL)
            if match:
                logging.info(f"收到发送匿名消息命令")
                target_group_id = match.group(1)
                content = match.group(2)
                anon_id = await get_anon_id_by_user_id(user_id, target_group_id)

                # 检查用户是否被禁言
                if await is_user_muted(anon_id, target_group_id):
                    logging.info(
                        f"用户 {user_id} 的匿名ID {anon_id} 在群 {target_group_id} 已被禁言"
                    )
                    await send_private_msg(
                        websocket,
                        user_id,
                        f"你在群{target_group_id}已被禁言，无法发送消息",
                    )
                    return

                logging.info(f"获取匿名ID映射: {anon_id}")
                if anon_id == None:
                    anon_id = await generate_unique_anon_id(user_id, target_group_id)
                    logging.info(f"获取失败，自动生成匿名ID为{anon_id}")
                content = f"[匿名{anon_id}]：\n{content}"
                response_raw_message = f"已发布至[群{target_group_id}]，你今日在群{target_group_id}内id为{anon_id}。"
                await send_group_msg(websocket, target_group_id, content)
                await send_private_msg(websocket, user_id, response_raw_message)

    elif re.match(r"-查看匿名(\d+)在(\d+)", raw_message):
        logging.info(f"收到查看匿名ID命令")
        match = re.match(r"-查看匿名(\d+)在(\d+)", raw_message)
        if match:
            if not is_admin(user_id):
                logging.error(f"用户 {user_id} 不是管理员，无法执行查看操作")
                await send_private_msg(websocket, user_id, "你没有权限执行此操作")
                return

            target_anon_id = match.group(1)
            target_group_id = match.group(2)
            logging.info(
                f"查找群 {target_group_id} 内匿名ID {target_anon_id} 对应的用户ID"
            )
            target_user_id = await get_user_id_by_anon_id(
                target_anon_id, target_group_id
            )
            if target_user_id:
                await send_private_msg(
                    websocket,
                    user_id,
                    f"群 {target_group_id} 内匿名ID {target_anon_id} 对应的用户ID为 {target_user_id}",
                )
            else:
                logging.error(
                    f"未找到群 {target_group_id} 内的匿名ID {target_anon_id} 对应的用户ID"
                )
                await send_private_msg(
                    websocket,
                    user_id,
                    f"未找到群 {target_group_id} 内的匿名ID {target_anon_id} 对应的用户ID",
                )

    elif re.match(r"-匿名禁言(\d+)在(\d+)", raw_message):
        logging.info(f"收到匿名禁言ID命令")
        match = re.match(r"-匿名禁言(\d+)在(\d+)", raw_message)
        if match:
            target_anon_id = match.group(1)
            target_group_id = match.group(2)
            await mute_anon_id(websocket, user_id, target_anon_id, target_group_id)

    elif re.match(r"-匿名解禁(\d+)在(\d+)", raw_message):
        logging.info(f"收到匿名解禁ID命令")
        match = re.match(r"-匿名解禁(\d+)在(\d+)", raw_message)
        if match:
            target_anon_id = match.group(1)
            target_group_id = match.group(2)
            await unmute_anon_id(websocket, user_id, target_anon_id, target_group_id)

    elif re.match(r"-匿名消息给管理员(.*)在(\d+)", raw_message, re.DOTALL):
        logging.info(f"收到匿名消息给管理员命令")
        match = re.match(r"-匿名消息给管理员(.*)在(\d+)", raw_message, re.DOTALL)
        if match:
            content = match.group(1)
            group_id = match.group(2)
            await send_anonymous_to_admin(websocket, user_id, content, group_id)

    elif re.match(r"-私聊回复(\d+)的(\d+)(.*)", raw_message, re.DOTALL):
        logging.info(f"收到私聊回复匿名消息命令")
        match = re.match(r"-私聊回复(\d+)的(\d+)(.*)", raw_message, re.DOTALL)
        if match:
            target_group_id = match.group(1)
            target_anon_id = match.group(2)
            content = match.group(3)

            # 检查群是否允许匿名聊天
            if not group_anon_chat_enabled.get(target_group_id, False):
                logging.warning(f"群 {target_group_id} 未开启匿名聊天功能")
                await send_private_msg(
                    websocket,
                    user_id,
                    f"群 {target_group_id} 未开启匿名聊天功能。请联系管理员使用命令 '-开启群{target_group_id}匿名聊天' 来开启。",
                )
                return

            anon_id = await get_anon_id_by_user_id(user_id, target_group_id)
            if anon_id is None:
                anon_id = await generate_unique_anon_id(user_id, target_group_id)

            # 检查用户是否被禁言
            if await is_user_muted(anon_id, target_group_id):
                logging.info(
                    f"用户 {user_id} 的匿名ID {anon_id} 在群 {target_group_id} 已被禁言"
                )
                await send_private_msg(
                    websocket, user_id, f"你在群{target_group_id}已被禁言，无法发送消息"
                )
                return

            if await get_user_id_by_anon_id(target_anon_id, target_group_id) is None:
                logging.error(f"未找到群{target_group_id}内的匿名ID {target_anon_id}")
                await send_private_msg(
                    websocket,
                    user_id,
                    f"未找到群{target_group_id}内的匿名ID {target_anon_id}",
                )
                return

            content = f"[匿名{anon_id}] 回复{target_anon_id}：\n{content}"
            response_raw_message = f"已发送至[匿名{target_anon_id}]"
            await send_private_msg(websocket, user_id, response_raw_message)

            target_user_id = await get_user_id_by_anon_id(
                target_anon_id, target_group_id
            )
            if target_user_id:
                await send_private_msg(
                    websocket, target_user_id, f"收到来自[匿名{anon_id}]\n{content}"
                )
            else:
                logging.error(
                    f"未找到群 {target_group_id} 内的匿名ID {target_anon_id} 对应的QQ号"
                )
    elif re.match(r"-开启群(\d+)匿名聊天", raw_message):
        logging.info(f"收到开启群匿名聊天命令")
        match = re.match(r"-开启群(\d+)匿名聊天", raw_message)
        if match:
            if not is_admin(user_id):
                logging.error(f"用户 {user_id} 不是管理员，无法执行开启操作")
                await send_private_msg(websocket, user_id, "你没有权限执行此操作")
                return

            target_group_id = match.group(1)
            group_anon_chat_enabled[target_group_id] = True
            await save_group_anon_chat_enabled()
            await send_private_msg(
                websocket, user_id, f"群 {target_group_id} 的匿名聊天功能已开启"
            )

    elif re.match(r"-关闭群(\d+)匿名聊天", raw_message):
        logging.info(f"收到关闭群匿名聊天命令")
        match = re.match(r"-关闭群(\d+)匿名聊天", raw_message)
        if match:
            if not is_admin(user_id):
                logging.error(f"用户 {user_id} 不是管理员，无法执行关闭操作")
                await send_private_msg(websocket, user_id, "你没有权限执行此操作")
                return

            target_group_id = match.group(1)
            group_anon_chat_enabled[target_group_id] = False
            await save_group_anon_chat_enabled()
            await send_private_msg(
                websocket, user_id, f"群 {target_group_id} 的匿名聊天功能已关闭"
            )

    elif re.match(r"-私聊发送(\d+)(.*)", raw_message):
        logging.info(f"收到私聊发送匿名消息命令")
        match = re.match(r"-私聊发送(\d+)(.*)", raw_message)
        if match:
            target_user_id = match.group(1)
            content = match.group(2)

            # 检查私聊匿名聊天是否开启
            if not private_anon_chat_enabled.get("enabled", False):
                logging.warning("私聊匿名聊天功能未开启")
                await send_private_msg(
                    websocket,
                    user_id,
                    "私聊匿名聊天功能未开启。请联系管理员使用命令 '-开启私聊匿名聊天' 来开启。",
                )
                return

            await send_private_anonymous_message(
                websocket, user_id, target_user_id, content
            )

    elif re.match(r"-查看匿名(\d+)", raw_message):
        logging.info(f"收到查看匿名ID命令")
        match = re.match(r"-查看匿名(\d+)", raw_message)
        if match:
            if not is_admin(user_id):
                logging.error(f"用户 {user_id} 不是管理员，无法执行查看操作")
                await send_private_msg(websocket, user_id, "你没有权限执行此操作")
                return

            anon_id = match.group(1)
            await get_target_user_id_by_anon_id(websocket, user_id, anon_id)

    elif re.match(r"-开启私聊匿名聊天", raw_message):
        logging.info(f"收到开启私聊匿名聊天命令")
        if not is_admin(user_id):
            logging.error(f"用户 {user_id} 不是管理员，无法执行开启操作")
            await send_private_msg(websocket, user_id, "你没有权限执行此操作")
            return

        private_anon_chat_enabled["enabled"] = True
        await save_private_anon_chat_enabled()
        await send_private_msg(websocket, user_id, "私聊匿名聊天功能已开启")

    elif re.match(r"-关闭私聊匿名聊天", raw_message):
        logging.info(f"收到关闭私聊匿名聊天命令")
        if not is_admin(user_id):
            logging.error(f"用户 {user_id} 不是管理员，无法执行关闭操作")
            await send_private_msg(websocket, user_id, "你没有权限执行此操作")
            return

        private_anon_chat_enabled["enabled"] = False
        await save_private_anon_chat_enabled()
        await send_private_msg(websocket, user_id, "私聊匿名聊天功能已关闭")
        await send_private_msg(websocket, user_id, "私聊匿名聊天功能已关闭")
    # elif raw_message == "匿名聊天":
    #     logging.info(f"用户 {user_id} 请求欢迎词内容")
    #     if os.path.exists("data/welcome_message.txt"):
    #         with open("data/welcome_message.txt", "r") as f:
    #             welcome_message = f.read().strip()
    #     else:
    #         welcome_message = "欢迎使用匿名系统！"
    #     await send_private_msg(websocket, user_id, welcome_message)
    #     logging.info(f"已发送欢迎词给用户 {user_id}")
    else:
        logging.info(
            f"匿名系统未匹配到任何命令，请检查命令是否正确，有无遗漏-，多字少字"
        )
        # await send_private_msg(
        #     websocket,
        #     user_id,
        #     "匿名系统未匹配到任何命令，请检查命令是否正确，有无遗漏-，多字少字",
        # )

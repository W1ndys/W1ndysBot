# script/Menu/main.py
# 示例脚本
# 本脚本写好了基本的函数，直接在函数中编写逻辑即可，必要的时候可以修改函数名
# 注意：Menu 是具体功能，请根据实际情况一键替换即可
# 注意：function 是函数名称，请根据实际情况一键替换即可

import logging
import os
import sys
import asyncio

# 添加项目根目录到sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.config import owner_id
from app.api import *
from app.switch import *

# 数据存储路径，实际开发时，请将Menu替换为具体的数据存放路径
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "Menu",
)


# 查看功能开关状态
def load_function_status(group_id):
    return load_switch(
        group_id, "function_status"
    )  # 注意：function_status 是开关名称，请根据实际情况修改


# 保存功能开关状态
def save_function_status(group_id, status):
    save_switch(
        group_id, "function_status", status
    )  # 注意：function_status 是开关名称，请根据实际情况修改


# 菜单
async def menu(websocket, group_id, message_id):
    message = (
        f"[CQ:reply,id={message_id}]"
        + """卷卷bot功能列表

groupswitch——查看群功能开关
groupmanager——群管理命令
blacklist——黑名单系统
banwords——违禁词系统
invitechain——邀请链系统
qasystem——问答系统
lockgroupcard——群名片锁
qfnu——曲阜师范大学定制服务

卷卷+任意内容可以与我对话

join——加入内测群
owner——联系开发者


发送对应的命令即可，例如：groupswitch"""
    )

    await send_group_msg(websocket, group_id, message)


# 群消息处理函数
async def handle_Menu_group_message(websocket, msg):
    try:
        group_id = str(msg.get("group_id"))
        raw_message = msg.get("raw_message")
        message_id = msg.get("message_id")

        if raw_message == "menu":
            await menu(websocket, group_id, message_id)
        elif f"卷卷" == raw_message:
            await send_group_msg(
                websocket,
                group_id,
                f"[CQ:reply,id={message_id}]你好啊，我是卷卷，一个基于NapCatQQ和Onebot11协议，用Python开发的QQ机器人，我可以帮你管理群聊，也有娱乐功能，发送“menu”可以查看所有功能~",
            )

        elif raw_message == "join":
            await send_group_msg(
                websocket,
                group_id,
                f"[CQ:reply,id={message_id}]卷卷bot内测群：728077087\n新功能测试的地方，欢迎参与测试\n有啥好玩的点子可以告诉我哦~\n点击链接加入群聊【卷卷内测群】：https://qm.qq.com/q/AXh6cTjSMM",
            )
            # await send_ArkShareGroupEx_group(websocket, 728077087, group_id)
        elif raw_message == "owner":
            await send_group_msg(
                websocket,
                group_id,
                f"[CQ:reply,id={message_id}]呐~这是我的开发者：\nQQ：2769731875\nhttps://qm.qq.com/q/dJjlDIFJfM",
            )
            # await send_ArkSharePeer_group(websocket, 2769731875, group_id)

    except Exception as e:
        logging.error(f"处理Menu群消息失败: {e}")
        return

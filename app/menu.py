# script/Menu/main.py

import logging


from app.config import owner_id
from app.api import *
from app.switch import *

# 数据存储路径，实际开发时，请将Menu替换为具体的数据存放路径
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "Menu",
)

VERSION = "1.1.7"


# 群消息处理函数
async def handle_Menu_group_message(websocket, msg):
    try:
        group_id = str(msg.get("group_id"))
        raw_message = msg.get("raw_message")
        message_id = msg.get("message_id")

        if raw_message == "卷卷":
            await send_group_msg(
                websocket,
                group_id,
                f"[CQ:reply,id={message_id}]你好啊，我是卷卷，"
                + "一个基于NapCatQQ和Onebot11协议，用Python开发的QQ机器人，我可以帮你管理群聊，还有其他功能~\n"
                + "开源地址：https://github.com/W1ndysBot/W1ndysBot\n"
                + "卷卷使用手册：https://blog.w1ndys.top/posts/fbd9a8fd.html\n"
                + f"版本：{VERSION}",
            )

        elif raw_message == "join":
            await send_group_msg(
                websocket,
                group_id,
                f"[CQ:reply,id={message_id}]卷卷bot内测群：728077087\n"
                + "新功能测试的地方，欢迎参与测试\n"
                + "有啥好玩的点子可以告诉我哦~\n"
                + "点击链接加入群聊【卷卷内测群】：https://qm.qq.com/q/AXh6cTjSMM",
            )
            # await send_ArkShareGroupEx_group(websocket, 728077087, group_id)
        elif raw_message == "owner":
            await send_group_msg(
                websocket,
                group_id,
                f"[CQ:reply,id={message_id}]呐~这是我的开发者：\n"
                + "QQ：2769731875\n"
                + "https://qm.qq.com/q/dJjlDIFJfM",
            )
            # await send_ArkSharePeer_group(websocket, 2769731875, group_id)

    except Exception as e:
        logging.error(f"处理Menu群消息失败: {e}")
        return

def generate_at_message(user_id):
    """
    生成@消息

    Args:
        user_id (int): 要@的用户QQ号，如果为"all"则表示@全体成员

    Returns:
        dict: 包含@消息段的字典，格式为:
        {"type": "at", "data": {"qq": user_id}}

    Note:
        - 在群聊中@全体成员需要管理员权限
        - 私聊中不支持@功能
    """
    return {"type": "at", "data": {"qq": user_id}}


def generate_reply_message(message_id):
    """
    生成回复消息

    Args:
        message_id (int): 要回复的消息ID

    Returns:
        dict: 包含回复消息段的字典，格式为:
        {"type": "reply", "data": {"id": message_id}}

    Note:
        - 回复消息会显示被回复消息的内容
        - 支持回复群聊和私聊消息
    """
    return {"type": "reply", "data": {"id": message_id}}


def generate_text_message(text):
    """
    生成文本消息

    Args:
        text (str): 要发送的文本内容

    Returns:
        dict: 包含文本消息段的字典，格式为:
        {"type": "text", "data": {"text": text}}

    Note:
        - 支持发送纯文本消息
        - 可以与其他消息类型组合发送
    """
    return {"type": "text", "data": {"text": text}}


def generate_face_message(face_id):
    """
    生成QQ表情消息

    Args:
        face_id (int): QQ表情ID，范围1-221

    Returns:
        dict: 包含表情消息段的字典，格式为:
        {"type": "face", "data": {"id": face_id}}

    Note:
        - 支持发送系统默认表情
        - 表情ID对应关系可参考QQ表情对照表
    """
    return {"type": "face", "data": {"id": face_id}}


def generate_image_message(file, type="base64", cache=True, proxy=True, timeout=None):
    """
    生成图片消息

    参数:
        file (str): 图片文件路径、URL或Base64编码
        type (str): 图片类型，可选值:
            - file: 本地文件路径（如 D:/a.jpg）
            - url: 网络图片URL（如 http://xxx/xxx.png）
            - base64: Base64编码的图片数据（如 xxxxxxxx）
        cache (bool): 是否使用已缓存的文件
        proxy (bool): 是否通过代理下载文件
        timeout (int): 下载文件的超时时间(秒)

    返回:
        dict: 包含图片消息段的字典，格式为:
        {
            "type": "image",
            "data": {
                "file": "file://D:/a.jpg" 或 "http://xxx/xxx.png" 或 "base64://xxxxxx",
                "cache": cache,
                "proxy": proxy,
                "timeout": timeout
            }
        }

    说明:
        - 支持发送本地图片、网络图片和Base64编码的图片
        - 本地图片需加前缀 file://，Base64需加前缀 base64://
        - 图片大小限制为10MB
        - 建议使用cache=True提高发送效率
    """
    # 自动处理file前缀
    if type == "file":
        if not file.startswith("file://"):
            file = f"file://{file}"
    elif type == "base64":
        if not file.startswith("base64://"):
            file = f"base64://{file}"
    # 网络图片直接使用URL，无需前缀
    # 组装data字典
    data = {
        "file": file,
        "cache": cache,
        "proxy": proxy,
        "timeout": timeout,
    }
    return {
        "type": "image",
        "data": data,
    }


def generate_record_message(file, magic=False, cache=True, proxy=True, timeout=None):
    """
    生成语音消息

    Args:
        file (str): 语音文件路径、URL或Base64编码
        magic (bool): 是否使用变声效果
        cache (bool): 是否使用已缓存的文件
        proxy (bool): 是否通过代理下载文件
        timeout (int): 下载文件的超时时间(秒)

    Returns:
        dict: 包含语音消息段的字典，格式为:
        {
            "type": "record",
            "data": {
                "file": file,
                "magic": magic,
                "cache": cache,
                "proxy": proxy,
                "timeout": timeout
            }
        }

    Note:
        - 支持发送本地语音、网络语音和Base64编码的语音
        - 语音格式支持silk、amr、mp3等
        - 语音时长限制为60秒
    """
    return {
        "type": "record",
        "data": {
            "file": file,
            "magic": magic,
            "cache": cache,
            "proxy": proxy,
            "timeout": timeout,
        },
    }


def generate_video_message(file, cache=True, proxy=True, timeout=None):
    """
    生成视频消息

    Args:
        file (str): 视频文件路径或URL
        cache (bool): 是否使用已缓存的文件
        proxy (bool): 是否通过代理下载文件
        timeout (int): 下载文件的超时时间(秒)

    Returns:
        dict: 包含视频消息段的字典，格式为:
        {
            "type": "video",
            "data": {
                "file": file,
                "cache": cache,
                "proxy": proxy,
                "timeout": timeout
            }
        }

    Note:
        - 支持发送本地视频和网络视频
        - 视频大小限制为100MB
        - 建议使用cache=True提高发送效率
    """
    return {
        "type": "video",
        "data": {"file": file, "cache": cache, "proxy": proxy, "timeout": timeout},
    }


def generate_rps_message():
    """
    生成猜拳消息

    Returns:
        dict: 包含猜拳消息段的字典，格式为:
        {"type": "rps", "data": {}}

    Note:
        - 发送后会随机生成剪刀、石头、布中的一个
        - 仅支持在群聊中使用
    """
    return {"type": "rps", "data": {}}


def generate_dice_message():
    """
    生成骰子消息

    Returns:
        dict: 包含骰子消息段的字典，格式为:
        {"type": "dice", "data": {}}

    Note:
        - 发送后会随机生成1-6中的一个数字
        - 仅支持在群聊中使用
    """
    return {"type": "dice", "data": {}}


def generate_poke_message(user_id):
    """
    生成戳一戳消息

    Args:
        user_id (int): 要戳的用户QQ号

    Returns:
        dict: 包含戳一戳消息段的字典，格式为:
        {"type": "poke", "data": {"qq": user_id}}

    Note:
        - 支持在群聊和私聊中使用
        - 每天对同一用户有次数限制
    """
    return {"type": "poke", "data": {"qq": user_id}}


def generate_share_message(url, title, content="", image=""):
    """
    生成链接分享消息

    Args:
        url (str): 分享的链接
        title (str): 分享的标题
        content (str, optional): 分享的简介
        image (str, optional): 分享的图片URL

    Returns:
        dict: 包含链接分享消息段的字典，格式为:
        {
            "type": "share",
            "data": {
                "url": url,
                "title": title,
                "content": content,
                "image": image
            }
        }

    Note:
        - 支持分享网页链接
        - 会自动抓取网页的标题和缩略图
        - 可以自定义标题、简介和图片
    """
    return {
        "type": "share",
        "data": {"url": url, "title": title, "content": content, "image": image},
    }


def generate_node_message(user_id, nickname, content):
    """
    生成合并转发消息

    Args:
        user_id (int): 用户ID
        nickname (str): 昵称
        content (list): 内容

    Returns:
        dict: 包含合并转发消息段的字典，格式为:
        {
            "type": "node",
            "data": {
                "user_id": user_id,
                "nickname": nickname,
                "content": content
            }
        }

    Note:
        - 支持发送合并转发消息
        - 可以自定义用户ID、昵称和内容
    """
    return {
        "type": "node",
        "data": {"user_id": user_id, "nickname": nickname, "content": content},
    }


def generate_file_message(file_bytes, name):
    """
    生成文件消息（传入文件二进制，自动转为base64编码）

    Args:
        file_bytes (bytes): 文件的二进制内容
        name (str): 文件名，用于显示的文件名称

    Returns:
        dict: 包含文件消息段的字典，格式为:
        {
            "type": "file",
            "data": {
                "file": "base64://xxxxxx",  # 自动转为base64编码
                "name": name
            }
        }

    Note:
        - 只需传入文件的二进制内容，函数会自动转为base64格式
        - 文件大小限制请参考服务端配置
        - name参数用于设置接收方看到的文件名
    """
    import base64

    b64_data = base64.b64encode(file_bytes).decode("utf-8")
    return {"type": "file", "data": {"file": f"base64://{b64_data}", "name": name}}

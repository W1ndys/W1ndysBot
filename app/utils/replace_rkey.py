import re
import json
import os
from logger import logger

RKEY_DIR = os.path.join("data", "Core", "nc_get_rkey.json")


# 如果字符串中有图片（包含rkey），则替换为本地缓存的rkey
def replace_rkey(match):
    cq_img = match.group(0)
    # 查找rkey参数
    rkey_pattern = r"rkey=([^,^\]]+)"
    rkey_search = re.search(rkey_pattern, cq_img)
    if rkey_search:
        # 读取本地rkey
        try:
            with open(RKEY_DIR, "r", encoding="utf-8") as f:
                rkey_json = json.load(f)
            new_rkey = rkey_json.get("rkey")
            if new_rkey:
                # 替换rkey参数
                new_cq_img = re.sub(rkey_pattern, f"rkey={new_rkey}", cq_img)
                return new_cq_img
        except Exception as e:
            logger.error(f"本地rkey替换失败: {e}")
    return cq_img

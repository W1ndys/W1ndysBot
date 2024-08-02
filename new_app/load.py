# load.py
# 用于加载配置文件

import logging
import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.anonymous_handler.main import (
    load_anon_id_map,
    load_admin_list,
    load_welcome_map,
)

# 初始化日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    try:
        await load_welcome_map()
    except Exception as e:
        pass

    try:
        await load_admin_list()
    except Exception as e:
        pass

    try:
        await load_anon_id_map()
    except Exception as e:
        pass


if __name__ == "__main__":
    asyncio.run(main())

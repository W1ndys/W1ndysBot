import asyncio
import logging
import sys
from pathlib import Path

# 配置功能模块的路径
feature_paths = {
    "test": "scripts/test.py",
    "forbidden_word_detector": "scripts/forbidden_word_detector/forbidden_word_detector.py",
}


# 动态添加功能模块路径并导入模块
def dynamic_import(feature_name, feature_path):
    feature_dir = Path(feature_path).parent
    sys.path.append(str(feature_dir))
    module_name = Path(feature_path).stem
    module = __import__(module_name)
    return module.run


# 启用的功能列表
enabled_features = [
    "test",
    "forbidden_word_detector",
]  # 如果不想启用某个功能，只需移除对应的名称

logging.basicConfig(level=logging.INFO)


async def main():
    tasks = []

    for feature in enabled_features:
        if feature in feature_paths:
            run_function = dynamic_import(feature, feature_paths[feature])
            tasks.append(run_function())
        else:
            logging.warning(f"功能 {feature} 不存在，已跳过。")

    if tasks:
        await asyncio.gather(*tasks)
    else:
        logging.info("没有启用的功能，退出。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("已关机...")

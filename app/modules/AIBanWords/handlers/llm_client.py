import json
import os
import aiohttp
from logger import logger
from .. import MODULE_NAME

# 配置
SILICON_FLOW_API_KEY = os.getenv("SILICON_FLOW_API_KEY")
BASE_URL = "https://api.siliconflow.cn/v1/chat/completions"


async def check_message(text, model="Qwen/Qwen2.5-72B-Instruct"):
    """
    检测消息是否违规
    :param text: 待检测的文本
    :param model: 使用的模型
    :return: 字典 {'is_risky': bool, 'reason': str, 'type': str}
    """
    if not SILICON_FLOW_API_KEY:
        # 尝试从硬编码的备用Key获取（仅作为示例，实际应确保环境变量存在）
        # 或者记录错误并返回安全
        logger.error(f"[{MODULE_NAME}] 未配置 SILICON_FLOW_API_KEY 环境变量")
        return {
            "is_risky": False,
            "type": "ERROR",
            "reason": "未配置API Key",
            "confidence": 0,
        }

    # 系统提示词
    system_prompt = """
    你是一个严厉但公正的“大学新生迎新群”的管理员。你的任务是检测用户发送的消息是否包含违规内容。
    
    请主要关注以下几类违规（Risk Types）：
    1. **AD_MARKETING**: 商业广告、推销课、办卡、考证机构推广。
    2. **TRAFFIC_DIVERSION**: 恶意引流。例如“加我QQ/微信看资料”、“进这个群领资料”、“兼职刷单”。
       * 注意：如果新生只是单纯礼貌地询问学长联系方式以便咨询学校问题，通常判定为安全。
    3. **NSFW**: 色情、低俗、暴力、赌博链接或暗示。

    判定规则：
    - 如果是正常的新生提问（关于宿舍、食堂、专业、选课），必须判定为安全（False）。
    - 带有“兼职”、“刷单”、“内部资料（非官方）”、“破解版”等关键词通常是高风险。
    - 任何涉及金钱交易的引导均为高风险。

    请仅以 JSON 格式返回结果，不要包含 markdown 格式或其他废话，格式如下：
    {
        "is_risky": true/false,  // 是否违规
        "type": "类型",          // 违规类型(AD_MARKETING, TRAFFIC_DIVERSION, NSFW, SPAM, NORMAL)
        "reason": "简短的中文理由", // 为什么判定为违规，或者为什么判定为正常
        "confidence": 0.95       // 置信度 0-1
    }
    """

    headers = {
        "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"待检测消息：{text}"},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(BASE_URL, headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"[{MODULE_NAME}] API调用失败: {response.status} - {error_text}"
                    )
                    return {
                        "is_risky": False,
                        "type": "ERROR",
                        "reason": f"API调用失败: {response.status}",
                        "confidence": 0,
                    }

                result = await response.json()
                content = result["choices"][0]["message"]["content"]

                if isinstance(content, str):
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        logger.error(f"[{MODULE_NAME}] JSON解析失败: {content}")
                        return {
                            "is_risky": False,
                            "type": "ERROR",
                            "reason": "解析响应失败",
                            "confidence": 0,
                        }
                return content

    except Exception as e:
        logger.error(f"[{MODULE_NAME}] API调用出错: {e}")
        return {
            "is_risky": False,
            "type": "ERROR",
            "reason": "检测服务异常",
            "confidence": 0,
        }

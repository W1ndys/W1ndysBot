# wzryxmg（王者荣耀小马糕）模块开发文档

## 一、功能概述

本模块用于自动收集和管理群聊中的王者荣耀小马糕消息，支持高价小马糕查询和过期自动清理功能。

## 二、核心功能需求

### 2.1 小马糕消息收集
- **触发条件**：开关开启 + 群聊消息匹配特定格式
- **消息格式**：`王者荣耀【xxxxxxxxxx】我的小马糕今天xxx块，复制链接来我的市集出售，马年上分大吉！`
- **示例**：`王者荣耀【东方不败1JGNNX】我的小马糕今天711块，复制链接来我的市集出售，马年上分大吉！`
- **存储规则**：
  - 相同的小马糕消息（完整消息内容）不重复存储
  - 记录存储时间戳和日期
  - 当天数据当天有效，次日自动失效

### 2.2 高价小马糕查询
- **触发条件**：用户发送包含"高价小马糕"的消息
- **响应逻辑**：
  - 从数据库查询当天该群组价格最高的小马糕
  - 发送该条消息到群内
  - 追加提示语：`\n\n若该小马糕无额度，可回复本条消息"删除"来删除该条数据`

### 2.3 小马糕删除
- **触发条件**：用户引用机器人发送的高价小马糕消息，回复"删除"
- **处理逻辑**：
  - 检测到"删除"消息后，提取被引用的消息ID
  - 调用 `get_msg` API 获取被引用消息的完整内容
  - 从消息内容中解析出小马糕代码
  - 根据小马糕代码从数据库中删除对应记录
  - 回复删除成功提示

## 三、技术实现方案

### 3.1 数据库设计

```sql
-- 表名：xmg_records
CREATE TABLE xmg_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id TEXT NOT NULL,           -- 群号
    user_id TEXT NOT NULL,            -- 发送者QQ号
    nickname TEXT,                    -- 发送者昵称
    full_message TEXT NOT NULL,       -- 完整的小马糕消息
    price INTEGER NOT NULL,           -- 小马糕价格
    store_date TEXT NOT NULL,         -- 存储日期(YYYY-MM-DD)，用于过期清理
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    UNIQUE(group_id, full_message, store_date)  -- 相同消息每天只保留一条
);
```

### 3.2 正则匹配规则

```python
import re

# 匹配小马糕消息格式
XMG_PATTERN = re.compile(
    r'王者荣耀【(.+?)】我的小马糕今天(\d+)块，复制链接来我的市集出售，马年上分大吉！'
)
```

### 3.3 Echo标记机制（关键）

由于WebSocket通信无法一对一获取API响应，需使用echo标记+临时变量实现消息关联。

本模块使用echo机制主要服务于**删除功能**：当用户回复"删除"时，需要调用 `get_msg` API 获取被引用消息的内容，然后通过echo识别响应。

**Echo格式规范**：`变量=值`，多个变量使用下划线 `_` 分割

```python
# 临时存储结构（模块级变量）
# 用于存储待处理的get_msg请求（主要是删除功能）
pending_get_msg = {}

# 删除场景：用户回复"删除"时
# 1. 提取被引用的消息ID (reply_msg_id)
# 2. 构造echo字符串
import uuid
import time

key = uuid.uuid4().hex[:8]
# echo格式: key={uuid}_gid={group_id}_uid={user_id}_mid={message_id}
echo_str = f"key={key}_gid={group_id}_uid={user_id}_mid={reply_msg_id}"

# 存储到pending，记录是谁在什么时候请求了什么消息
pending_get_msg[echo_str] = {
    "group_id": group_id,
    "user_id": user_id,
    "message_id": reply_msg_id,  # 被引用的消息ID
    "delete_msg_id": current_msg_id,  # 用户发送的"删除"消息ID，用于回复
    "timestamp": time.time()
}

# 调用API获取被引用消息的内容
from api.message import get_msg
await get_msg(
    websocket,
    reply_msg_id,
    note=f"wzryxmg_get_{echo_str}"
)
```

### 3.4 Response处理器逻辑

在`handle_response.py`中处理 `get_msg` 的响应，用于删除功能：

```python
async def handle(self):
    """处理响应"""
    echo = self.msg.get("echo", "")
    
    # 判断是否为获取消息详情的响应（删除功能）
    if "wzryxmg_get_" in echo:
        await self._handle_get_msg_response()

async def _handle_get_msg_response(self):
    """处理get_msg响应，用于删除小马糕记录"""
    # 提取echo_str部分
    parts = self.echo.split("wzryxmg_get_")
    if len(parts) < 2:
        return
    
    echo_str = parts[1]
    
    if echo_str not in pending_get_msg:
        logger.warning(f"[{MODULE_NAME}]未找到pending记录: {echo_str}")
        return
    
    # 获取原始请求信息
    request_info = pending_get_msg[echo_str]
    group_id = request_info["group_id"]
    user_id = request_info["user_id"]
    delete_msg_id = request_info["delete_msg_id"]
    
    # 获取消息内容
    data = self.msg.get("data", {})
    message_data = data.get("message", {})
    raw_message = message_data.get("raw_message", "")
    
    # 从消息内容中解析小马糕
    xmg_info = self._parse_xmg_message(raw_message)
    
    if not xmg_info:
        await send_group_msg(
            self.websocket,
            group_id,
            [
                generate_reply_message(delete_msg_id),
                generate_text_message("无法识别该消息中的小马糕信息"),
            ]
        )
        del pending_get_msg[echo_str]
        return
    
    # 根据小马糕代码删除记录
    with DataManager() as dm:
        deleted = dm.delete_by_xmg_code(group_id, xmg_info["code"])
        
        if deleted:
            await send_group_msg(
                self.websocket,
                group_id,
                [
                    generate_reply_message(delete_msg_id),
                    generate_text_message(f"已删除小马糕【{xmg_info['code']}】的记录"),
                ]
            )
        else:
            await send_group_msg(
                self.websocket,
                group_id,
                [
                    generate_reply_message(delete_msg_id),
                    generate_text_message("该小马糕记录已不存在或已被删除"),
                ]
            )
    
    # 清理pending记录
    del pending_get_msg[echo_str]

def _parse_xmg_message(self, raw_message: str) -> Optional[dict]:
    """
    从小马糕消息中解析出代码和价格
    
    Returns:
        {"code": "小马糕代码", "price": 711} 或 None
    """
    match = XMG_PATTERN.search(raw_message)
    if match:
        return {
            "code": match.group(1),
            "price": int(match.group(2))
        }
    return None
```

**解析辅助函数**：

```python
def parse_echo(echo_str: str) -> dict:
    """
    解析echo字符串，提取变量
    
    Args:
        echo_str: 如 "key=abc123_gid=123456_uid=789012_mid=12345"
    
    Returns:
        dict: {"key": "abc123", "gid": "123456", "uid": "789012", "mid": "12345"}
    """
    result = {}
    parts = echo_str.split("_")
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            result[key] = value
    return result
```

## 四、文件结构与代码规划

### 4.1 文件结构

```
app/modules/wzryxmg/
├── __init__.py              # 模块配置（MODULE_NAME, SWITCH_NAME等）
├── main.py                  # 事件分发入口
├── DESIGN.md                # 本设计文档
└── handlers/
    ├── data_manager.py      # 数据库管理类
    ├── handle_message.py    # 消息事件分发器
    ├── handle_message_group.py   # 群消息处理器（核心逻辑）
    ├── handle_message_private.py # 私消息处理器（暂无功能）
    ├── handle_response.py   # 响应处理器（捕获发送成功的消息ID）
    ├── handle_notice.py     # 通知事件分发器
    ├── handle_notice_group.py    # 群通知处理器（暂无功能）
    ├── handle_notice_friend.py   # 好友通知处理器（暂无功能）
    ├── handle_meta_event.py      # 元事件处理器（暂无功能）
    └── handle_request.py    # 请求事件处理器（暂无功能）
```

### 4.2 核心代码实现规划

#### __init__.py
```python
import os

MODULE_NAME = "wzryxmg"
SWITCH_NAME = "小马糕"
MODULE_ENABLED = True
MODULE_DESCRIPTION = "王者荣耀小马糕收集与高价查询"
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)

# 命令定义
BASE_COMMAND = "小马糕"
COMMANDS = {
    BASE_COMMAND: "显示当前群内最高价格的小马糕",
    f"{BASE_COMMAND}帮助": "显示本模块帮助信息",
}

# 全局临时存储（用于echo机制）
# pending_get_msg: 等待get_msg响应的临时存储
# 用于删除功能：存储用户发起的删除请求信息，等待get_msg返回被引用消息内容
# 格式: {echo_str: {"group_id": "", "user_id": "", "message_id": "", "timestamp": 0}}
# echo_str 格式: "key={uuid}_gid={group_id}_uid={user_id}_mid={message_id}"
pending_get_msg = {}
```

#### data_manager.py
```python
class DataManager:
    TABLES = {
        "xmg_records": {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "group_id": "TEXT NOT NULL",
            "user_id": "TEXT NOT NULL",
            "nickname": "TEXT",
            "full_message": "TEXT NOT NULL",
            "price": "INTEGER NOT NULL",
            "store_date": "TEXT NOT NULL",  # YYYY-MM-DD格式
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        }
    }
    
    TABLE_CONSTRAINTS = {
        "xmg_records": [
            "UNIQUE(group_id, full_message, store_date)"  # 相同消息每天只保留一条
        ]
    }
    
    # 方法规划
    def add_xmg(self, group_id, user_id, nickname, full_message, price) -> bool:
        """添加小马糕记录，相同消息不重复存储（通过数据库UNIQUE约束实现）"""
        store_date = datetime.now().strftime("%Y-%m-%d")
        # INSERT 实现，重复会抛异常或返回False
    
    def get_highest_price_xmg(self, group_id) -> Optional[Dict]:
        """获取当天该群组价格最高的小马糕"""
        store_date = datetime.now().strftime("%Y-%m-%d")
        # SELECT * FROM xmg_records WHERE group_id=? AND store_date=? ORDER BY price DESC LIMIT 1
    
    def delete_by_xmg_code(self, group_id: str, xmg_code: str) -> bool:
        """
        根据小马糕代码删除记录（同一天内）
        
        Args:
            group_id: 群号
            xmg_code: 小马糕代码，如"东方不败1JGNNX"
        
        Returns:
            bool: 是否成功删除
        """
        store_date = datetime.now().strftime("%Y-%m-%d")
        # 从full_message中匹配包含该代码的记录
        # DELETE FROM xmg_records WHERE group_id=? AND store_date=? AND full_message LIKE '%【{xmg_code}】%'
    
    def delete_expired_records(self) -> int:
        """删除过期的记录（非当天的），返回删除数量"""
        today = datetime.now().strftime("%Y-%m-%d")
        # DELETE FROM xmg_records WHERE store_date != ?
    
    def get_record_by_id(self, record_id) -> Optional[Dict]:
        """根据ID获取记录详情"""
```

#### handle_message_group.py
```python
import re
from datetime import datetime
from .. import MODULE_NAME, SWITCH_NAME, pending_xmg_messages
from ..handlers.data_manager import DataManager
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_reply_message

# 正则表达式
XMG_PATTERN = re.compile(
    r'王者荣耀【(.+?)】我的小马糕今天(\d+)块，复制链接来我的市集出售，马年上分大吉！'
)

class GroupMessageHandler:
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.group_id = str(msg.get("group_id", ""))
        self.user_id = str(msg.get("user_id", ""))
        self.message_id = str(msg.get("message_id", ""))
        self.raw_message = msg.get("raw_message", "")
        self.sender = msg.get("sender", {})
        self.nickname = self.sender.get("nickname", "")
    
    async def handle(self):
        # 1. 处理开关命令
        if await self._handle_switch_command():
            return
        
        # 2. 检查开关状态
        if not is_group_switch_on(self.group_id, MODULE_NAME):
            return
        
        # 3. 检查是否为引用回复删除
        if await self._handle_delete_reply():
            return
        
        # 4. 检查是否为高价查询
        if await self._handle_high_price_query():
            return
        
        # 5. 检查是否为小马糕消息
        await self._handle_xmg_message()
    
    async def _handle_delete_reply(self) -> bool:
        """
        处理引用回复删除逻辑
        返回True表示已处理
        """
        # 检查消息是否为"删除"
        if self.raw_message.strip() != "删除":
            return False
        
        # 检查是否有引用消息
        message = self.msg.get("message", [])
        reply_msg_id = None
        for segment in message:
            if segment.get("type") == "reply":
                reply_msg_id = str(segment.get("data", {}).get("id", ""))
                break
        
        if not reply_msg_id:
            return False
        
        # 使用echo机制调用get_msg获取被引用消息的内容
        import uuid
        import time
        from api.message import get_msg
        from .. import pending_get_msg
        
        key = uuid.uuid4().hex[:8]
        # echo格式: key={uuid}_gid={group_id}_uid={user_id}_mid={reply_msg_id}
        echo_str = f"key={key}_gid={self.group_id}_uid={self.user_id}_mid={reply_msg_id}"
        
        # 存储到pending，记录删除请求信息
        pending_get_msg[echo_str] = {
            "group_id": self.group_id,
            "user_id": self.user_id,
            "message_id": reply_msg_id,  # 被引用的消息ID
            "delete_msg_id": self.message_id,  # "删除"消息ID，用于回复
            "timestamp": time.time()
        }
        
        # 调用get_msg获取被引用消息的内容
        await get_msg(
            self.websocket,
            reply_msg_id,
            note=f"wzryxmg_get_{echo_str}"
        )
        
        return True
    
    async def _handle_high_price_query(self) -> bool:
        """
        处理高价小马糕查询
        返回True表示已处理
        """
        if "高价小马糕" not in self.raw_message:
            return False
        
        # 先清理过期数据
        with DataManager() as dm:
            dm.delete_expired_records()
            
            # 查询当天最高价
            record = dm.get_highest_price_xmg(self.group_id)
            
            if not record:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("今天还没有人分享小马糕哦~"),
                    ]
                )
                return True
            
            # 构造消息
            message_content = record["full_message"]
            hint = "\n\n若该小马糕无额度，可回复本条消息删除该条数据"
            
            # 直接发送高价小马糕消息，无需echo机制
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(message_content + hint),
                ]
            )
        return True
    
    async def _handle_xmg_message(self):
        """
        处理小马糕消息收集
        """
        match = XMG_PATTERN.match(self.raw_message)
        if not match:
            return
        
        # 提取信息
        xmg_code = match.group(1)  # 小马糕代码，如"东方不败1JGNNX"
        price = int(match.group(2))  # 价格，如711
        
        # 存储到数据库
        with DataManager() as dm:
            success = dm.add_or_update_xmg(
                group_id=self.group_id,
                user_id=self.user_id,
                nickname=self.nickname,
                full_message=self.raw_message,
                price=price
            )
            
            if success:
                logger.info(f"[{MODULE_NAME}]已存储{self.nickname}的小马糕，价格：{price}")
```

#### handle_response.py
```python
import re
from .. import MODULE_NAME, pending_get_msg
from logger import logger
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_reply_message
from .data_manager import DataManager

# 小马糕消息正则（用于解析get_msg返回的内容）
XMG_PATTERN = re.compile(
    r'王者荣耀【(.+?)】我的小马糕今天(\d+)块，复制链接来我的市集出售，马年上分大吉！'
)

class ResponseHandler:
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", "")
    
    async def handle(self):
        try:
            # 检查是否为get_msg响应（删除功能）
            if "wzryxmg_get_" in self.echo:
                await self._handle_get_msg_response()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")
    
    async def _handle_get_msg_response(self):
        """处理get_msg响应，用于删除小马糕记录"""
        # 提取echo_str部分（格式: key=xxx_gid=xxx_uid=xxx_mid=xxx）
        parts = self.echo.split("wzryxmg_get_")
        if len(parts) < 2:
            return
        
        echo_str = parts[1]
        
        if echo_str not in pending_get_msg:
            logger.warning(f"[{MODULE_NAME}]未找到pending记录: {echo_str}")
            return
        
        # 获取原始请求信息
        request_info = pending_get_msg[echo_str]
        group_id = request_info["group_id"]
        delete_msg_id = request_info["delete_msg_id"]
        
        # 获取消息内容（get_msg返回的数据结构）
        # data 中包含 message 字段
        message_data = self.data.get("message", [])
        
        # 提取文本内容（消息段数组中找type=text的）
        raw_message = ""
        for segment in message_data:
            if segment.get("type") == "text":
                raw_message = segment.get("data", {}).get("text", "")
                break
        
        # 从消息内容中解析小马糕
        xmg_info = self._parse_xmg_message(raw_message)
        
        if not xmg_info:
            await send_group_msg(
                self.websocket,
                group_id,
                [
                    generate_reply_message(delete_msg_id),
                    generate_text_message("无法识别该消息中的小马糕信息，可能不是小马糕消息"),
                ]
            )
            del pending_get_msg[echo_str]
            return
        
        # 根据小马糕代码删除记录
        with DataManager() as dm:
            deleted = dm.delete_by_xmg_code(group_id, xmg_info["code"])
            
            if deleted:
                await send_group_msg(
                    self.websocket,
                    group_id,
                    [
                        generate_reply_message(delete_msg_id),
                        generate_text_message(f"已删除小马糕【{xmg_info['code']}】（{xmg_info['price']}块）的记录"),
                    ]
                )
                logger.info(f"[{MODULE_NAME}]已删除小马糕记录，代码：{xmg_info['code']}，价格：{xmg_info['price']}")
            else:
                await send_group_msg(
                    self.websocket,
                    group_id,
                    [
                        generate_reply_message(delete_msg_id),
                        generate_text_message("该小马糕记录已不存在或已被删除"),
                    ]
                )
        
        # 清理pending记录
        del pending_get_msg[echo_str]
    
    def _parse_xmg_message(self, raw_message: str):
        """从小马糕消息中解析出代码和价格"""
        match = XMG_PATTERN.search(raw_message)
        if match:
            return {
                "code": match.group(1),
                "price": int(match.group(2))
            }
        return None
```

## 五、关键逻辑流程图

### 5.1 小马糕消息收集流程

```
群消息到达
    │
    ▼
开关是否开启? ──否──> 忽略
    │是
    ▼
匹配小马糕格式? ──否──> 检查其他命令
    │是
    ▼
提取价格、昵称、完整消息
    │
    ▼
存入数据库（INSERT OR REPLACE）
    │
    ▼
记录日志
```

### 5.2 高价查询流程

```
群消息包含"高价小马糕"
    │
    ▼
开关是否开启? ──否──> 忽略
    │是
    ▼
清理过期记录
    │
    ▼
查询当天最高价记录 ──无──> 回复"今天还没有人分享"
    │有
    ▼
生成echo_key
    │
    ▼
存入pending_xmg_messages
    │
    ▼
发送群消息（携带echo标记）
    │
    ▼
等待响应...
```

### 5.3 get_msg响应处理流程（删除功能）

```
收到响应(status="ok")
    │
    ▼
echo包含"wzryxmg_get_"? ──否──> 忽略
    │是
    ▼
提取echo_str（key=xxx_gid=xxx_uid=xxx_mid=xxx）
    │
    ▼
从pending_get_msg中获取请求信息
    │
    ▼
从响应data.message中提取raw_message
    │
    ▼
解析小马糕代码和价格
    │
    ▼
调用dm.delete_by_xmg_code删除记录
    │
    ▼
回复用户删除结果
    │
    ▼
清理pending记录
```

### 5.4 删除流程

```
群消息为"删除"
    │
    ▼
检查是否有引用消息段(reply) ──无──> 正常消息处理
    │有
    ▼
获取被引用的message_id
    │
    ▼
生成echo_str（key=xxx_gid=xxx_uid=xxx_mid=xxx）
    │
    ▼
存入pending_get_msg
    │
    ▼
调用get_msg API获取被引用消息内容
    │
    ▼
等待响应...
    │
    ▼
【收到响应后】
    │
    ▼
解析消息内容中的小马糕代码
    │
    ▼
调用dm.delete_by_xmg_code删除记录
    │
    ▼
回复用户删除结果
    │
    ▼
清理pending_get_msg
```

## 六、异常处理与边界情况

### 6.1 异常情况

| 异常场景 | 处理方式 |
|---------|---------|
| 数据库操作失败 | 记录error日志，不阻断程序 |
| 正则匹配失败 | 返回None，交由后续处理器处理 |
| echo_key未找到 | 记录warning日志，忽略该响应 |
| 响应中无message_id | 记录warning日志，无法建立映射 |
| 删除时记录已不存在 | 回复"该小马糕记录已不存在或已被删除" |
| 跨群组引用删除 | 验证group_id，不匹配则忽略 |

### 6.2 内存管理

```python
# pending_xmg_messages的过期清理
# 在handle_response中，如果echo_key不存在，可能是已过期
# 可以设置一个最大保留时间（如5分钟）

import time

def clean_pending_messages():
    """清理过期的pending消息（超过5分钟）"""
    now = time.time()
    expired_echo_strs = [
        k for k, v in pending_get_msg.items() 
        if now - v["timestamp"] > 300  # 5分钟
    ]
    for echo_str in expired_echo_strs:
        del pending_get_msg[echo_str]
```

### 6.3 sent_xmg_messages的清理

```python
# sent_xmg_messages也需要定期清理，避免内存无限增长
# 可以在每日0点清理前一天的记录

def clean_sent_messages():
    """清理超过24小时的已发送记录"""
    now = time.time()
    expired_ids = [
        k for k, v in sent_xmg_messages.items()
        if now - v["timestamp"] > 86400  # 24小时
    ]
    for k in expired_ids:
        del sent_xmg_messages[k]
```

## 七、配置项

无需额外配置项，使用项目的开关系统即可。

## 八、日志规范

```python
# 收集小马糕
logger.info(f"[{MODULE_NAME}]已存储{nickname}的小马糕，价格：{price}，群组：{group_id}")

# 高价查询
logger.info(f"[{MODULE_NAME}]用户{user_id}查询高价小马糕，返回价格：{price}")

# 删除操作
logger.info(f"[{MODULE_NAME}]用户{user_id}删除了小马糕记录，价格：{price}，record_id: {record_id}")

# 错误日志
logger.error(f"[{MODULE_NAME}]数据库操作失败: {e}")
logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")
```

## 九、测试要点

1. **正则匹配测试**：验证各种格式的小马糕消息都能正确匹配
2. **数据库操作测试**：验证增删改查功能正常
3. **开关测试**：验证开关开启/关闭时功能是否正常
4. **Echo机制测试**：验证发送高价小马糕后能正确捕获message_id
5. **删除功能测试**：验证引用删除功能正常
6. **过期清理测试**：验证次日数据自动失效
7. **并发测试**：验证多个群组同时使用时的稳定性

## 十、后续扩展建议

1. 支持查看历史平均价格
2. 支持价格排行榜（Top 5）
3. 支持按价格区间筛选
4. 支持私聊查询（需要开启私聊开关）

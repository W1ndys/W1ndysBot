class NoticeHandler:
    """
    舆情监控通知事件处理器
    """
    
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg

    async def handle(self):
        """
        处理通知事件
        """
        # 舆情监控模块暂无特殊通知事件处理需求
        pass
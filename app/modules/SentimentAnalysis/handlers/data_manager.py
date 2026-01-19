import json
import os
from .. import DATA_DIR


class SentimentDataManager:
    """
    舆情监控数据管理器
    """

    CONFIG_FILE = "config.json"

    def __init__(self, group_id):
        self.group_id = str(group_id)
        self.config_path = os.path.join(DATA_DIR, self.CONFIG_FILE)
        self.config = self._load_config()

    def _load_config(self):
        """
        加载配置文件
        """
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # 默认配置
            return {
                "global": {
                    "enabled": True,
                    "threshold": 0.7
                },
                "groups": {}
            }

    def _save_config(self):
        """
        保存配置文件
        """
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def is_enabled(self, group_id=None):
        """
        检查舆情监控是否启用
        
        Args:
            group_id: 群号，如果为None则检查全局设置
            
        Returns:
            bool: 是否启用
        """
        if group_id is None:
            return self.config["global"]["enabled"]
        
        group_id = str(group_id)
        # 先检查群特定设置，再检查全局设置
        if group_id in self.config["groups"]:
            return self.config["groups"][group_id].get("enabled", self.config["global"]["enabled"])
        return self.config["global"]["enabled"]

    def set_enabled(self, enabled, group_id=None):
        """
        设置舆情监控启用状态
        
        Args:
            enabled (bool): 是否启用
            group_id: 群号，如果为None则设置全局设置
        """
        if group_id is None:
            self.config["global"]["enabled"] = enabled
        else:
            group_id = str(group_id)
            if group_id not in self.config["groups"]:
                self.config["groups"][group_id] = {}
            self.config["groups"][group_id]["enabled"] = enabled
        
        self._save_config()

    def get_threshold(self, group_id=None):
        """
        获取情绪判断阈值
        
        Args:
            group_id: 群号，如果为None则获取全局设置
            
        Returns:
            float: 情绪判断阈值
        """
        if group_id is None:
            return self.config["global"]["threshold"]
        
        group_id = str(group_id)
        # 先检查群特定设置，再检查全局设置
        if group_id in self.config["groups"]:
            return self.config["groups"][group_id].get("threshold", self.config["global"]["threshold"])
        return self.config["global"]["threshold"]

    def set_threshold(self, threshold, group_id=None):
        """
        设置情绪判断阈值
        
        Args:
            threshold (float): 情绪判断阈值
            group_id: 群号，如果为None则设置全局设置
        """
        if group_id is None:
            self.config["global"]["threshold"] = threshold
        else:
            group_id = str(group_id)
            if group_id not in self.config["groups"]:
                self.config["groups"][group_id] = {}
            self.config["groups"][group_id]["threshold"] = threshold
        
        self._save_config()
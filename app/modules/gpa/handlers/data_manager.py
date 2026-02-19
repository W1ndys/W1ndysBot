"""
GPA 数据库管理模块

功能特性：
1. 查询班级绩点统计信息（均值、标准差等）
2. 基于正态分布估算百分位排名
3. 支持模糊匹配班级名称

使用示例：
    with DataManager() as dm:
        result = dm.calculate_gpa_percentile("22网安", "2024-2025-1", 3.91)
"""

import sqlite3
import os
import math
from typing import Optional, List, Dict, Any


class DataManager:
    """
    GPA 数据库管理类

    支持上下文管理器协议，自动处理连接的创建和关闭。
    """

    def __init__(self):
        """初始化数据库连接"""
        # 数据库文件路径在模块目录下
        self.db_path = os.path.join(os.path.dirname(__file__), "..", "gpa_ranking.db")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def __enter__(self):
        """进入上下文时返回自身"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文：关闭连接"""
        self.conn.close()
        return False

    def find_class_by_fuzzy_name(self, fuzzy_name: str) -> List[str]:
        """
        根据模糊名称查找班级

        Args:
            fuzzy_name: 模糊班级名称，如 "22网安"

        Returns:
            匹配到的完整班级名称列表，如果没有匹配则返回空列表
        """
        # 构建多种可能的匹配模式
        patterns = [
            f"%{fuzzy_name}%",  # 直接包含
            f"%{fuzzy_name.replace('级', '')}%",  # 去掉级字
            f"%20{fuzzy_name}%",  # 年份前缀
        ]

        # 如果输入包含数字开头，尝试提取年级和专业
        if fuzzy_name and fuzzy_name[0].isdigit():
            # 例如 "22网安" -> 提取 "22" 和 "网安"
            grade = ""
            major = ""
            for i, char in enumerate(fuzzy_name):
                if char.isdigit():
                    grade += char
                else:
                    major = fuzzy_name[i:]
                    break

            if grade and major:
                # 尝试匹配 2022级、22级、22等格式
                patterns.extend(
                    [
                        f"%{grade}%{major}%",
                        f"%20{grade}%{major}%",
                        f"%{grade}级%{major}%",
                    ]
                )

        # 去重
        patterns = list(set(patterns))

        matched_classes = []
        for pattern in patterns:
            self.cursor.execute(
                "SELECT DISTINCT class_name FROM gpa_ranking WHERE class_name LIKE ?",
                (pattern,),
            )
            rows = self.cursor.fetchall()
            for row in rows:
                if row["class_name"] not in matched_classes:
                    matched_classes.append(row["class_name"])

        return matched_classes

    def get_class_gpa_stats(
        self, class_name: str, term: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取班级绩点统计信息

        Args:
            class_name: 班级名称
            term: 学期，如 "2024-2025-1" 或 "all"

        Returns:
            统计信息字典，包含 mean, std, max, min, count
        """
        if term == "all":
            # 查询所有学期
            self.cursor.execute(
                """
                SELECT 
                    AVG(weighted_gpa) as mean,
                    MAX(weighted_gpa) as max_gpa,
                    MIN(weighted_gpa) as min_gpa,
                    COUNT(*) as count
                FROM gpa_ranking 
                WHERE class_name = ?
                """,
                (class_name,),
            )
        else:
            self.cursor.execute(
                """
                SELECT 
                    AVG(weighted_gpa) as mean,
                    MAX(weighted_gpa) as max_gpa,
                    MIN(weighted_gpa) as min_gpa,
                    COUNT(*) as count
                FROM gpa_ranking 
                WHERE class_name = ? AND term = ?
                """,
                (class_name, term),
            )
        row = self.cursor.fetchone()

        if not row or row["count"] == 0:
            return None

        # 计算标准差
        if term == "all":
            self.cursor.execute(
                """
                SELECT weighted_gpa FROM gpa_ranking 
                WHERE class_name = ?
                """,
                (class_name,),
            )
        else:
            self.cursor.execute(
                """
                SELECT weighted_gpa FROM gpa_ranking 
                WHERE class_name = ? AND term = ?
                """,
                (class_name, term),
            )
        gpas = [r["weighted_gpa"] for r in self.cursor.fetchall()]

        mean = row["mean"]
        if len(gpas) > 1:
            variance = sum((x - mean) ** 2 for x in gpas) / len(gpas)
            std = math.sqrt(variance)
        else:
            std = 0

        return {
            "mean": mean,
            "std": std,
            "max": row["max_gpa"],
            "min": row["min_gpa"],
            "count": row["count"],
            "gpas": gpas,
        }

    def get_closest_gpa_record(
        self, class_name: str, term: str, target_gpa: float
    ) -> Optional[Dict[str, Any]]:
        """
        获取最接近目标绩点的记录

        Args:
            class_name: 班级名称
            term: 学期，如 "2024-2025-1" 或 "all"
            target_gpa: 目标绩点

        Returns:
            最接近的记录
        """
        if term == "all":
            self.cursor.execute(
                """
                SELECT * FROM gpa_ranking 
                WHERE class_name = ?
                ORDER BY ABS(weighted_gpa - ?) ASC
                LIMIT 1
                """,
                (class_name, target_gpa),
            )
        else:
            self.cursor.execute(
                """
                SELECT * FROM gpa_ranking 
                WHERE class_name = ? AND term = ?
                ORDER BY ABS(weighted_gpa - ?) ASC
                LIMIT 1
                """,
                (class_name, term, target_gpa),
            )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def calculate_gpa_percentile(
        self, class_name: str, term: str, target_gpa: float
    ) -> Optional[Dict[str, Any]]:
        """
        查询目标绩点的百分位排名

        直接从数据库中查找最接近目标绩点的记录，返回实际的排名百分比。

        Args:
            class_name: 班级名称
            term: 学期，如 "2024-2025-1" 或 "all"
            target_gpa: 目标绩点

        Returns:
            包含查询结果的字典
        """
        # 获取最接近目标绩点的记录
        closest_record = self.get_closest_gpa_record(class_name, term, target_gpa)

        if not closest_record:
            return None

        # 获取统计信息（用于参考）
        stats = self.get_class_gpa_stats(class_name, term)

        return {
            "target_gpa": target_gpa,
            "class_name": class_name,
            "term": term,
            "mean": round(stats["mean"], 2) if stats else None,
            "std": round(stats["std"], 3) if stats else None,
            "count": closest_record["total_count"],
            "rank": closest_record["rank"],
            "rank_percent": closest_record["rank_percent"],
            "closest_gpa": closest_record["weighted_gpa"],
        }

    def get_available_terms(self, class_name: str) -> List[str]:
        """
        获取班级可用的学期列表

        Args:
            class_name: 班级名称

        Returns:
            学期列表
        """
        self.cursor.execute(
            "SELECT DISTINCT term FROM gpa_ranking WHERE class_name = ? ORDER BY term",
            (class_name,),
        )
        return [row["term"] for row in self.cursor.fetchall()]

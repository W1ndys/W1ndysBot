import sqlite3
from datetime import date, timedelta
from collections import Counter
import jieba  # 中文分词
import re
import time
import os
from . import DATA_DIR
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64


class QQMessageAnalyzer:
    def __init__(
        self,
        group_id,
        db_path=os.path.join(DATA_DIR, "qq_messages.db"),
    ):
        self.db_path = db_path
        self.group_id = str(group_id)
        self.table_name = f"group_messages_{self.group_id}"
        self._init_db()
        # 正则过滤
        self.filter_patterns = [
            r"\[CQ:.*\]",  # CQ码消息
        ]

    def _init_db(self):
        """初始化数据库和表（按群号分表）"""
        with sqlite3.connect(self.db_path) as conn:
            # 设置时区为东八区
            conn.execute("PRAGMA timezone = '+08:00'")
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_time TIMESTAMP NOT NULL,
                    message_content TEXT NOT NULL,
                    sender_id TEXT
                )
            """
            )
            # 确保日期索引存在
            conn.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_message_date_{self.group_id} 
                ON {self.table_name}(date(message_time))
            """
            )

    def _is_filtered(self, content):
        """判断消息是否需要被过滤"""
        return any(re.search(pattern, content) for pattern in self.filter_patterns)

    def add_message(self, content, sender_id=None, message_time=None):
        """存储单条消息，新增正则过滤"""
        if self._is_filtered(content):
            return  # 匹配过滤规则则不存储
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"INSERT INTO {self.table_name} (message_content, sender_id, message_time) VALUES (?, ?, ?)",
                (content, sender_id, message_time),
            )

    def _get_daily_messages(self, query_date=None):
        """获取某日所有消息(默认今天)"""
        target_date = query_date or date.today()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                f"SELECT message_content FROM {self.table_name} "
                "WHERE date(message_time) = ?",
                (target_date.isoformat(),),
            )
            return [row[0] for row in cursor.fetchall()]

    def _clean_text(self, text):
        """文本清洗"""
        # 移除URL
        text = re.sub(r"http[s]?://\S+", "", text)
        # 移除CQ码
        text = re.sub(r"\[CQ:.*\]", "", text)
        return text.strip()

    def generate_daily_report(self, query_date=None):
        """
        生成每日报告
        返回: (词云数据, top10词汇)
        """
        messages = self._get_daily_messages(query_date)
        if not messages:
            return {}, []

        # 中文分词和词频统计
        word_counter = Counter()
        for msg in messages:
            cleaned = self._clean_text(msg)
            words = jieba.lcut(cleaned)  # 使用结巴分词
            # 直接统计所有词的出现次数，包括重复出现的词
            word_counter.update([w for w in words if len(w) > 1])  # 过滤单字

        # 获取前10高频词
        top10 = word_counter.most_common(10)

        # 词云数据格式: {word: frequency}
        wordcloud_data = dict(word_counter)

        return wordcloud_data, top10

    def cleanup_old_data(self, days_to_keep=30):
        """清理旧数据(保留最近N天)"""
        cutoff_date = (date.today() - timedelta(days=days_to_keep)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"DELETE FROM {self.table_name} WHERE date(message_time) < ?",
                (cutoff_date,),
            )
            # 不要在这里执行 VACUUM

        # 用新的连接单独执行 VACUUM
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("VACUUM")

    def generate_wordcloud_image_base64(self, query_date=None):
        """
        生成词云图片并以base64编码返回
        :param query_date: 指定日期，默认今天
        :return: base64字符串
        """
        wordcloud_data, _ = self.generate_daily_report(query_date)
        if not wordcloud_data:
            return None
        wc = WordCloud(
            font_path=self.get_font_path(),
            width=800,
            height=400,
            background_color="white",
        )
        wc.generate_from_frequencies(wordcloud_data)
        buf = io.BytesIO()
        plt.figure(figsize=(8, 4))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        return img_base64

    def get_font_path(self):
        # Windows
        if os.path.exists("C:/Windows/Fonts/msyh.ttc"):
            return "C:/Windows/Fonts/msyh.ttc"
        # Ubuntu Noto Sans CJK（fonts-noto-cjk 安装后路径）
        elif os.path.exists("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"):
            return "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
        elif os.path.exists("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"):
            return "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
        elif os.path.exists("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"):
            return "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
        elif os.path.exists("/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"):
            return "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
        elif os.path.exists("/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc"):
            return "/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc"
        # Ubuntu 文泉驿
        elif os.path.exists("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"):
            return "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
        else:
            raise RuntimeError(
                "未找到可用的中文字体，请确认已安装 fonts-noto-cjk 或手动安装并指定 font_path"
            )


# ===================== 使用示例 =====================
if __name__ == "__main__":
    # 假设群号为 123456
    analyzer = QQMessageAnalyzer(group_id="123456")

    # 基础用法：插入消息
    analyzer.add_message("今天天气真好！", sender_id="user_001")
    analyzer.add_message("大家一起学习Python吧！", sender_id="user_002")
    analyzer.add_message("http://test.com 这是一个测试链接", sender_id="user_003")

    # 基础用法：生成今天的词云和高频词
    wordcloud_data, top10 = analyzer.generate_daily_report()
    print("今日词云数据：", wordcloud_data)
    print("今日Top10高频词：", top10)

    # 词云图片base64演示
    img_base64 = analyzer.generate_wordcloud_image_base64()
    if img_base64:
        print("词云图片Base64(前100字符)：", img_base64[:100], "...")
    else:
        print("今日无词云数据，无法生成图片")

    # 进阶用法：自定义日期查询（如查询2024-03-20）
    from datetime import date

    wordcloud_data, top10 = analyzer.generate_daily_report(query_date=date(2024, 3, 20))
    print("2024-03-20词云数据：", wordcloud_data)
    print("2024-03-20 Top10高频词：", top10)

    # 进阶用法：清理30天前的旧数据
    analyzer.cleanup_old_data(days_to_keep=30)
    print("已清理30天前的旧消息数据")

    # ===================== 多种情况测试 =====================
    print("\n===== 多种情况测试 =====")

    # 1. 无消息时的处理
    empty_group = QQMessageAnalyzer(group_id="empty_group")
    wordcloud_data, top10 = empty_group.generate_daily_report()
    print("空群今日词云数据：", wordcloud_data)
    print("空群今日Top10高频词：", top10)

    # 2. 插入大量消息后的性能测试（这里只插入1000条做演示，实际可更多）
    start = time.time()
    for i in range(1000):
        analyzer.add_message(f"测试消息{i}，Python真好玩！", sender_id=f"user_{i%10}")
    print(f"插入1000条消息耗时：{time.time() - start:.2f}秒")
    start = time.time()
    wordcloud_data, top10 = analyzer.generate_daily_report()
    print(f"生成词云耗时：{time.time() - start:.2f}秒")
    print("性能群Top10高频词：", top10)

    # 3. 不同群组的独立性测试
    group_a = QQMessageAnalyzer(group_id="A")
    group_b = QQMessageAnalyzer(group_id="B")
    group_a.add_message("A群消息", sender_id="A1")
    group_b.add_message("B群消息", sender_id="B1")
    print("A群词云：", group_a.generate_daily_report()[0])
    print("B群词云：", group_b.generate_daily_report()[0])

    # 4. 消息内容包含特殊字符或仅有链接
    special_group = QQMessageAnalyzer(group_id="special")
    special_group.add_message("！！！？？？###$$$@@@", sender_id="sp1")
    special_group.add_message("https://only.link", sender_id="sp2")
    special_group.add_message("正常消息，带有http://test.com链接", sender_id="sp3")
    wordcloud_data, top10 = special_group.generate_daily_report()
    print("特殊内容群词云：", wordcloud_data)
    print("特殊内容群Top10高频词：", top10)

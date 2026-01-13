import sqlite3
import os
import re
import math
from collections import defaultdict


class DataManager:
    # 类级别缓存，避免重复构建索引
    _inverted_index = None
    _questions_cache = None
    _idf_cache = None

    def __init__(self):
        # 数据库文件位于模块目录下
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(module_dir, "freshman_questions.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # 初始化索引（仅首次）
        if DataManager._inverted_index is None:
            self._build_index()

    def _tokenize(self, text: str) -> list:
        """
        中文分词：使用字符级别 + 二元组(bigram) 分词
        不依赖外部分词库，适合短文本匹配
        """
        if not text:
            return []

        # 移除标点符号和空白
        text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", text)

        tokens = []
        # 单字符
        tokens.extend(list(text))
        # 二元组 (bigram)
        for i in range(len(text) - 1):
            tokens.append(text[i : i + 2])
        # 三元组 (trigram) 提高长词匹配精度
        for i in range(len(text) - 2):
            tokens.append(text[i : i + 3])

        return tokens

    def _build_index(self):
        """
        构建倒排索引和IDF值
        """
        self.cursor.execute(
            "SELECT id, type, question, optionA, optionB, optionC, optionD, optionAnswer FROM questions"
        )
        all_questions = self.cursor.fetchall()

        DataManager._questions_cache = {q[0]: q for q in all_questions}
        DataManager._inverted_index = defaultdict(set)

        # 文档频率统计（用于计算IDF）
        doc_freq = defaultdict(int)
        total_docs = len(all_questions)

        for question in all_questions:
            q_id = question[0]
            q_text = question[2]  # question字段
            tokens = set(self._tokenize(q_text))

            for token in tokens:
                DataManager._inverted_index[token].add(q_id)
                doc_freq[token] += 1

        # 计算IDF值
        DataManager._idf_cache = {}
        for token, freq in doc_freq.items():
            DataManager._idf_cache[token] = math.log(total_docs / (freq + 1)) + 1

    def _calculate_similarity(self, keyword: str, question_text: str) -> float:
        """
        计算关键词与题目的相似度（TF-IDF + Jaccard混合）
        对短关键词采用更严格的匹配策略
        """
        keyword_tokens = self._tokenize(keyword)
        question_tokens = self._tokenize(question_text)

        if not keyword_tokens or not question_tokens:
            return 0.0

        # 清洗后的关键词（去除标点空白）
        clean_keyword = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", keyword)
        clean_question = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", question_text)

        # 对于短关键词（<=4字符），必须完整包含在题目中才有效
        if len(clean_keyword) <= 4:
            if clean_keyword not in clean_question:
                return 0.0  # 短关键词不完整包含则直接返回0

        keyword_set = set(keyword_tokens)
        question_set = set(question_tokens)

        # Jaccard相似度
        intersection = keyword_set & question_set
        union = keyword_set | question_set
        jaccard = len(intersection) / len(union) if union else 0

        # TF-IDF加权得分（降低单字符token权重）
        tfidf_score = 0.0
        for token in intersection:
            idf = DataManager._idf_cache.get(token, 1.0)
            # 单字符token权重降低50%
            if len(token) == 1:
                idf *= 0.5
            # TF使用关键词中的词频
            tf = keyword_tokens.count(token) / len(keyword_tokens)
            tfidf_score += tf * idf

        # 关键词覆盖率：关键词在题目中出现的比例
        keyword_coverage = len(intersection) / len(keyword_set) if keyword_set else 0

        # 连续匹配加分（关键词作为子串出现）
        continuous_bonus = 0.0
        if clean_keyword in clean_question:
            continuous_bonus = 0.6  # 完全包含加分提高
        else:
            # 检查关键词的连续子串匹配（至少3字符以上才有加分）
            for i in range(len(clean_keyword), 2, -1):
                for j in range(len(clean_keyword) - i + 1):
                    substr = clean_keyword[j : j + i]
                    if len(substr) >= 3 and substr in clean_question:
                        continuous_bonus = max(
                            continuous_bonus, 0.3 * (i / len(clean_keyword))
                        )
                        break

        # 综合得分：Jaccard + TF-IDF + 连续匹配 + 覆盖率
        final_score = (
            jaccard * 0.2
            + tfidf_score * 0.3
            + continuous_bonus * 0.3
            + keyword_coverage * 0.2
        )

        return final_score

    def _get_min_score_threshold(self, keyword: str) -> float:
        """
        根据关键词长度动态计算最小相似度阈值
        短关键词要求更高的匹配度，长关键词可以适当放宽

        Args:
            keyword: 搜索关键词

        Returns:
            最小相似度阈值
        """
        keyword_len = len(keyword)
        if keyword_len <= 4:
            return 0.40  # 短关键词要求较高匹配度
        elif keyword_len <= 8:
            return 0.30  # 中等长度
        elif keyword_len <= 15:
            return 0.22  # 较长关键词
        else:
            return 0.15  # 长关键词可以更宽松

    def search_questions(self, keyword: str, limit: int = 5) -> list:
        """
        根据关键词搜索题目（使用倒排索引 + 相似度排序）

        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            匹配的题目列表，按相似度降序排列，每个元素为元组:
            (id, type, question, optionA, optionB, optionC, optionD, optionAnswer)
        """
        keyword_tokens = self._tokenize(keyword)

        if not keyword_tokens:
            return []

        # 动态计算最小相似度阈值
        min_score = self._get_min_score_threshold(keyword)

        # 使用倒排索引快速获取候选文档
        candidate_ids = set()
        for token in keyword_tokens:
            if token in DataManager._inverted_index:
                candidate_ids.update(DataManager._inverted_index[token])

        if not candidate_ids:
            # 倒排索引无结果，回退到LIKE查询（仅当关键词较长时才回退）
            if len(keyword) >= 6:
                self.cursor.execute(
                    """SELECT id, type, question, optionA, optionB, optionC, optionD, optionAnswer
                       FROM questions
                       WHERE question LIKE ?
                       LIMIT ?""",
                    (f"%{keyword}%", limit),
                )
                return self.cursor.fetchall()
            return []

        # 计算相似度并排序
        scored_results = []
        for q_id in candidate_ids:
            question = DataManager._questions_cache[q_id]
            score = self._calculate_similarity(keyword, question[2])
            if score >= min_score:  # 使用动态阈值过滤低质量匹配
                scored_results.append((score, question))

        # 按相似度降序排序
        scored_results.sort(key=lambda x: x[0], reverse=True)

        # 返回前limit个结果
        return [item[1] for item in scored_results[:limit]]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

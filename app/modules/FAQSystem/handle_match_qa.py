import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
from collections import defaultdict
import jieba
from .db_manager import FAQDatabaseManager
import scipy.sparse
from typing import Optional


class AdvancedFAQMatcher:
    def __init__(self, group_id: str):
        """
        初始化高级问答匹配器，加载指定群组的问答对数据。
        参数:
            group_id: str 群组ID
        """
        self.group_id = group_id
        self.FAQ_pairs = []
        self.vectorizer = TfidfVectorizer(tokenizer=self._tokenize)
        self.tfidf_matrix: Optional[scipy.sparse.csr_matrix] = None
        self.keyword_index = defaultdict(list)
        self._load_from_db()
        self.threshold = 0.6

    def _load_from_db(self):
        """
        从数据库加载所有问答对到内存。
        """
        with FAQDatabaseManager(self.group_id) as db:
            self.FAQ_pairs = [(id, q, a) for id, q, a in db.get_all_FAQ_pairs()]

    def _tokenize(self, text):
        """
        对输入文本进行分词处理，返回分词列表。
        参数:
            text: str 输入文本
        返回:
            list 分词结果
        """
        text = text.lower()
        tokens = list(jieba.cut(text))
        return [t for t in tokens if t.strip()]

    def add_FAQ_pair(self, question, answer):
        """
        添加新的问答对到内存和数据库。
        参数:
            question: str 问题
            answer: str 答案
        """
        with FAQDatabaseManager(self.group_id) as db:
            result_id = db.add_FAQ_pair(question, answer)
        if result_id:
            self.FAQ_pairs.append((result_id, question, answer))
            return result_id
        return None

    def delete_FAQ_pair(self, FAQ_id: int) -> bool:
        """
        从内存和数据库中删除指定ID的问答对。
        参数:
            FAQ_id: int 问答对ID
        返回:
            bool 是否删除成功
        """
        # 从内存中删除
        self.FAQ_pairs = [(id, q, a) for id, q, a in self.FAQ_pairs if id != FAQ_id]
        # 从数据库中删除
        with FAQDatabaseManager(self.group_id) as db:
            db.delete_FAQ_pair(FAQ_id)
        return True

    def build_index(self):
        """
        构建TF-IDF索引和关键词倒排索引，用于高效检索。
        """
        # 构建TF-IDF索引
        questions = [q for _, q, a in self.FAQ_pairs]
        self.tfidf_matrix = self.vectorizer.fit_transform(questions).tocsr()  # type: ignore

        # 构建关键词倒排索引
        self.keyword_index.clear()
        for idx, (id, q, a) in enumerate(self.FAQ_pairs):
            keywords = set(self._tokenize(q))
            for word in keywords:
                self.keyword_index[word].append(idx)

    def _get_candidate_indices(self, query):
        """
        使用关键词倒排索引初步筛选候选问题的索引集合。
        参数:
            query: str 查询问题
        返回:
            list 候选问题的索引列表
        """
        # 使用关键词索引初步筛选候选问题
        query_keywords = set(self._tokenize(query))
        candidate_indices = set()

        for word in query_keywords:
            if word in self.keyword_index:
                candidate_indices.update(self.keyword_index[word])

        return (
            list(candidate_indices) if candidate_indices else range(len(self.FAQ_pairs))
        )

    def find_best_match(self, query):
        """
        查找与输入问题最匹配的问答对，返回原始问题、答案、相似度分数和数据库id。
        参数:
            query: str 用户输入的问题
            threshold: float 匹配阈值，低于该值则认为无合适答案
        返回:
            (orig_question, orig_answer, score, id) 或 (None, None, score, None)
        """
        if not self.FAQ_pairs or self.tfidf_matrix is None:
            return None, None, 0.0, None

        # 步骤1: 初步筛选候选问题
        candidate_indices = self._get_candidate_indices(query)

        # 步骤2: 计算TF-IDF余弦相似度
        query_vec = self.vectorizer.transform([query])
        indices = list(candidate_indices)
        assert isinstance(self.tfidf_matrix, scipy.sparse.csr_matrix)
        tfidf_candidates = scipy.sparse.vstack(
            [self.tfidf_matrix[i] for i in indices]
        ).tocsr()
        similarities = cosine_similarity(query_vec, tfidf_candidates)  # type: ignore
        best_candidate_idx = np.argmax(similarities)
        best_score = similarities[0, best_candidate_idx]
        best_FAQ_idx = indices[best_candidate_idx]

        # 步骤3: 使用编辑距离进行二次验证
        seq_score = difflib.SequenceMatcher(
            None, query, self.FAQ_pairs[best_FAQ_idx][1]
        ).ratio()
        # 优化加权方式：TF-IDF与编辑距离0.3:0.7
        combined_score = 0.3 * best_score + 0.7 * seq_score

        if combined_score >= self.threshold:
            FAQ_id, orig_question, orig_answer = self.FAQ_pairs[best_FAQ_idx]
            return orig_question, orig_answer, combined_score, FAQ_id
        return None, None, combined_score, None

    def get_FAQ_id_by_question(self, question: str) -> int:
        """
        根据问题查找对应的问答对ID，找不到返回-1。
        """
        for FAQ_id, q, _ in self.FAQ_pairs:
            if q == question:
                return FAQ_id
        return -1

    def find_multiple_matches(self, query, min_score=0.5, max_results=10):
        """
        查找多个匹配的问答对

        参数:
            query: str，查询文本
            min_score: float，最小相似度阈值
            max_results: int，最大返回结果数量

        返回:
            list，包含 (question, answer, score, qa_id) 的元组列表，按相似度降序排列
        """
        if not self.FAQ_pairs or self.tfidf_matrix is None:
            return []

        # 获取候选问题索引
        candidate_indices = self._get_candidate_indices(query)

        # 计算TF-IDF相似度
        query_vec = self.vectorizer.transform([query])
        results = []

        for idx in candidate_indices:
            FAQ_id, question, answer = self.FAQ_pairs[idx]

            # 计算TF-IDF相似度
            tfidf_sim = cosine_similarity(query_vec, self.tfidf_matrix[idx : idx + 1])[
                0, 0
            ]

            # 计算编辑距离相似度
            seq_sim = difflib.SequenceMatcher(None, query, question).ratio()

            # 组合相似度 (与find_best_match保持一致)
            combined_score = 0.3 * tfidf_sim + 0.7 * seq_sim

            if combined_score >= min_score:
                results.append((question, answer, combined_score, FAQ_id))

        # 按相似度降序排列并限制数量
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:max_results]


if __name__ == "__main__":
    matcher = AdvancedFAQMatcher("1234567890")
    matcher.build_index()

    while True:
        query = input("请输入问题: ")
        orig_question, answer, score, FAQ_id = matcher.find_best_match(query)
        print(f"问题: {query}")
        if answer:
            print(f"数据库原句: {orig_question}")
            print(f"匹配答案: {answer} (相似度: {score:.2f}) [ID: {FAQ_id}]")
        else:
            print(f"未找到合适答案 (相似度: {score:.2f})\n")

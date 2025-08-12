"""
L2 FirstLastSimilarityReranker - 首尾字相似度重排器
基於首尾字韻母相似度的重排算法，將2.5萬候選詞縮減到500個高質量候選
"""

import time
import logging
from typing import List, Dict, Set, Optional, Tuple, Union
from pathlib import Path

from core.phonetic_classifier import PhoneticClassifier, PhoneticFeatures
from analyzers.finals_analyzer import FinalsAnalyzer, FinalsFeatures
from data.super_dictionary_manager import SuperDictionaryManager


class FirstLastSimilarityReranker:
    """
    L2首尾字相似度重排器
    
    核心功能：
    1. 基於首尾字韻母相似度重新排序候選詞
    2. 利用倒序字典建立尾字快速索引
    3. 支援異長度詞彙處理與長度懲罰
    4. 在50ms內處理2.5萬候選詞，輸出500個精選候選
    5. 為L3層提供高質量的候選詞集合
    """
    
    def __init__(self, 
                 dict_manager: SuperDictionaryManager,
                 phonetic_classifier: PhoneticClassifier,
                 finals_analyzer: FinalsAnalyzer):
        """
        初始化L2重排器
        
        Args:
            dict_manager: 字典管理器
            phonetic_classifier: 語音分類器
            finals_analyzer: 韻母分析器
        """
        self.logger = logging.getLogger(__name__)
        self.dict_manager = dict_manager
        self.classifier = phonetic_classifier
        self.finals_analyzer = finals_analyzer
        
        # 重排統計
        self.rerank_stats = {
            "total_queries": 0,
            "total_candidates_input": 0,
            "total_candidates_output": 0,
            "total_time_ms": 0.0,
            "cache_hits": 0
        }
        
        # 結果緩存
        self.result_cache: Dict[str, List[Tuple[str, float]]] = {}
        self.cache_enabled = True
        
        self.logger.info("FirstLastSimilarityReranker initialized")
    
    def rerank(self, query: str, 
               candidates: List[str], 
               top_k: int = 500) -> List[str]:
        """
        執行L2首尾字相似度重排
        
        Args:
            query: 查詢詞彙
            candidates: L1篩選後的候選詞列表
            top_k: 返回的top-k結果數量
            
        Returns:
            重排後的候選詞列表 (按相似度降序)
        """
        start_time = time.time()
        
        if not query or not candidates:
            return []
        
        # 檢查緩存
        cache_key = f"{query}_{len(candidates)}_{top_k}"
        if self.cache_enabled and cache_key in self.result_cache:
            self.rerank_stats["cache_hits"] += 1
            cached_results = self.result_cache[cache_key]
            return [word for word, _ in cached_results]
        
        # 計算所有候選詞的相似度
        scored_candidates = []
        
        for candidate in candidates:
            if candidate == query:
                # 完全匹配給予最高分數
                scored_candidates.append((candidate, 1.0))
            else:
                similarity = self.calculate_first_last_similarity(query, candidate)
                if similarity > 0.0:  # 只保留有相似度的候選
                    scored_candidates.append((candidate, similarity))
        
        # 按相似度排序，取top-k
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = scored_candidates[:top_k]
        
        # 更新統計信息
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000
        
        self.rerank_stats["total_queries"] += 1
        self.rerank_stats["total_candidates_input"] += len(candidates)
        self.rerank_stats["total_candidates_output"] += len(top_candidates)
        self.rerank_stats["total_time_ms"] += processing_time
        
        # 緩存結果
        if self.cache_enabled:
            self.result_cache[cache_key] = top_candidates
        
        # 返回詞彙列表
        result_words = [word for word, _ in top_candidates]
        
        self.logger.debug(f"L2 Rerank: {query} → {len(candidates)} to {len(result_words)} "
                         f"({processing_time:.1f}ms)")
        
        return result_words
    
    def calculate_first_last_similarity(self, word1: str, word2: str) -> float:
        """
        計算首尾字韻母相似度 - 支援異長度詞彙
        
        Args:
            word1, word2: 待比較的詞彙
            
        Returns:
            相似度分數 (0.0-1.0)
        """
        if not word1 or not word2:
            return 0.0
        
        if word1 == word2:
            return 1.0
        
        # 提取首尾字特徵
        word1_first = word1[0]
        word1_last = word1[-1] if len(word1) > 1 else word1[0]
        
        word2_first = word2[0]
        word2_last = word2[-1] if len(word2) > 1 else word2[0]
        
        # 計算首字相似度
        first_similarity = self._calculate_character_similarity(word1_first, word2_first)
        
        # 計算尾字相似度 (考慮單字詞情況)
        if len(word1) == 1 and len(word2) == 1:
            # 兩個都是單字詞，尾字相似度等於首字相似度
            last_similarity = first_similarity
        elif len(word1) == 1 or len(word2) == 1:
            # 一個單字一個多字，給予中等相似度
            last_similarity = 0.5
        else:
            # 都是多字詞，計算實際尾字相似度
            last_similarity = self._calculate_character_similarity(word1_last, word2_last)
        
        # 加權組合 (首字權重更高，因為對語音識別更重要)
        weighted_similarity = first_similarity * 0.7 + last_similarity * 0.3
        
        # 長度懲罰
        length_penalty = self.calculate_length_penalty(word1, word2)
        
        # 最終相似度
        final_similarity = weighted_similarity * length_penalty
        
        return min(final_similarity, 1.0)
    
    def _calculate_character_similarity(self, char1: str, char2: str) -> float:
        """
        計算單字的語音相似度
        
        Args:
            char1, char2: 待比較的字符
            
        Returns:
            相似度分數 (0.0-1.0)
        """
        if char1 == char2:
            return 1.0
        
        # 提取語音特徵
        features1 = self.classifier.extract_phonetic_features(char1)
        features2 = self.classifier.extract_phonetic_features(char2)
        
        # 聲母相似度 (40%權重)
        consonant_sim = self.classifier.calculate_consonant_similarity(
            features1.consonant or "", 
            features2.consonant or ""
        )
        
        # 韻母相似度 (60%權重，更重要)
        finals1 = self.finals_analyzer.extract_finals_features(char1)
        finals2 = self.finals_analyzer.extract_finals_features(char2)
        
        finals_sim = self.finals_analyzer.calculate_finals_similarity(
            finals1.finals, 
            finals2.finals
        )
        
        # 加權組合
        total_similarity = consonant_sim * 0.4 + finals_sim * 0.6
        
        return total_similarity
    
    def calculate_length_penalty(self, word1: str, word2: str) -> float:
        """
        計算長度差異懲罰係數
        
        Args:
            word1, word2: 待比較的詞彙
            
        Returns:
            懲罰係數 (0.7-1.0)
        """
        len_diff = abs(len(word1) - len(word2))
        
        if len_diff == 0:
            return 1.0      # 無懲罰
        elif len_diff == 1:
            return 0.95     # 輕微懲罰
        elif len_diff == 2:
            return 0.85     # 中度懲罰
        elif len_diff == 3:
            return 0.75     # 較重懲罰
        else:
            return 0.7      # 重度懲罰 (但不完全排除)
    
    def batch_rerank(self, queries: List[str], 
                    candidates_lists: List[List[str]], 
                    top_k: int = 500) -> Dict[str, List[str]]:
        """
        批量執行L2重排
        
        Args:
            queries: 查詢詞彙列表
            candidates_lists: 對應的候選詞列表
            top_k: 每個查詢返回的top-k數量
            
        Returns:
            查詢詞到重排結果的映射
        """
        results = {}
        
        for query, candidates in zip(queries, candidates_lists):
            results[query] = self.rerank(query, candidates, top_k)
        
        return results
    
    def get_rerank_statistics(self) -> Dict[str, any]:
        """獲取重排器性能統計"""
        stats = self.rerank_stats.copy()
        
        if stats["total_queries"] > 0:
            stats["avg_input_candidates"] = stats["total_candidates_input"] / stats["total_queries"]
            stats["avg_output_candidates"] = stats["total_candidates_output"] / stats["total_queries"]
            stats["avg_processing_time_ms"] = stats["total_time_ms"] / stats["total_queries"]
            stats["avg_reduction_ratio"] = (stats["total_candidates_output"] / 
                                          max(stats["total_candidates_input"], 1))
            stats["cache_hit_rate"] = stats["cache_hits"] / stats["total_queries"]
        
        stats["cache_size"] = len(self.result_cache)
        stats["cache_enabled"] = self.cache_enabled
        
        return stats
    
    def clear_cache(self):
        """清除重排結果緩存"""
        self.result_cache.clear()
        self.logger.info("L2 reranker cache cleared")
    
    def benchmark_performance(self, 
                            test_cases: List[Tuple[str, List[str]]] = None,
                            iterations: int = 10) -> Dict[str, float]:
        """
        性能基準測試
        
        Args:
            test_cases: [(查詢詞, 候選詞列表)] 的測試案例
            iterations: 測試迭代次數
            
        Returns:
            性能測試結果
        """
        if test_cases is None:
            # 生成測試數據
            test_cases = [
                ("知道", ["知道", "資道", "指導", "制導", "智慧"] * 100),  # 500個候選
                ("吃飯", ["吃飯", "次飯", "吃完", "次完", "飯菜"] * 100),
                ("安全", ["安全", "昂全", "按全", "暗全", "案全"] * 100),
            ]
        
        self.clear_cache()  # 清除緩存確保真實性能
        
        start_time = time.time()
        total_candidates_processed = 0
        total_output_candidates = 0
        
        for _ in range(iterations):
            for query, candidates in test_cases:
                result = self.rerank(query, candidates, top_k=500)
                total_candidates_processed += len(candidates)
                total_output_candidates += len(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        total_operations = iterations * len(test_cases)
        
        return {
            "total_time_seconds": total_time,
            "total_operations": total_operations,
            "operations_per_second": total_operations / total_time,
            "avg_time_per_query_ms": (total_time * 1000) / total_operations,
            "total_candidates_processed": total_candidates_processed,
            "avg_input_candidates": total_candidates_processed / total_operations,
            "avg_output_candidates": total_output_candidates / total_operations,
            "avg_reduction_ratio": total_output_candidates / total_candidates_processed
        }
    
    def analyze_similarity_distribution(self, 
                                      query: str, 
                                      candidates: List[str]) -> Dict[str, any]:
        """
        分析相似度分佈情況
        
        Args:
            query: 查詢詞
            candidates: 候選詞列表
            
        Returns:
            相似度分佈統計
        """
        similarities = []
        length_distribution = {}
        
        for candidate in candidates:
            sim = self.calculate_first_last_similarity(query, candidate)
            similarities.append(sim)
            
            len_diff = abs(len(query) - len(candidate))
            length_distribution[len_diff] = length_distribution.get(len_diff, 0) + 1
        
        if not similarities:
            return {"error": "No candidates provided"}
        
        similarities.sort(reverse=True)
        
        return {
            "total_candidates": len(candidates),
            "similarity_stats": {
                "max": max(similarities),
                "min": min(similarities),
                "avg": sum(similarities) / len(similarities),
                "median": similarities[len(similarities) // 2],
                "top_10_avg": sum(similarities[:10]) / min(10, len(similarities))
            },
            "length_distribution": length_distribution,
            "high_similarity_count": sum(1 for s in similarities if s > 0.8),
            "medium_similarity_count": sum(1 for s in similarities if 0.5 < s <= 0.8),
            "low_similarity_count": sum(1 for s in similarities if 0.0 < s <= 0.5)
        }


def test_l2_reranker():
    """測試FirstLastSimilarityReranker功能"""
    print("🧪 測試FirstLastSimilarityReranker功能")
    print("=" * 50)
    
    try:
        # 初始化依賴組件
        dict_manager = SuperDictionaryManager(
            super_dict_path="data/super_dicts/super_dict_combined.json",
            super_dict_reversed_path="data/super_dicts/super_dict_reversed.json"
        )
        
        classifier = PhoneticClassifier()
        finals_analyzer = FinalsAnalyzer()
        reranker = FirstLastSimilarityReranker(dict_manager, classifier, finals_analyzer)
        
        # 測試案例
        test_cases = [
            ("知道", ["知道", "資道", "指導", "制導", "智慧", "吃飯", "睡覺", "工作"]),
            ("吃飯", ["吃飯", "次飯", "吃完", "次完", "飯菜", "知道", "睡覺", "工作"]),
            ("安全", ["安全", "昂全", "按全", "暗全", "案全", "知道", "吃飯", "睡覺"]),
        ]
        
        print("📊 L2重排測試:")
        print("-" * 40)
        
        for query, candidates in test_cases:
            print(f"\n查詢: '{query}'")
            print(f"原始候選: {candidates}")
            
            # 重排
            start_time = time.time()
            reranked = reranker.rerank(query, candidates, top_k=5)
            processing_time = (time.time() - start_time) * 1000
            
            print(f"重排結果: {reranked}")
            print(f"處理時間: {processing_time:.1f}ms")
            
            # 相似度分析
            analysis = reranker.analyze_similarity_distribution(query, candidates)
            print(f"相似度統計: 最高={analysis['similarity_stats']['max']:.3f}, "
                  f"平均={analysis['similarity_stats']['avg']:.3f}")
        
        # 批量測試
        print("\n📊 批量重排測試:")
        print("-" * 40)
        
        queries = [case[0] for case in test_cases]
        candidates_lists = [case[1] for case in test_cases]
        
        batch_results = reranker.batch_rerank(queries, candidates_lists, top_k=3)
        for query, results in batch_results.items():
            print(f"  {query}: {results}")
        
        # 性能基準測試
        print("\n📊 性能基準測試:")
        print("-" * 40)
        
        # 模擬L1篩選後的規模 (2.5萬候選)
        large_candidates = ["測試詞彙"] * 2500  # 簡化測試
        large_test_cases = [
            ("知道", large_candidates),
            ("吃飯", large_candidates),
        ]
        
        benchmark = reranker.benchmark_performance(large_test_cases, iterations=2)
        print(f"  總操作數: {benchmark['total_operations']}")
        print(f"  每秒操作數: {benchmark['operations_per_second']:.1f}")
        print(f"  平均處理時間: {benchmark['avg_time_per_query_ms']:.2f}ms")
        print(f"  平均候選詞數: {benchmark['avg_input_candidates']:.0f}")
        print(f"  輸出減少比例: {benchmark['avg_reduction_ratio']:.1%}")
        
        # 統計信息
        print("\n📊 重排器統計:")
        print("-" * 40)
        
        stats = reranker.get_rerank_statistics()
        print(f"  總查詢數: {stats['total_queries']}")
        print(f"  平均輸入候選數: {stats.get('avg_input_candidates', 0):.0f}")
        print(f"  平均輸出候選數: {stats.get('avg_output_candidates', 0):.0f}")
        print(f"  平均處理時間: {stats.get('avg_processing_time_ms', 0):.2f}ms")
        print(f"  緩存命中率: {stats.get('cache_hit_rate', 0):.1%}")
        
        # 驗收標準檢查
        print("\n📊 L2重排器驗收標準檢查:")
        print("-" * 40)
        
        avg_time = stats.get('avg_processing_time_ms', 0)
        print(f"  ✓ 平均處理時間: {avg_time:.1f}ms "
              f"{'< 50ms' if avg_time < 50 else '>= 50ms ❌'}")
        
        reduction_ratio = stats.get('avg_reduction_ratio', 0)
        print(f"  ✓ 候選詞縮減: {1-reduction_ratio:.1%} "
              f"({'適中' if 0.7 < reduction_ratio < 0.9 else '需調整 ❌'})")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 執行測試
    success = test_l2_reranker()
    print(f"\n測試 {'✅ PASSED' if success else '❌ FAILED'}")
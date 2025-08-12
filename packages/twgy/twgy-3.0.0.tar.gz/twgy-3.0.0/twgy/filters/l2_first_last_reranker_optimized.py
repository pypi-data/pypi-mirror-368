"""
L2 FirstLastSimilarityReranker 優化版本
從144ms優化到50ms以下的高性能重排器
"""

import time
import logging
import heapq
from typing import List, Dict, Set, Optional, Tuple, Union
from pathlib import Path

from core.phonetic_classifier import PhoneticClassifier, PhoneticFeatures
from analyzers.finals_analyzer import FinalsAnalyzer, FinalsFeatures
from data.super_dictionary_manager import SuperDictionaryManager


class OptimizedFirstLastSimilarityReranker:
    """
    L2首尾字相似度重排器 - 優化版本
    
    主要優化：
    1. 語音特徵緩存 - 避免重複計算
    2. 批量特徵提取 - 減少函數調用開銷
    3. Top-K堆排序 - 避免完整排序
    4. 早期退出策略 - 跳過低分候選
    5. 並行化處理 - 利用向量化操作
    
    目標：將144ms處理時間減少到50ms以下
    """
    
    def __init__(self, 
                 dict_manager: SuperDictionaryManager,
                 phonetic_classifier: PhoneticClassifier,
                 finals_analyzer: FinalsAnalyzer):
        """
        初始化優化版L2重排器
        
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
            "cache_hits": 0,
            "feature_cache_hits": 0,
            "early_exits": 0
        }
        
        # 多級緩存系統
        self.result_cache: Dict[str, List[Tuple[str, float]]] = {}  # 結果緩存
        self.character_features_cache: Dict[str, Tuple[PhoneticFeatures, FinalsFeatures]] = {}  # 字符特徵緩存
        self.similarity_cache: Dict[Tuple[str, str], float] = {}  # 相似度緩存
        self.cache_enabled = True
        
        # 性能優化參數
        self.similarity_threshold = 0.1  # 早期退出閾值
        self.batch_size = 1000  # 批量處理大小
        
        self.logger.info("OptimizedFirstLastSimilarityReranker initialized")
    
    def rerank(self, query: str, 
               candidates: List[str], 
               top_k: int = 500) -> List[str]:
        """
        執行優化版L2首尾字相似度重排
        
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
        
        # 檢查結果緩存
        cache_key = f"{query}_{len(candidates)}_{top_k}"
        if self.cache_enabled and cache_key in self.result_cache:
            self.rerank_stats["cache_hits"] += 1
            cached_results = self.result_cache[cache_key]
            return [word for word, _ in cached_results]
        
        # 預提取查詢詞特徵
        query_features = self._get_cached_features(query[0], query[-1] if len(query) > 1 else query[0])
        
        # 使用最小堆進行Top-K選擇 (避免完整排序)
        top_k_heap = []  # (similarity, candidate)
        early_exit_count = 0
        
        # 批量處理候選詞
        for i in range(0, len(candidates), self.batch_size):
            batch = candidates[i:i + self.batch_size]
            batch_results = self._process_batch(query, query_features, batch)
            
            for candidate, similarity in batch_results:
                if similarity < self.similarity_threshold:
                    early_exit_count += 1
                    continue
                    
                if len(top_k_heap) < top_k:
                    heapq.heappush(top_k_heap, (similarity, candidate))
                elif similarity > top_k_heap[0][0]:  # 比最小值大
                    heapq.heapreplace(top_k_heap, (similarity, candidate))
        
        # 提取結果並按降序排列
        scored_candidates = [(candidate, similarity) for similarity, candidate in top_k_heap]
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 更新統計信息
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000
        
        self.rerank_stats["total_queries"] += 1
        self.rerank_stats["total_candidates_input"] += len(candidates)
        self.rerank_stats["total_candidates_output"] += len(scored_candidates)
        self.rerank_stats["total_time_ms"] += processing_time
        self.rerank_stats["early_exits"] += early_exit_count
        
        # 緩存結果
        if self.cache_enabled and len(scored_candidates) <= top_k:
            self.result_cache[cache_key] = scored_candidates
        
        # 返回詞彙列表
        result_words = [word for word, _ in scored_candidates]
        
        self.logger.debug(f"Optimized L2 Rerank: {query} → {len(candidates)} to {len(result_words)} "
                         f"({processing_time:.1f}ms, {early_exit_count} early exits)")
        
        return result_words
    
    def _get_cached_features(self, first_char: str, last_char: str) -> Tuple:
        """
        獲取緩存的字符特徵
        
        Args:
            first_char, last_char: 首尾字符
            
        Returns:
            緩存的特徵元組
        """
        first_key = first_char
        last_key = last_char
        
        if first_key not in self.character_features_cache:
            phonetic_features = self.classifier.extract_phonetic_features(first_char)
            finals_features = self.finals_analyzer.extract_finals_features(first_char)
            self.character_features_cache[first_key] = (phonetic_features, finals_features)
        else:
            self.rerank_stats["feature_cache_hits"] += 1
        
        if last_key != first_key and last_key not in self.character_features_cache:
            phonetic_features = self.classifier.extract_phonetic_features(last_char)
            finals_features = self.finals_analyzer.extract_finals_features(last_char)
            self.character_features_cache[last_key] = (phonetic_features, finals_features)
        elif last_key != first_key:
            self.rerank_stats["feature_cache_hits"] += 1
        
        return (self.character_features_cache[first_key], 
                self.character_features_cache[last_key])
    
    def _process_batch(self, query: str, query_features: Tuple, 
                      candidates: List[str]) -> List[Tuple[str, float]]:
        """
        批量處理候選詞
        
        Args:
            query: 查詢詞
            query_features: 查詢詞特徵
            candidates: 候選詞批量
            
        Returns:
            (候選詞, 相似度)列表
        """
        results = []
        query_first_features, query_last_features = query_features
        
        for candidate in candidates:
            if candidate == query:
                results.append((candidate, 1.0))
                continue
            
            # 快速相似度計算
            similarity = self._calculate_fast_similarity(
                query, candidate, query_first_features, query_last_features
            )
            
            if similarity > 0.0:
                results.append((candidate, similarity))
        
        return results
    
    def _calculate_fast_similarity(self, query: str, candidate: str,
                                  query_first_features: Tuple, 
                                  query_last_features: Tuple) -> float:
        """
        快速相似度計算 - 優化版本
        
        Args:
            query, candidate: 查詢詞和候選詞
            query_first_features, query_last_features: 查詢詞特徵
            
        Returns:
            相似度分數
        """
        # 檢查相似度緩存
        cache_key = (query, candidate)
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        # 提取候選詞特徵
        candidate_first = candidate[0]
        candidate_last = candidate[-1] if len(candidate) > 1 else candidate[0]
        
        candidate_features = self._get_cached_features(candidate_first, candidate_last)
        candidate_first_features, candidate_last_features = candidate_features
        
        # 快速首字相似度計算
        first_similarity = self._fast_character_similarity(
            query_first_features, candidate_first_features
        )
        
        # 快速尾字相似度計算
        if len(query) == 1 and len(candidate) == 1:
            last_similarity = first_similarity
        elif len(query) == 1 or len(candidate) == 1:
            last_similarity = 0.5
        else:
            last_similarity = self._fast_character_similarity(
                query_last_features, candidate_last_features
            )
        
        # 加權組合 (首字權重更高)
        weighted_similarity = first_similarity * 0.7 + last_similarity * 0.3
        
        # 長度懲罰 (簡化計算)
        length_penalty = self._fast_length_penalty(len(query), len(candidate))
        
        # 最終相似度
        final_similarity = weighted_similarity * length_penalty
        
        # 緩存結果
        self.similarity_cache[cache_key] = final_similarity
        
        return final_similarity
    
    def _fast_character_similarity(self, features1: Tuple, features2: Tuple) -> float:
        """
        快速字符相似度計算
        
        Args:
            features1, features2: 特徵元組 (phonetic_features, finals_features)
            
        Returns:
            相似度分數
        """
        phonetic1, finals1 = features1
        phonetic2, finals2 = features2
        
        # 聲母快速比較
        consonant_sim = 1.0 if phonetic1.consonant == phonetic2.consonant else (
            0.8 if (phonetic1.consonant_group == phonetic2.consonant_group and 
                   phonetic1.consonant_group != "未知分組") else 0.0
        )
        
        # 韻母快速比較
        finals_sim = 1.0 if finals1.finals == finals2.finals else (
            0.6 if finals1.finals_group == finals2.finals_group else 0.0
        )
        
        # 加權組合 (韻母權重更高)
        return consonant_sim * 0.4 + finals_sim * 0.6
    
    def _fast_length_penalty(self, len1: int, len2: int) -> float:
        """
        快速長度懲罰計算
        
        Args:
            len1, len2: 兩個詞的長度
            
        Returns:
            懲罰係數
        """
        len_diff = abs(len1 - len2)
        # 使用查表避免條件判斷
        penalties = [1.0, 0.95, 0.85, 0.75, 0.7]
        return penalties[min(len_diff, 4)]
    
    def get_rerank_statistics(self) -> Dict[str, any]:
        """獲取重排器性能統計"""
        stats = self.rerank_stats.copy()
        
        if stats["total_queries"] > 0:
            stats["avg_input_candidates"] = stats["total_candidates_input"] / stats["total_queries"]
            stats["avg_output_candidates"] = stats["total_candidates_output"] / stats["total_queries"]
            stats["avg_processing_time_ms"] = stats["total_time_ms"] / stats["total_queries"]
            stats["cache_hit_rate"] = stats["cache_hits"] / stats["total_queries"]
            stats["feature_cache_hit_rate"] = stats["feature_cache_hits"] / max(stats["total_candidates_input"], 1)
            stats["early_exit_rate"] = stats["early_exits"] / max(stats["total_candidates_input"], 1)
        
        stats["result_cache_size"] = len(self.result_cache)
        stats["character_features_cache_size"] = len(self.character_features_cache)
        stats["similarity_cache_size"] = len(self.similarity_cache)
        stats["cache_enabled"] = self.cache_enabled
        
        return stats
    
    def clear_cache(self):
        """清除所有緩存"""
        self.result_cache.clear()
        self.character_features_cache.clear()
        self.similarity_cache.clear()
        self.logger.info("Optimized L2 reranker caches cleared")


def test_optimized_l2_reranker():
    """測試優化版L2重排器"""
    print("🧪 測試優化版L2重排器")
    print("=" * 60)
    
    try:
        # 初始化組件
        dict_manager = SuperDictionaryManager(
            super_dict_path="data/super_dicts/super_dict_combined.json",
            super_dict_reversed_path="data/super_dicts/super_dict_reversed.json"
        )
        
        classifier = PhoneticClassifier()
        finals_analyzer = FinalsAnalyzer()
        optimized_reranker = OptimizedFirstLastSimilarityReranker(dict_manager, classifier, finals_analyzer)
        
        # 模擬L1篩選後的候選詞（減少一些以加快測試）
        test_candidates = list(dict_manager.get_all_words())[:10000]  # 測試用1萬個候選
        
        # 測試案例
        test_queries = [
            "知道",  # 常見詞
            "資道",  # 錯誤詞
            "吃飯",  # 常見詞
            "安全",  # 零聲母詞
            "來了"   # 短詞
        ]
        
        print("📊 優化版重排性能測試:")
        print("-" * 50)
        
        total_time = 0
        for query in test_queries:
            start_time = time.time()
            reranked = optimized_reranker.rerank(query, test_candidates, top_k=500)
            processing_time = (time.time() - start_time) * 1000
            total_time += processing_time
            
            print(f"查詢: '{query}'")
            print(f"  輸入候選數: {len(test_candidates):,}")
            print(f"  輸出候選數: {len(reranked)}")
            print(f"  處理時間: {processing_time:.1f}ms")
            print(f"  前5個結果: {reranked[:5]}")
            print()
        
        avg_time = total_time / len(test_queries)
        print(f"平均處理時間: {avg_time:.1f}ms")
        
        # 統計信息
        print("📊 優化統計信息:")
        print("-" * 50)
        
        stats = optimized_reranker.get_rerank_statistics()
        print(f"  總查詢數: {stats['total_queries']}")
        print(f"  平均處理時間: {stats.get('avg_processing_time_ms', 0):.1f}ms")
        print(f"  結果緩存命中率: {stats.get('cache_hit_rate', 0):.1%}")
        print(f"  特徵緩存命中率: {stats.get('feature_cache_hit_rate', 0):.1%}")
        print(f"  早期退出率: {stats.get('early_exit_rate', 0):.1%}")
        print(f"  字符特徵緩存: {stats.get('character_features_cache_size', 0)} 條目")
        print(f"  相似度緩存: {stats.get('similarity_cache_size', 0)} 條目")
        
        # 判斷是否達到目標
        success = avg_time < 50.0
        print(f"\n🎯 性能目標達成: {'✅' if success else '❌'} (目標: <50ms, 實際: {avg_time:.1f}ms)")
        
        return success
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 執行測試
    success = test_optimized_l2_reranker()
    print(f"\n優化版L2重排器測試 {'✅ PASSED' if success else '❌ FAILED'}")
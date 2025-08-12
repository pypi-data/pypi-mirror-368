"""
L3 FullPhoneticReranker - 完整語音特徵精排器
結合聲韻調三維度語音特徵的最終精排，將500候選縮減到最佳50個結果
"""

import time
import logging
from typing import List, Dict, Set, Optional, Tuple, Union, Any
from pathlib import Path
from dataclasses import dataclass

from core.phonetic_classifier import PhoneticClassifier, PhoneticFeatures
from analyzers.finals_analyzer import FinalsAnalyzer, FinalsFeatures
from analyzers.tone_analyzer import ToneAnalyzer, ToneFeatures
from data.super_dictionary_manager import SuperDictionaryManager


@dataclass
class CompletePhoneticFeatures:
    """完整語音特徵結構"""
    character: str = ""
    consonant_features: Optional[PhoneticFeatures] = None
    finals_features: Optional[FinalsFeatures] = None
    tone_features: Optional[ToneFeatures] = None
    
    # 綜合相似度分數
    total_similarity: float = 0.0
    consonant_similarity: float = 0.0
    finals_similarity: float = 0.0
    tone_similarity: float = 0.0


@dataclass
class WordPhoneticProfile:
    """詞彙語音特徵檔案"""
    word: str = ""
    character_features: List[CompletePhoneticFeatures] = None
    word_length: int = 0
    overall_similarity: float = 0.0
    complexity_score: float = 0.0      # 語音複雜度評估
    
    def __post_init__(self):
        if self.character_features is None:
            self.character_features = []
        self.word_length = len(self.word)


class FullPhoneticReranker:
    """
    L3完整語音特徵精排器
    
    核心功能：
    1. 整合聲韻調三維度語音特徵
    2. 實現多字詞逐字對比與整體評估  
    3. 支援語音複雜度評估與案例分級
    4. 記錄訓練數據供第二期機器學習模型使用
    5. 在100ms內處理500候選詞，輸出50個最佳結果
    """
    
    def __init__(self, 
                 dict_manager: SuperDictionaryManager,
                 phonetic_classifier: PhoneticClassifier,
                 finals_analyzer: FinalsAnalyzer,
                 tone_analyzer: ToneAnalyzer,
                 enable_data_logging: bool = True):
        """
        初始化L3精排器
        
        Args:
            dict_manager: 字典管理器
            phonetic_classifier: 聲母分類器
            finals_analyzer: 韻母分析器
            tone_analyzer: 聲調分析器
            enable_data_logging: 是否啟用數據記錄
        """
        self.logger = logging.getLogger(__name__)
        self.dict_manager = dict_manager
        self.consonant_classifier = phonetic_classifier
        self.finals_analyzer = finals_analyzer
        self.tone_analyzer = tone_analyzer
        self.enable_data_logging = enable_data_logging
        
        # 語音特徵權重配置 (可調參數)
        self.feature_weights = {
            "consonant": 0.35,      # 聲母權重35%
            "finals": 0.45,         # 韻母權重45% (更重要)
            "tone": 0.20           # 聲調權重20%
        }
        
        # 複雜度評估配置
        self.complexity_thresholds = {
            "simple": 0.8,          # 簡單案例：相似度>0.8
            "medium": 0.5,          # 中等案例：0.5<相似度≤0.8
            "complex": 0.0          # 複雜案例：相似度≤0.5
        }
        
        # 性能統計
        self.rerank_stats = {
            "total_queries": 0,
            "total_candidates_input": 0,
            "total_candidates_output": 0,
            "total_time_ms": 0.0,
            "complexity_distribution": {"simple": 0, "medium": 0, "complex": 0},
            "cache_hits": 0
        }
        
        # 結果緩存
        self.result_cache: Dict[str, List[WordPhoneticProfile]] = {}
        self.cache_enabled = True
        
        # 訓練數據記錄
        self.training_data = [] if enable_data_logging else None
        
        self.logger.info("FullPhoneticReranker initialized")
    
    def rerank(self, query: str, 
               candidates: List[str], 
               top_k: int = 50) -> List[str]:
        """
        執行L3完整語音特徵精排
        
        Args:
            query: 查詢詞彙
            candidates: L2重排後的候選詞列表 (~500個)
            top_k: 返回的top-k結果數量
            
        Returns:
            精排後的候選詞列表 (按相似度降序)
        """
        start_time = time.time()
        
        if not query or not candidates:
            return []
        
        # 檢查緩存
        cache_key = f"{query}_{len(candidates)}_{top_k}"
        if self.cache_enabled and cache_key in self.result_cache:
            self.rerank_stats["cache_hits"] += 1
            cached_profiles = self.result_cache[cache_key]
            return [profile.word for profile in cached_profiles]
        
        # 構建查詢詞語音特徵檔案
        query_profile = self._build_phonetic_profile(query)
        
        # 批量構建候選詞語音特徵檔案
        candidate_profiles = []
        for candidate in candidates:
            if candidate == query:
                # 完全匹配給予最高分數
                profile = WordPhoneticProfile(word=candidate, overall_similarity=1.0)
                candidate_profiles.append(profile)
            else:
                profile = self._build_phonetic_profile(candidate)
                # 計算與查詢詞的綜合相似度
                profile.overall_similarity = self._calculate_word_similarity(query_profile, profile)
                # 評估語音複雜度
                profile.complexity_score = self._assess_complexity(query_profile, profile)
                candidate_profiles.append(profile)
        
        # 按綜合相似度排序
        candidate_profiles.sort(key=lambda x: x.overall_similarity, reverse=True)
        top_profiles = candidate_profiles[:top_k]
        
        # 記錄訓練數據
        if self.enable_data_logging:
            self._log_training_data(query_profile, candidate_profiles, top_profiles)
        
        # 更新統計信息
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000
        
        self.rerank_stats["total_queries"] += 1
        self.rerank_stats["total_candidates_input"] += len(candidates)
        self.rerank_stats["total_candidates_output"] += len(top_profiles)
        self.rerank_stats["total_time_ms"] += processing_time
        
        # 更新複雜度分佈統計
        for profile in top_profiles:
            if profile.overall_similarity > self.complexity_thresholds["simple"]:
                self.rerank_stats["complexity_distribution"]["simple"] += 1
            elif profile.overall_similarity > self.complexity_thresholds["medium"]:
                self.rerank_stats["complexity_distribution"]["medium"] += 1
            else:
                self.rerank_stats["complexity_distribution"]["complex"] += 1
        
        # 緩存結果
        if self.cache_enabled:
            self.result_cache[cache_key] = top_profiles
        
        result_words = [profile.word for profile in top_profiles]
        
        self.logger.debug(f"L3 Rerank: {query} → {len(candidates)} to {len(result_words)} "
                         f"({processing_time:.1f}ms)")
        
        return result_words
    
    def _build_phonetic_profile(self, word: str) -> WordPhoneticProfile:
        """構建詞彙的完整語音特徵檔案"""
        profile = WordPhoneticProfile(word=word)
        
        for char in word:
            char_features = CompletePhoneticFeatures(character=char)
            
            # 提取各維度特徵
            char_features.consonant_features = self.consonant_classifier.extract_phonetic_features(char)
            char_features.finals_features = self.finals_analyzer.extract_finals_features(char)
            char_features.tone_features = self.tone_analyzer.extract_tone_features(char)
            
            profile.character_features.append(char_features)
        
        return profile
    
    def _calculate_word_similarity(self, query_profile: WordPhoneticProfile, 
                                  candidate_profile: WordPhoneticProfile) -> float:
        """計算詞彙間的綜合語音相似度"""
        if not query_profile.character_features or not candidate_profile.character_features:
            return 0.0
        
        query_len = len(query_profile.character_features)
        candidate_len = len(candidate_profile.character_features)
        
        # 使用動態規劃處理異長度詞彙對比
        similarity_matrix = self._build_similarity_matrix(
            query_profile.character_features,
            candidate_profile.character_features
        )
        
        # 計算最佳對齊相似度
        optimal_similarity = self._find_optimal_alignment(similarity_matrix, query_len, candidate_len)
        
        # 長度懲罰
        length_penalty = self._calculate_length_penalty(query_len, candidate_len)
        
        return optimal_similarity * length_penalty
    
    def _build_similarity_matrix(self, query_chars: List[CompletePhoneticFeatures],
                               candidate_chars: List[CompletePhoneticFeatures]) -> List[List[float]]:
        """建立字符間相似度矩陣"""
        query_len = len(query_chars)
        candidate_len = len(candidate_chars)
        
        matrix = [[0.0] * candidate_len for _ in range(query_len)]
        
        for i in range(query_len):
            for j in range(candidate_len):
                matrix[i][j] = self._calculate_character_similarity(query_chars[i], candidate_chars[j])
        
        return matrix
    
    def _calculate_character_similarity(self, query_char: CompletePhoneticFeatures,
                                      candidate_char: CompletePhoneticFeatures) -> float:
        """計算單字間的完整語音相似度"""
        if query_char.character == candidate_char.character:
            return 1.0
        
        # 聲母相似度
        consonant_sim = self.consonant_classifier.calculate_consonant_similarity(
            query_char.consonant_features.consonant or "",
            candidate_char.consonant_features.consonant or ""
        )
        
        # 韻母相似度
        finals_sim = self.finals_analyzer.calculate_finals_similarity(
            query_char.finals_features.finals,
            candidate_char.finals_features.finals
        )
        
        # 聲調相似度
        tone_sim = self.tone_analyzer.calculate_tone_similarity(
            query_char.tone_features.tone,
            candidate_char.tone_features.tone
        )
        
        # 加權組合
        total_similarity = (
            consonant_sim * self.feature_weights["consonant"] +
            finals_sim * self.feature_weights["finals"] +
            tone_sim * self.feature_weights["tone"]
        )
        
        return total_similarity
    
    def _find_optimal_alignment(self, similarity_matrix: List[List[float]], 
                              query_len: int, candidate_len: int) -> float:
        """找到最佳對齊方案的相似度"""
        if not similarity_matrix or query_len == 0 or candidate_len == 0:
            return 0.0
        
        # 動態規劃找最佳對齊
        dp = [[0.0] * (candidate_len + 1) for _ in range(query_len + 1)]
        
        for i in range(1, query_len + 1):
            for j in range(1, candidate_len + 1):
                # 匹配得分
                match_score = similarity_matrix[i-1][j-1]
                
                # 三種操作
                match = dp[i-1][j-1] + match_score
                delete = dp[i-1][j] * 0.8  # 刪除懲罰
                insert = dp[i][j-1] * 0.8  # 插入懲罰
                
                dp[i][j] = max(match, delete, insert)
        
        # 標準化分數
        max_possible = max(query_len, candidate_len)
        return dp[query_len][candidate_len] / max_possible
    
    def _calculate_length_penalty(self, len1: int, len2: int) -> float:
        """計算長度差異懲罰"""
        len_diff = abs(len1 - len2)
        
        if len_diff == 0:
            return 1.0
        elif len_diff == 1:
            return 0.92
        elif len_diff == 2:
            return 0.8
        elif len_diff == 3:
            return 0.65
        else:
            return 0.5
    
    def _assess_complexity(self, query_profile: WordPhoneticProfile,
                          candidate_profile: WordPhoneticProfile) -> float:
        """評估語音變異複雜度"""
        # 基於多個因子評估複雜度
        complexity_factors = []
        
        # 1. 整體相似度 (越低越複雜)
        overall_sim = candidate_profile.overall_similarity
        complexity_factors.append(1.0 - overall_sim)
        
        # 2. 長度差異復雜度
        len_diff = abs(len(query_profile.word) - len(candidate_profile.word))
        length_complexity = min(len_diff * 0.2, 1.0)
        complexity_factors.append(length_complexity)
        
        # 3. 特徵維度不一致數
        feature_mismatches = 0
        total_comparisons = 0
        
        min_len = min(len(query_profile.character_features), 
                     len(candidate_profile.character_features))
        
        for i in range(min_len):
            q_char = query_profile.character_features[i]
            c_char = candidate_profile.character_features[i]
            
            # 檢查各維度是否匹配
            if q_char.consonant_features.consonant != c_char.consonant_features.consonant:
                feature_mismatches += 1
            if q_char.finals_features.finals != c_char.finals_features.finals:
                feature_mismatches += 1
            if q_char.tone_features.tone != c_char.tone_features.tone:
                feature_mismatches += 1
            
            total_comparisons += 3
        
        if total_comparisons > 0:
            feature_complexity = feature_mismatches / total_comparisons
            complexity_factors.append(feature_complexity)
        
        # 綜合複雜度評分
        return sum(complexity_factors) / len(complexity_factors)
    
    def _log_training_data(self, query_profile: WordPhoneticProfile,
                          all_candidates: List[WordPhoneticProfile],
                          selected_candidates: List[WordPhoneticProfile]):
        """記錄機器學習訓練數據"""
        if not self.enable_data_logging:
            return
        
        training_entry = {
            "timestamp": time.time(),
            "query": query_profile.word,
            "query_features": self._serialize_profile(query_profile),
            "total_candidates": len(all_candidates),
            "selected_count": len(selected_candidates),
            "candidates": [
                {
                    "word": profile.word,
                    "features": self._serialize_profile(profile),
                    "similarity": profile.overall_similarity,
                    "complexity": profile.complexity_score,
                    "rank": i + 1,
                    "selected": profile in selected_candidates
                }
                for i, profile in enumerate(all_candidates[:100])  # 限制記錄數量
            ]
        }
        
        self.training_data.append(training_entry)
    
    def _serialize_profile(self, profile: WordPhoneticProfile) -> Dict[str, Any]:
        """序列化語音特徵檔案供數據記錄"""
        return {
            "word": profile.word,
            "length": profile.word_length,
            "characters": [
                {
                    "char": char.character,
                    "consonant": char.consonant_features.consonant if char.consonant_features else "",
                    "consonant_group": char.consonant_features.consonant_group if char.consonant_features else "",
                    "finals": char.finals_features.finals if char.finals_features else "",
                    "finals_group": char.finals_features.finals_group if char.finals_features else "",
                    "tone": char.tone_features.tone if char.tone_features else 0,
                    "tone_name": char.tone_features.tone_name if char.tone_features else ""
                }
                for char in profile.character_features
            ]
        }
    
    def batch_rerank(self, queries: List[str], 
                    candidates_lists: List[List[str]], 
                    top_k: int = 50) -> Dict[str, List[str]]:
        """批量執行L3精排"""
        results = {}
        
        for query, candidates in zip(queries, candidates_lists):
            results[query] = self.rerank(query, candidates, top_k)
        
        return results
    
    def get_rerank_statistics(self) -> Dict[str, Any]:
        """獲取精排器性能統計"""
        stats = self.rerank_stats.copy()
        
        if stats["total_queries"] > 0:
            stats["avg_input_candidates"] = stats["total_candidates_input"] / stats["total_queries"]
            stats["avg_output_candidates"] = stats["total_candidates_output"] / stats["total_queries"]
            stats["avg_processing_time_ms"] = stats["total_time_ms"] / stats["total_queries"]
            stats["avg_reduction_ratio"] = (stats["total_candidates_output"] / 
                                          max(stats["total_candidates_input"], 1))
            stats["cache_hit_rate"] = stats["cache_hits"] / stats["total_queries"]
        
        # 複雜度分佈百分比
        total_cases = sum(stats["complexity_distribution"].values())
        if total_cases > 0:
            stats["complexity_percentages"] = {
                level: count / total_cases 
                for level, count in stats["complexity_distribution"].items()
            }
        
        stats["cache_size"] = len(self.result_cache)
        stats["training_data_size"] = len(self.training_data) if self.training_data else 0
        
        return stats
    
    def get_training_data(self) -> List[Dict[str, Any]]:
        """獲取訓練數據記錄"""
        return self.training_data.copy() if self.training_data else []
    
    def clear_cache(self):
        """清除緩存"""
        self.result_cache.clear()
        self.logger.info("L3 reranker cache cleared")
    
    def save_training_data(self, filepath: str):
        """保存訓練數據到文件"""
        if not self.training_data:
            self.logger.warning("No training data to save")
            return
        
        import json
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.training_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved {len(self.training_data)} training entries to {filepath}")


def test_l3_full_phonetic_reranker():
    """測試FullPhoneticReranker功能"""
    print("🧪 測試FullPhoneticReranker功能")
    print("=" * 50)
    
    try:
        # 初始化依賴組件
        dict_manager = SuperDictionaryManager(
            super_dict_path="data/super_dicts/super_dict_combined.json",
            super_dict_reversed_path="data/super_dicts/super_dict_reversed.json"
        )
        
        consonant_classifier = PhoneticClassifier()
        finals_analyzer = FinalsAnalyzer()
        tone_analyzer = ToneAnalyzer()
        
        l3_reranker = FullPhoneticReranker(
            dict_manager, consonant_classifier, finals_analyzer, tone_analyzer
        )
        
        # 測試案例
        test_cases = [
            ("知道", ["知道", "資道", "指導", "制導", "智慧", "吃飯", "睡覺", "來了", "電腦", "手機"] * 10),  # 100候選
            ("吃飯", ["吃飯", "次飯", "吃完", "次完", "飯菜", "知道", "睡覺", "工作", "安全", "電腦"] * 10),
        ]
        
        print("📊 L3精排測試:")
        print("-" * 40)
        
        for query, candidates in test_cases:
            print(f"\n查詢: '{query}'")
            print(f"輸入候選: {len(candidates)} 個")
            
            # 精排
            start_time = time.time()
            reranked = l3_reranker.rerank(query, candidates, top_k=10)
            processing_time = (time.time() - start_time) * 1000
            
            print(f"精排結果: {len(reranked)} 個")
            print(f"處理時間: {processing_time:.1f}ms")
            print(f"前5個: {reranked[:5]}")
            
            # 複雜度分析
            stats = l3_reranker.get_rerank_statistics()
            if "complexity_percentages" in stats:
                comp_perc = stats["complexity_percentages"]
                print(f"複雜度分佈: 簡單={comp_perc.get('simple', 0):.1%}, "
                      f"中等={comp_perc.get('medium', 0):.1%}, "
                      f"複雜={comp_perc.get('complex', 0):.1%}")
        
        # 性能統計
        print("\n📊 L3精排器統計:")
        print("-" * 40)
        
        final_stats = l3_reranker.get_rerank_statistics()
        print(f"總查詢數: {final_stats['total_queries']}")
        print(f"平均輸入候選數: {final_stats.get('avg_input_candidates', 0):.0f}")
        print(f"平均輸出候選數: {final_stats.get('avg_output_candidates', 0):.0f}")
        print(f"平均處理時間: {final_stats.get('avg_processing_time_ms', 0):.2f}ms")
        print(f"緩存命中率: {final_stats.get('cache_hit_rate', 0):.1%}")
        print(f"訓練數據條目: {final_stats['training_data_size']}")
        
        # 驗收標準檢查
        print("\n📊 L3精排器驗收標準檢查:")
        print("-" * 40)
        
        avg_time = final_stats.get('avg_processing_time_ms', 0)
        avg_output = final_stats.get('avg_output_candidates', 0)
        
        print(f"✓ 平均處理時間: {avg_time:.1f}ms "
              f"{'< 100ms ✅' if avg_time < 100 else '>= 100ms ❌'}")
        print(f"✓ 輸出候選數: {avg_output:.0f} 個 "
              f"{'≤50 ✅' if avg_output <= 50 else '>50 ❌'}")
        
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
    success = test_l3_full_phonetic_reranker()
    print(f"\n測試 {'✅ PASSED' if success else '❌ FAILED'}")
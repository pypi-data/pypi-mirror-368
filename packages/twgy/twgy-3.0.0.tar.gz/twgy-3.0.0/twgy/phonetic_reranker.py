"""
PhoneticReranker - 語音重排系統主API
整合17萬詞典的完整中文語音錯誤修正介面，提供ASR後處理服務
"""

import time
import logging
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass

from .core.phonetic_classifier import PhoneticClassifier
from .analyzers.finals_analyzer import FinalsAnalyzer
from .analyzers.tone_analyzer import ToneAnalyzer
from .data.super_dictionary_manager import SuperDictionaryManager
from .filters.l1_consonant_filter import FirstConsonantFilter
from .filters.l2_first_last_reranker import FirstLastSimilarityReranker
from .filters.l3_full_phonetic_reranker import FullPhoneticReranker
from .data.training_data_logger import TrainingDataLogger
from .rerankers.dimsim_reranker import DimSimReranker, DimSimConfig


@dataclass
class RerankerConfig:
    """語音重排器配置"""
    # 數據路徑
    dict_path: str = "data/super_dicts/super_dict_combined.json"
    dict_reversed_path: str = "data/super_dicts/super_dict_reversed.json"
    
    # L1配置
    l1_use_full_dict: bool = True
    l1_enable_cache: bool = True
    
    # L2配置
    l2_top_k: int = 500
    l2_enable_cache: bool = True
    
    # L3配置  
    l3_top_k: int = 50
    l3_enable_cache: bool = True
    
    # 訓練數據記錄
    enable_training_data_logging: bool = False
    training_data_dir: str = "data/training_logs"
    training_db_name: str = "phonetic_reranker.db"
    
    # 性能配置
    max_processing_time_ms: float = 250.0
    enable_performance_monitoring: bool = True
    
    # DimSim配置
    enable_dimsim: bool = True
    dimsim_weight: float = 0.3  # DimSim分數權重 (0.0-1.0)
    dimsim_stage: str = "L2"    # 應用階段: L2|L3
    dimsim_max_candidates: int = 200
    dimsim_cache_size: int = 1000


@dataclass
class RerankerResult:
    """重排結果結構"""
    query: str = ""
    candidates: List[str] = None
    processing_time_ms: float = 0.0
    
    # 詳細信息
    l1_candidates_count: int = 0
    l2_candidates_count: int = 0  
    l3_candidates_count: int = 0
    dimsim_candidates_count: int = 0
    l1_time_ms: float = 0.0
    l2_time_ms: float = 0.0
    l3_time_ms: float = 0.0
    dimsim_time_ms: float = 0.0
    
    # 質量評估
    complexity_level: str = ""
    confidence_score: float = 0.0
    
    # 錯誤信息
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.candidates is None:
            self.candidates = []


class PhoneticReranker:
    """
    中文語音重排系統主API
    
    功能：
    1. 整合L1+L2+L3三層語音篩選與重排架構
    2. 支援ASR錯誤修正的批量處理
    3. 提供語音相似度計算和候選詞推薦
    4. 自動數據收集供機器學習模型訓練
    5. 高性能處理：<250ms響應，支援並發查詢
    
    使用場景：
    - ASR系統後處理語音錯誤修正
    - 中文輸入法候選詞推薦
    - 語音相似詞搜索和匹配
    - 中文語音學研究數據收集
    """
    
    def __init__(self, config: Optional[RerankerConfig] = None):
        """
        初始化語音重排系統
        
        Args:
            config: 重排器配置，使用默認配置如果為None
        """
        self.config = config or RerankerConfig()
        self.logger = logging.getLogger(__name__)
        
        # 初始化狀態
        self._initialized = False
        self._initialization_error = None
        
        # 性能監控
        self.performance_stats = {
            "total_queries": 0,
            "total_processing_time": 0.0,
            "avg_processing_time": 0.0,
            "successful_queries": 0,
            "error_queries": 0,
            "timeout_queries": 0
        }
        
        try:
            self._initialize_components()
            self._initialized = True
            self.logger.info("PhoneticReranker initialized successfully")
        except Exception as e:
            self._initialization_error = str(e)
            self.logger.error(f"PhoneticReranker initialization failed: {e}")
            raise
    
    def _initialize_components(self):
        """初始化所有核心組件"""
        self.logger.info("Initializing PhoneticReranker components...")
        
        # 初始化數據管理器
        self.dict_manager = SuperDictionaryManager(
            super_dict_path=self.config.dict_path,
            super_dict_reversed_path=self.config.dict_reversed_path
        )
        
        # 初始化語音分析器
        self.phonetic_classifier = PhoneticClassifier()
        self.finals_analyzer = FinalsAnalyzer()
        self.tone_analyzer = ToneAnalyzer()
        
        # 初始化三層篩選器
        self.l1_filter = FirstConsonantFilter(
            self.dict_manager, 
            self.phonetic_classifier
        )
        
        self.l2_reranker = FirstLastSimilarityReranker(
            self.dict_manager,
            self.phonetic_classifier,
            self.finals_analyzer
        )
        
        self.l3_reranker = FullPhoneticReranker(
            self.dict_manager,
            self.phonetic_classifier,
            self.finals_analyzer,
            self.tone_analyzer,
            enable_data_logging=False  # 由主API控制
        )
        
        # 初始化DimSim重排序器
        if self.config.enable_dimsim:
            dimsim_config = DimSimConfig(
                enable_dimsim=True,
                dimsim_weight=self.config.dimsim_weight,
                max_candidates=self.config.dimsim_max_candidates,
                cache_size=self.config.dimsim_cache_size
            )
            self.dimsim_reranker = DimSimReranker(dimsim_config)
        else:
            self.dimsim_reranker = None
        
        # 初始化訓練數據記錄器
        if self.config.enable_training_data_logging:
            self.training_logger = TrainingDataLogger(
                data_dir=self.config.training_data_dir,
                db_name=self.config.training_db_name
            )
        else:
            self.training_logger = None
        
        self.logger.info(f"Components initialized with {self.dict_manager.total_entries:,} dictionary entries")
    
    def rerank(self, query: str, max_candidates: Optional[int] = None) -> RerankerResult:
        """
        執行語音重排 - 主要API方法
        
        Args:
            query: 查詢詞彙
            max_candidates: 最大返回候選數（默認使用配置值）
            
        Returns:
            RerankerResult: 完整的重排結果
        """
        if not self._initialized:
            return RerankerResult(
                query=query,
                error=f"Reranker not initialized: {self._initialization_error}"
            )
        
        start_time = time.time()
        max_candidates = max_candidates or self.config.l3_top_k
        
        try:
            # 執行三層重排管道
            result = self._execute_pipeline(query, max_candidates)
            
            # 更新性能統計
            self.performance_stats["successful_queries"] += 1
            
            return result
            
        except Exception as e:
            # 處理錯誤
            processing_time = (time.time() - start_time) * 1000
            self.performance_stats["error_queries"] += 1
            
            error_result = RerankerResult(
                query=query,
                processing_time_ms=processing_time,
                error=str(e)
            )
            
            self.logger.error(f"Rerank failed for '{query}': {e}")
            return error_result
        
        finally:
            # 更新總體統計
            total_time = (time.time() - start_time) * 1000
            self.performance_stats["total_queries"] += 1
            self.performance_stats["total_processing_time"] += total_time
            self.performance_stats["avg_processing_time"] = (
                self.performance_stats["total_processing_time"] / 
                self.performance_stats["total_queries"]
            )
            
            # 檢查超時
            if total_time > self.config.max_processing_time_ms:
                self.performance_stats["timeout_queries"] += 1
                self.logger.warning(f"Query '{query}' exceeded timeout: {total_time:.1f}ms")
    
    def _execute_pipeline(self, query: str, max_candidates: int) -> RerankerResult:
        """執行完整的三層重排管道"""
        pipeline_start = time.time()
        
        # Phase 1: L1聲母篩選
        l1_start = time.time()
        l1_candidates = self.l1_filter.filter(
            query, 
            use_full_dict=self.config.l1_use_full_dict,
            enable_cache=self.config.l1_enable_cache
        )
        l1_time = (time.time() - l1_start) * 1000
        
        # Phase 2: L2首尾字重排
        l2_start = time.time() 
        l2_candidates = self.l2_reranker.rerank(query, l1_candidates, self.config.l2_top_k)
        l2_time = (time.time() - l2_start) * 1000
        
        # Phase 2.5: DimSim重排序 (如果在L2階段啟用)
        dimsim_time = 0.0
        dimsim_candidates_count = 0
        if self.config.enable_dimsim and self.config.dimsim_stage == "L2":
            dimsim_start = time.time()
            dimsim_results = self.dimsim_reranker.rerank(query, l2_candidates)
            l2_candidates = [result.text for result in dimsim_results]
            dimsim_time = (time.time() - dimsim_start) * 1000
            dimsim_candidates_count = len(dimsim_results)
            self.logger.debug(f"DimSim reranked {dimsim_candidates_count} candidates at L2 stage in {dimsim_time:.1f}ms")
        
        # Phase 3: L3完整語音精排
        l3_start = time.time()
        l3_candidates = self.l3_reranker.rerank(query, l2_candidates, max_candidates)
        l3_time = (time.time() - l3_start) * 1000
        
        # Phase 3.5: DimSim重排序 (如果在L3階段啟用)
        if self.config.enable_dimsim and self.config.dimsim_stage == "L3":
            dimsim_start = time.time()
            dimsim_results = self.dimsim_reranker.rerank(query, l3_candidates)
            l3_candidates = [result.text for result in dimsim_results]
            dimsim_time = (time.time() - dimsim_start) * 1000
            dimsim_candidates_count = len(dimsim_results)
            self.logger.debug(f"DimSim reranked {dimsim_candidates_count} candidates at L3 stage in {dimsim_time:.1f}ms")
        
        pipeline_time = (time.time() - pipeline_start) * 1000
        
        # 評估複雜度和信心分數
        complexity_level = self._assess_complexity(len(l1_candidates), len(l2_candidates), len(l3_candidates))
        confidence_score = self._calculate_confidence(l3_candidates, query, pipeline_time)
        
        # 構建結果
        result = RerankerResult(
            query=query,
            candidates=l3_candidates,
            processing_time_ms=pipeline_time,
            
            l1_candidates_count=len(l1_candidates),
            l2_candidates_count=len(l2_candidates),
            l3_candidates_count=len(l3_candidates),
            dimsim_candidates_count=dimsim_candidates_count,
            l1_time_ms=l1_time,
            l2_time_ms=l2_time,  
            l3_time_ms=l3_time,
            dimsim_time_ms=dimsim_time,
            
            complexity_level=complexity_level,
            confidence_score=confidence_score
        )
        
        # 記錄訓練數據
        if self.training_logger:
            self._log_training_data(query, result)
        
        return result
    
    def _assess_complexity(self, l1_count: int, l2_count: int, l3_count: int) -> str:
        """評估查詢複雜度"""
        if l1_count < 1000 and l2_count < 100:
            return "simple"
        elif l1_count < 10000 and l2_count < 300:
            return "medium"
        else:
            return "complex"
    
    def _calculate_confidence(self, candidates: List[str], query: str, processing_time: float) -> float:
        """計算結果信心分數 (0-1)"""
        confidence_factors = []
        
        # 候選數量因子
        if len(candidates) >= 10:
            confidence_factors.append(0.8)
        elif len(candidates) >= 5:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.4)
        
        # 完全匹配因子
        if query in candidates:
            exact_match_bonus = 0.2
            if candidates[0] == query:
                exact_match_bonus = 0.3  # 頂部匹配更好
            confidence_factors.append(exact_match_bonus)
        
        # 處理時間因子（越快越有信心）
        if processing_time < 100:
            confidence_factors.append(0.1)
        elif processing_time > 500:
            confidence_factors.append(-0.1)  # 懲罰太慢的查詢
        
        return min(max(sum(confidence_factors), 0.0), 1.0)
    
    def _log_training_data(self, query: str, result: RerankerResult):
        """記錄訓練數據"""
        try:
            l1_result = {
                "candidates_count": result.l1_candidates_count,
                "processing_time_ms": result.l1_time_ms
            }
            
            l2_result = {
                "candidates_count": result.l2_candidates_count,
                "processing_time_ms": result.l2_time_ms
            }
            
            l3_result = {
                "candidates_count": result.l3_candidates_count,
                "processing_time_ms": result.l3_time_ms,
                "top_candidates": result.candidates,
                "complexity_level": result.complexity_level,
                "complexity_score": 1.0 - result.confidence_score  # 轉換為複雜度分數
            }
            
            phonetic_features = {
                "query_length": len(query),
                "total_time_ms": result.processing_time_ms,
                "confidence_score": result.confidence_score
            }
            
            self.training_logger.log_training_case(
                query, l1_result, l2_result, l3_result, phonetic_features
            )
        except Exception as e:
            self.logger.warning(f"Training data logging failed: {e}")
    
    def batch_rerank(self, queries: List[str], 
                    max_candidates: Optional[int] = None) -> List[RerankerResult]:
        """
        批量執行語音重排
        
        Args:
            queries: 查詢詞彙列表
            max_candidates: 每個查詢的最大候選數
            
        Returns:
            重排結果列表
        """
        results = []
        for query in queries:
            result = self.rerank(query, max_candidates)
            results.append(result)
        return results
    
    def get_similar_words(self, word: str, 
                         similarity_threshold: float = 0.6,
                         max_results: int = 20) -> List[Dict[str, Any]]:
        """
        獲取語音相似詞列表
        
        Args:
            word: 目標詞彙
            similarity_threshold: 相似度閾值
            max_results: 最大結果數
            
        Returns:
            相似詞列表，包含相似度分數
        """
        result = self.rerank(word, max_candidates=max_results * 2)
        
        if result.error:
            return []
        
        # 簡化實現：基於重排結果估算相似度
        similar_words = []
        for i, candidate in enumerate(result.candidates[:max_results]):
            if candidate != word:
                # 基於排名估算相似度分數
                estimated_similarity = max(0.9 - (i * 0.05), similarity_threshold)
                if estimated_similarity >= similarity_threshold:
                    similar_words.append({
                        "word": candidate,
                        "similarity": estimated_similarity,
                        "rank": i + 1
                    })
        
        return similar_words
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取系統統計信息"""
        stats = {
            "system_info": {
                "initialized": self._initialized,
                "dictionary_size": self.dict_manager.total_entries if self._initialized else 0,
                "config": {
                    "l1_use_full_dict": self.config.l1_use_full_dict,
                    "l2_top_k": self.config.l2_top_k,
                    "l3_top_k": self.config.l3_top_k,
                    "training_data_logging": self.config.enable_training_data_logging,
                    "max_processing_time_ms": self.config.max_processing_time_ms
                }
            },
            "performance": self.performance_stats.copy()
        }
        
        if self._initialized:
            # 組件統計
            stats["components"] = {
                "l1_filter": self.l1_filter.get_filter_statistics(),
                "l2_reranker": self.l2_reranker.get_rerank_statistics(),
                "l3_reranker": self.l3_reranker.get_rerank_statistics()
            }
            
            # 訓練數據統計
            if self.training_logger:
                stats["training_data"] = self.training_logger.get_statistics()
        
        return stats
    
    def clear_caches(self):
        """清除所有緩存"""
        if self._initialized:
            self.l1_filter.clear_cache()
            self.l2_reranker.clear_cache()
            self.l3_reranker.clear_cache()
            self.logger.info("All caches cleared")
    
    def finalize_session(self):
        """結束當前會話（主要用於訓練數據記錄）"""
        if self.training_logger:
            return self.training_logger.finalize_session()
        return None


def test_phonetic_reranker_api():
    """測試PhoneticReranker主API"""
    print("🧪 測試PhoneticReranker主API")
    print("=" * 60)
    
    try:
        # 初始化重排器
        config = RerankerConfig(
            l3_top_k=10,
            enable_training_data_logging=True,
            max_processing_time_ms=300.0
        )
        
        reranker = PhoneticReranker(config)
        
        # 測試案例
        test_queries = [
            "知道", "資道", "吃飯", "安全", "來了",
            "電腦", "手機", "這樣", "醬瓜", "收集"
        ]
        
        print("📊 單查詢API測試:")
        print("-" * 50)
        
        for query in test_queries[:3]:
            result = reranker.rerank(query)
            
            print(f"\n查詢: '{result.query}'")
            if result.error:
                print(f"  錯誤: {result.error}")
                continue
                
            print(f"  處理時間: {result.processing_time_ms:.1f}ms")
            print(f"  管道流程: {result.l1_candidates_count} → {result.l2_candidates_count} → {result.l3_candidates_count}")
            print(f"  複雜度: {result.complexity_level}")
            print(f"  信心分數: {result.confidence_score:.2f}")
            print(f"  候選結果: {result.candidates[:5]}")
        
        # 批量處理測試
        print(f"\n📊 批量API測試:")
        print("-" * 50)
        
        batch_results = reranker.batch_rerank(test_queries)
        successful_results = [r for r in batch_results if not r.error]
        
        print(f"批量處理結果:")
        print(f"  總查詢數: {len(batch_results)}")
        print(f"  成功數: {len(successful_results)}")
        print(f"  平均處理時間: {sum(r.processing_time_ms for r in successful_results) / len(successful_results):.1f}ms")
        
        # 相似詞測試
        print(f"\n📊 相似詞API測試:")
        print("-" * 50)
        
        similar_words = reranker.get_similar_words("知道", similarity_threshold=0.7, max_results=5)
        print(f"與'知道'相似的詞:")
        for sim_word in similar_words:
            print(f"  {sim_word['word']}: {sim_word['similarity']:.2f}")
        
        # 統計信息測試
        print(f"\n📊 系統統計:")
        print("-" * 50)
        
        stats = reranker.get_statistics()
        system_info = stats["system_info"]
        performance = stats["performance"]
        
        print(f"系統狀態:")
        print(f"  初始化: {system_info['initialized']}")
        print(f"  詞典大小: {system_info['dictionary_size']:,}")
        print(f"  L3輸出數: {system_info['config']['l3_top_k']}")
        
        print(f"\n性能統計:")
        print(f"  總查詢數: {performance['total_queries']}")
        print(f"  成功查詢: {performance['successful_queries']}")
        print(f"  平均時間: {performance['avg_processing_time']:.1f}ms")
        print(f"  錯誤查詢: {performance['error_queries']}")
        print(f"  超時查詢: {performance['timeout_queries']}")
        
        # 結束會話
        session_summary = reranker.finalize_session()
        if session_summary:
            print(f"\n會話結束: {session_summary.session_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ API測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 執行API測試
    success = test_phonetic_reranker_api()
    print(f"\nAPI測試 {'✅ PASSED' if success else '❌ FAILED'}")
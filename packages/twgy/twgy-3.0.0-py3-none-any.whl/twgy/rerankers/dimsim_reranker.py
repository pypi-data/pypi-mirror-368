"""
DimSim重排序器
使用DimSim庫進行語音相似度計算和候選重排序
"""

import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

try:
    import dimsim
    DIMSIM_AVAILABLE = True
except ImportError:
    DIMSIM_AVAILABLE = False
    logging.warning("DimSim not available. Install with: pip install dimsim")

from core.exceptions import TWGYError, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class DimSimCandidate:
    """DimSim重排序後的候選結果"""
    text: str
    original_score: float
    dimsim_similarity: float
    dimsim_distance: float
    final_score: float
    rank: int


@dataclass 
class DimSimConfig:
    """DimSim重排序器配置"""
    enable_dimsim: bool = True
    dimsim_weight: float = 0.3  # DimSim分數權重 (0.0-1.0)
    original_weight: float = 0.7  # 原始分數權重
    max_candidates: int = 200  # 最大處理候選數量
    min_similarity_threshold: float = 0.0  # 最小相似度閾值
    enable_caching: bool = True
    cache_size: int = 1000


class DimSimReranker:
    """
    DimSim重排序器
    
    使用DimSim計算語音相似度，與原有分數融合後重新排序
    """
    
    def __init__(self, config: DimSimConfig = None):
        """
        初始化DimSim重排序器
        
        Args:
            config: DimSim配置
        """
        self.config = config or DimSimConfig()
        self.available = DIMSIM_AVAILABLE
        
        # 性能統計
        self.query_count = 0
        self.total_processing_time = 0.0
        self.total_similarity_calculations = 0
        
        # 簡單緩存
        self.similarity_cache: Dict[Tuple[str, str], float] = {}
        
        if not self.available:
            logger.warning("DimSim not available - reranker will pass through without modification")
        else:
            logger.info(f"DimSim reranker initialized with weight={self.config.dimsim_weight}")
    
    def rerank(
        self, 
        query: str, 
        candidates: List[str],
        original_scores: Optional[List[float]] = None
    ) -> List[DimSimCandidate]:
        """
        使用DimSim重新排序候選列表
        
        Args:
            query: 查詢字符串
            candidates: 候選字符串列表
            original_scores: 原始分數列表（可選）
            
        Returns:
            重排序後的候選列表
        """
        if not self.available or not self.config.enable_dimsim:
            # DimSim不可用時，返回原始順序
            return self._create_passthrough_results(candidates, original_scores)
        
        if not candidates:
            return []
        
        start_time = time.time()
        
        try:
            # 限制處理數量
            process_candidates = candidates[:self.config.max_candidates]
            process_scores = (original_scores[:self.config.max_candidates] 
                            if original_scores else [1.0] * len(process_candidates))
            
            # 計算DimSim相似度
            dimsim_results = self._calculate_dimsim_similarities(query, process_candidates)
            
            # 融合分數並排序
            final_results = self._merge_and_rank(
                process_candidates, 
                process_scores, 
                dimsim_results
            )
            
            # 更新統計
            processing_time = (time.time() - start_time) * 1000
            self._update_stats(processing_time, len(process_candidates))
            
            logger.debug(f"DimSim reranked {len(process_candidates)} candidates in {processing_time:.1f}ms")
            
            return final_results
            
        except Exception as e:
            logger.error(f"DimSim reranking failed: {e}")
            # 失敗時返回原始結果
            return self._create_passthrough_results(candidates, original_scores)
    
    def _calculate_dimsim_similarities(
        self, 
        query: str, 
        candidates: List[str]
    ) -> List[Tuple[float, float]]:
        """
        計算DimSim相似度
        
        Args:
            query: 查詢字符串
            candidates: 候選字符串列表
            
        Returns:
            (相似度, 距離) 列表
        """
        results = []
        
        for candidate in candidates:
            # 檢查緩存
            cache_key = (query, candidate)
            if self.config.enable_caching and cache_key in self.similarity_cache:
                similarity = self.similarity_cache[cache_key]
                distance = 1.0 / similarity - 1.0 if similarity > 0 else float('inf')
            else:
                try:
                    # 計算DimSim距離
                    if len(query) != len(candidate):
                        # DimSim要求長度相同，對不同長度的字符串給予懲罰
                        distance = float('inf')
                        similarity = 0.0
                    else:
                        distance = dimsim.get_distance(query, candidate)
                        similarity = 1.0 / (1.0 + distance) if distance >= 0 else 0.0
                    
                    # 緩存結果
                    if self.config.enable_caching:
                        self._update_cache(cache_key, similarity)
                        
                except Exception as e:
                    logger.debug(f"DimSim calculation failed for {query}-{candidate}: {e}")
                    distance = float('inf')
                    similarity = 0.0
            
            results.append((similarity, distance))
            self.total_similarity_calculations += 1
        
        return results
    
    def _merge_and_rank(
        self,
        candidates: List[str],
        original_scores: List[float], 
        dimsim_results: List[Tuple[float, float]]
    ) -> List[DimSimCandidate]:
        """
        融合原始分數和DimSim分數，重新排序
        
        Args:
            candidates: 候選列表
            original_scores: 原始分數
            dimsim_results: DimSim結果 (相似度, 距離)
            
        Returns:
            排序後的結果列表
        """
        merged_results = []
        
        for i, (candidate, original_score) in enumerate(zip(candidates, original_scores)):
            dimsim_similarity, dimsim_distance = dimsim_results[i]
            
            # 跳過低相似度結果
            if dimsim_similarity < self.config.min_similarity_threshold:
                continue
            
            # 標準化原始分數 (假設原始分數越高越好)
            normalized_original = min(1.0, max(0.0, original_score))
            
            # 加權融合
            final_score = (
                self.config.original_weight * normalized_original +
                self.config.dimsim_weight * dimsim_similarity
            )
            
            merged_results.append(DimSimCandidate(
                text=candidate,
                original_score=original_score,
                dimsim_similarity=dimsim_similarity,
                dimsim_distance=dimsim_distance,
                final_score=final_score,
                rank=0  # 稍後設置
            ))
        
        # 按最終分數排序
        merged_results.sort(key=lambda x: x.final_score, reverse=True)
        
        # 設置排名
        for rank, result in enumerate(merged_results, 1):
            result.rank = rank
        
        return merged_results
    
    def _create_passthrough_results(
        self, 
        candidates: List[str], 
        original_scores: Optional[List[float]]
    ) -> List[DimSimCandidate]:
        """創建透傳結果（DimSim不可用時）"""
        if not original_scores:
            original_scores = [1.0] * len(candidates)
        
        results = []
        for i, (candidate, score) in enumerate(zip(candidates, original_scores)):
            results.append(DimSimCandidate(
                text=candidate,
                original_score=score,
                dimsim_similarity=0.0,
                dimsim_distance=float('inf'),
                final_score=score,
                rank=i + 1
            ))
        
        return results
    
    def _update_cache(self, key: Tuple[str, str], similarity: float):
        """更新相似度緩存"""
        if len(self.similarity_cache) >= self.config.cache_size:
            # 簡單的LRU：移除最舊的條目
            oldest_key = next(iter(self.similarity_cache))
            del self.similarity_cache[oldest_key]
        
        self.similarity_cache[key] = similarity
    
    def _update_stats(self, processing_time_ms: float, candidate_count: int):
        """更新性能統計"""
        self.query_count += 1
        self.total_processing_time += processing_time_ms
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        if self.query_count == 0:
            return {"status": "no_queries_processed"}
        
        return {
            "available": self.available,
            "total_queries": self.query_count,
            "total_similarity_calculations": self.total_similarity_calculations,
            "avg_processing_time_ms": self.total_processing_time / self.query_count,
            "cache_size": len(self.similarity_cache),
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "config": {
                "dimsim_weight": self.config.dimsim_weight,
                "original_weight": self.config.original_weight,
                "max_candidates": self.config.max_candidates
            }
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """計算緩存命中率"""
        if self.total_similarity_calculations == 0:
            return 0.0
        
        # 簡化的命中率計算
        cache_hits = max(0, self.total_similarity_calculations - len(self.similarity_cache))
        return cache_hits / self.total_similarity_calculations
    
    def clear_cache(self):
        """清除緩存"""
        self.similarity_cache.clear()
        logger.info("DimSim reranker cache cleared")
    
    def is_available(self) -> bool:
        """檢查DimSim是否可用"""
        return self.available and self.config.enable_dimsim
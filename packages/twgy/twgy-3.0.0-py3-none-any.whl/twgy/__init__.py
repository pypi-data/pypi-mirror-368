"""
TWGY - Taiwan Mandarin phonetic Similarity Processor
台灣國語語音相似性處理系統

A comprehensive system for processing Mandarin phonetic similarities,
optimized for Taiwan Mandarin variations including:
- 平翹舌不分 (Retroflex/non-retroflex confusion)
- 前後鼻音不分 (Front/back nasal confusion) 
- 邊鼻音不分 (Lateral/nasal confusion)

Usage:
    >>> from twgy import PhoneticReranker
    >>> reranker = PhoneticReranker()
    >>> result = reranker.rerank("知道")
    >>> print(result.candidates[:5])
    ['知道', '指導', '智道', '志道', '制導']
"""

from .phonetic_reranker import PhoneticReranker, RerankerConfig, RerankerResult
from .core.phonetic_classifier import PhoneticClassifier
from .analyzers.finals_analyzer import FinalsAnalyzer
from .analyzers.tone_analyzer import ToneAnalyzer
from .data.super_dictionary_manager import SuperDictionaryManager

# 版本信息
__version__ = "3.0.0"
__author__ = "TWGY Development Team"
__email__ = "twgy.dev@example.com"
__description__ = "Taiwan Mandarin Phonetic Similarity Processor"

# 公開API
__all__ = [
    # 主要類別
    "PhoneticReranker",
    "RerankerConfig", 
    "RerankerResult",
    
    # 核心組件
    "PhoneticClassifier",
    "FinalsAnalyzer",
    "ToneAnalyzer",
    "SuperDictionaryManager",
    
    # 便利函數
    "quick_rerank",
    "get_similar_words",
    "batch_process",
]

def quick_rerank(word: str, max_candidates: int = 10) -> list:
    """
    快速語音重排 - 便利函數
    
    Args:
        word: 查詢詞彙
        max_candidates: 最大候選數
        
    Returns:
        相似詞列表
        
    Example:
        >>> similar = quick_rerank("知道", 5)
        >>> print(similar)
        ['知道', '指導', '智道', '志道', '制導']
    """
    reranker = PhoneticReranker()
    result = reranker.rerank(word, max_candidates)
    return result.candidates if not result.error else []

def get_similar_words(word: str, threshold: float = 0.6, max_results: int = 20) -> list:
    """
    獲取相似詞 - 便利函數
    
    Args:
        word: 目標詞彙
        threshold: 相似度閾值
        max_results: 最大結果數
        
    Returns:
        相似詞字典列表，包含word和similarity字段
        
    Example:
        >>> similar = get_similar_words("知道")
        >>> for item in similar[:3]:
        ...     print(f"{item['word']}: {item['similarity']:.2f}")
        指導: 0.85
        智道: 0.80
        志道: 0.75
    """
    reranker = PhoneticReranker()
    return reranker.get_similar_words(word, threshold, max_results)

def batch_process(words: list, max_candidates: int = 10) -> list:
    """
    批量處理 - 便利函數
    
    Args:
        words: 詞彙列表
        max_candidates: 每個詞的最大候選數
        
    Returns:
        處理結果列表
        
    Example:
        >>> words = ["知道", "資道", "吃飯"]
        >>> results = batch_process(words)
        >>> for result in results:
        ...     print(f"{result.query}: {len(result.candidates)} candidates")
    """
    reranker = PhoneticReranker()
    return reranker.batch_rerank(words, max_candidates)

# 系統信息
def get_version():
    """獲取版本信息"""
    return __version__

def get_system_info():
    """獲取系統信息"""
    import platform
    import sys
    
    info = {
        "twgy_version": __version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0]
    }
    
    try:
        reranker = PhoneticReranker()
        stats = reranker.get_statistics()
        info.update({
            "dictionary_size": stats["system_info"]["dictionary_size"],
            "initialized": stats["system_info"]["initialized"]
        })
    except Exception as e:
        info["initialization_error"] = str(e)
    
    return info
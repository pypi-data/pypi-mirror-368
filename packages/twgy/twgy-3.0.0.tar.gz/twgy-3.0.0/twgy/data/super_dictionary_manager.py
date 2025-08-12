"""
SuperDictionaryManager - 17萬詞典管理器
管理萌典超級字典資源，建立高效索引系統支援L1/L2層篩選與重排
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import time


class SuperDictionaryManager:
    """
    萌典17萬詞典管理器
    
    功能：
    1. 載入super_dict_combined.json (正序) 和 super_dict_reversed.json (倒序)
    2. 建立首字索引支援L1快速篩選
    3. 建立尾字索引支援L2首尾字相似度計算
    4. 提供O(1)字級查詢和統計功能
    """
    
    def __init__(self, 
                 super_dict_path: str = "data/super_dicts/super_dict_combined.json",
                 super_dict_reversed_path: str = "data/super_dicts/super_dict_reversed.json"):
        """
        初始化超級字典管理器
        
        Args:
            super_dict_path: 正序字典路徑
            super_dict_reversed_path: 倒序字典路徑
        """
        self.logger = logging.getLogger(__name__)
        self.super_dict_path = Path(super_dict_path)
        self.super_dict_reversed_path = Path(super_dict_reversed_path)
        
        # 字典數據
        self.super_dict: List[str] = []
        self.super_dict_reversed: List[str] = []
        
        # 索引系統
        self.first_char_index: Dict[str, List[str]] = defaultdict(list)
        self.last_char_index: Dict[str, List[str]] = defaultdict(list)
        
        # 統計信息
        self.total_entries: int = 0
        self.unique_first_chars: Set[str] = set()
        self.unique_last_chars: Set[str] = set()
        self.load_time: float = 0.0
        
        # 載入字典
        self._load_dictionaries()
        self._build_indexes()
        
        self.logger.info(f"SuperDictionaryManager initialized with {self.total_entries} entries")
    
    def _load_dictionaries(self) -> None:
        """載入正序和倒序字典檔案"""
        start_time = time.time()
        
        try:
            # 載入正序字典
            if not self.super_dict_path.exists():
                raise FileNotFoundError(f"Super dictionary not found: {self.super_dict_path}")
            
            with open(self.super_dict_path, 'r', encoding='utf-8') as f:
                self.super_dict = json.load(f)
            
            # 載入倒序字典
            if not self.super_dict_reversed_path.exists():
                raise FileNotFoundError(f"Reversed dictionary not found: {self.super_dict_reversed_path}")
            
            with open(self.super_dict_reversed_path, 'r', encoding='utf-8') as f:
                self.super_dict_reversed = json.load(f)
            
            self.total_entries = len(self.super_dict)
            self.load_time = time.time() - start_time
            
            self.logger.info(f"Loaded {self.total_entries} entries in {self.load_time:.2f}s")
            
            # 數據一致性檢查
            if len(self.super_dict) != len(self.super_dict_reversed):
                self.logger.warning("Dictionary sizes mismatch!")
            
        except Exception as e:
            self.logger.error(f"Failed to load dictionaries: {e}")
            raise
    
    def _build_indexes(self) -> None:
        """建立首字和尾字快速索引"""
        start_time = time.time()
        
        # 建立首字索引（基於正序字典）
        for word in self.super_dict:
            if word and len(word) > 0:
                first_char = word[0]
                self.first_char_index[first_char].append(word)
                self.unique_first_chars.add(first_char)
        
        # 建立尾字索引（基於倒序字典）
        for reversed_word in self.super_dict_reversed:
            if reversed_word and len(reversed_word) > 0:
                # 倒序詞的首字就是原詞的尾字
                last_char = reversed_word[0]
                original_word = reversed_word[::-1]  # 還原原始詞彙
                self.last_char_index[last_char].append(original_word)
                self.unique_last_chars.add(last_char)
        
        index_time = time.time() - start_time
        self.logger.info(f"Built indexes in {index_time:.2f}s: "
                        f"{len(self.unique_first_chars)} first chars, "
                        f"{len(self.unique_last_chars)} last chars")
    
    def get_words_by_first_char(self, first_char: str) -> List[str]:
        """
        根據首字獲取所有相關詞彙 - L1篩選核心功能
        
        Args:
            first_char: 首字
            
        Returns:
            以該字開頭的所有詞彙列表
        """
        return self.first_char_index.get(first_char, [])
    
    def get_words_by_last_char(self, last_char: str) -> List[str]:
        """
        根據尾字獲取所有相關詞彙 - L2重排核心功能
        
        Args:
            last_char: 尾字
            
        Returns:
            以該字結尾的所有詞彙列表
        """
        return self.last_char_index.get(last_char, [])
    
    def get_words_by_first_last_chars(self, first_char: str, last_char: str) -> List[str]:
        """
        根據首尾字組合獲取詞彙 - 進階篩選功能
        
        Args:
            first_char: 首字
            last_char: 尾字
            
        Returns:
            符合首尾字條件的詞彙列表
        """
        first_words = set(self.get_words_by_first_char(first_char))
        last_words = set(self.get_words_by_last_char(last_char))
        
        # 取交集
        return list(first_words & last_words)
    
    def filter_by_length(self, words: List[str], target_length: int, 
                        tolerance: int = 1) -> List[str]:
        """
        按長度篩選詞彙
        
        Args:
            words: 詞彙列表
            target_length: 目標長度
            tolerance: 長度容差
            
        Returns:
            符合長度條件的詞彙列表
        """
        return [word for word in words 
                if abs(len(word) - target_length) <= tolerance]
    
    def get_all_words(self) -> List[str]:
        """獲取完整17萬詞典"""
        return self.super_dict.copy()
    
    def get_statistics(self) -> Dict[str, any]:
        """獲取字典統計信息"""
        length_distribution = defaultdict(int)
        for word in self.super_dict:
            length_distribution[len(word)] += 1
        
        return {
            "total_entries": self.total_entries,
            "unique_first_chars": len(self.unique_first_chars),
            "unique_last_chars": len(self.unique_last_chars),
            "load_time_seconds": self.load_time,
            "length_distribution": dict(length_distribution),
            "average_word_length": sum(len(word) for word in self.super_dict) / len(self.super_dict),
            "first_char_coverage": {
                "max_words_per_char": max(len(words) for words in self.first_char_index.values()),
                "min_words_per_char": min(len(words) for words in self.first_char_index.values()),
                "avg_words_per_char": sum(len(words) for words in self.first_char_index.values()) / len(self.first_char_index)
            }
        }
    
    def validate_integrity(self) -> Tuple[bool, List[str]]:
        """
        驗證字典完整性
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # 檢查基本數據
        if not self.super_dict:
            errors.append("Super dictionary is empty")
        
        if not self.super_dict_reversed:
            errors.append("Reversed dictionary is empty")
        
        # 檢查索引完整性
        indexed_first_count = sum(len(words) for words in self.first_char_index.values())
        if indexed_first_count != self.total_entries:
            errors.append(f"First char index mismatch: {indexed_first_count} vs {self.total_entries}")
        
        indexed_last_count = sum(len(words) for words in self.last_char_index.values())
        if indexed_last_count != self.total_entries:
            errors.append(f"Last char index mismatch: {indexed_last_count} vs {self.total_entries}")
        
        # 檢查數據質量
        empty_words = sum(1 for word in self.super_dict if not word or len(word) == 0)
        if empty_words > 0:
            errors.append(f"Found {empty_words} empty words")
        
        return len(errors) == 0, errors
    
    def search_words(self, query: str, max_results: int = 100) -> List[str]:
        """
        簡單的詞彙搜索功能
        
        Args:
            query: 搜索關鍵詞
            max_results: 最大結果數
            
        Returns:
            包含關鍵詞的詞彙列表
        """
        results = []
        for word in self.super_dict:
            if query in word:
                results.append(word)
                if len(results) >= max_results:
                    break
        return results


def test_super_dictionary_manager():
    """測試SuperDictionaryManager基本功能"""
    try:
        # 初始化管理器
        manager = SuperDictionaryManager(
            super_dict_path="/Users/fl/Python/M1A2T/TWGY_V3/data/super_dicts/super_dict_combined.json",
            super_dict_reversed_path="/Users/fl/Python/M1A2T/TWGY_V3/data/super_dicts/super_dict_reversed.json"
        )
        
        # 驗證完整性
        is_valid, errors = manager.validate_integrity()
        print(f"Dictionary integrity: {'✓ Valid' if is_valid else '✗ Invalid'}")
        if errors:
            for error in errors:
                print(f"  Error: {error}")
        
        # 統計信息
        stats = manager.get_statistics()
        print(f"Total entries: {stats['total_entries']:,}")
        print(f"Load time: {stats['load_time_seconds']:.2f}s")
        print(f"Unique first chars: {stats['unique_first_chars']}")
        print(f"Average word length: {stats['average_word_length']:.1f}")
        
        # 測試首字查詢
        words_start_with_知 = manager.get_words_by_first_char("知")
        print(f"Words starting with '知': {len(words_start_with_知)} (first 10: {words_start_with_知[:10]})")
        
        # 測試尾字查詢  
        words_end_with_道 = manager.get_words_by_last_char("道")
        print(f"Words ending with '道': {len(words_end_with_道)} (first 10: {words_end_with_道[:10]})")
        
        # 測試首尾字組合查詢
        words_知_道 = manager.get_words_by_first_last_chars("知", "道")
        print(f"Words '知...道': {words_知_道}")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 執行測試
    success = test_super_dictionary_manager()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
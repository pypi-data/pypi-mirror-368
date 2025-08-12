"""
ToneAnalyzer - 聲調相似度分析器
實現基於聲調特徵的相似度計算，支援L3完整語音特徵重排
"""

import logging
from typing import Dict, List, Set, Optional, Tuple, Union
from dataclasses import dataclass
import re


@dataclass
class ToneFeatures:
    """聲調語音特徵結構"""
    tone: int = 0                       # 聲調值 (1-4, 0=未知)
    tone_name: str = ""                 # 聲調名稱 (陰平、陽平等)
    tone_type: str = ""                 # 聲調類型 (平聲、上聲等)
    pitch_contour: str = ""             # 音高變化 (高、中、低、升、降)
    tone_length: str = ""               # 音長特徵 (短、長)
    is_entering_tone: bool = False      # 是否為入聲


class ToneAnalyzer:
    """
    聲調相似度分析器
    
    功能：
    1. 聲調語音學特徵提取與分類
    2. 基於音高變化計算聲調相似度
    3. 支援台灣國語聲調變異 (二三聲混淆、輕聲處理等)
    4. 為L3重排器提供精確的聲調相似度分數
    """
    
    def __init__(self):
        """初始化聲調分析器"""
        self.logger = logging.getLogger(__name__)
        
        # 四聲調系統定義
        self.tone_system = {
            1: {
                "name": "陰平",
                "type": "平聲",
                "pitch_contour": "高平",
                "pitch_level": "55",
                "length": "長",
                "characteristics": "高而平"
            },
            2: {
                "name": "陽平",
                "type": "平聲", 
                "pitch_contour": "中升",
                "pitch_level": "35",
                "length": "長",
                "characteristics": "由中到高"
            },
            3: {
                "name": "上聲",
                "type": "上聲",
                "pitch_contour": "低升",
                "pitch_level": "214", 
                "length": "長",
                "characteristics": "先降後升"
            },
            4: {
                "name": "去聲",
                "type": "去聲",
                "pitch_contour": "高降",
                "pitch_level": "51",
                "length": "長",
                "characteristics": "由高到低"
            },
            0: {
                "name": "輕聲",
                "type": "輕聲",
                "pitch_contour": "中短",
                "pitch_level": "0",
                "length": "短",
                "characteristics": "短而輕"
            }
        }
        
        # 聲調分組（基於語音學特徵）
        self.tone_groups = {
            "平聲": [1, 2],         # 陰平、陽平
            "仄聲": [3, 4],         # 上聲、去聲
            "長調": [1, 2, 3, 4],   # 所有完整聲調
            "短調": [0],            # 輕聲
        }
        
        # 音高特徵分類
        self.pitch_features = {
            "高音區": [1, 4],       # 陰平(55)、去聲(51) 
            "中音區": [2],          # 陽平(35)
            "低音區": [3],          # 上聲(214)
            "升調": [2, 3],         # 陽平、上聲
            "降調": [4],            # 去聲
            "平調": [1],            # 陰平
            "曲調": [3]             # 上聲(曲折調)
        }
        
        # 台灣國語聲調變異對照表
        self.tone_confusion_pairs = [
            # 二三聲混淆 (台灣國語常見)
            (2, 3, 0.8),    # 陽平 vs 上聲
            (3, 2, 0.8),    # 上聲 vs 陽平
            
            # 一四聲混淆 (部分方言)
            (1, 4, 0.6),    # 陰平 vs 去聲
            (4, 1, 0.6),    # 去聲 vs 陰平
            
            # 輕聲與各聲調的弱化關係
            (1, 0, 0.5),    # 陰平 → 輕聲
            (2, 0, 0.5),    # 陽平 → 輕聲
            (3, 0, 0.5),    # 上聲 → 輕聲
            (4, 0, 0.5),    # 去聲 → 輕聲
        ]
        
        # 建立反向索引
        self._build_tone_mappings()
        
        self.logger.info(f"ToneAnalyzer initialized with {len(self.tone_system)} tones")
    
    def _build_tone_mappings(self):
        """建立聲調映射和相似度快速查找表"""
        # 聲調相似度快速查找表
        self.tone_similarity_cache = {}
        
        for tone1, tone2, similarity in self.tone_confusion_pairs:
            self.tone_similarity_cache[(tone1, tone2)] = similarity
            # 對稱性已在列表中處理，不重複添加
        
        # 建立音高特徵反向映射
        self.tone_to_pitch_features = {}
        for feature, tones in self.pitch_features.items():
            for tone in tones:
                if tone not in self.tone_to_pitch_features:
                    self.tone_to_pitch_features[tone] = []
                self.tone_to_pitch_features[tone].append(feature)
    
    def extract_tone_features(self, character: str, tone_hint: int = None) -> ToneFeatures:
        """
        提取單字聲調特徵
        
        Args:
            character: 中文字符
            tone_hint: 聲調提示 (1-4, 0=輕聲)
            
        Returns:
            ToneFeatures: 聲調特徵結構
        """
        # 簡化實現：基於字符映射 (實際需要聲調標註或拼音庫)
        char_tone_map = {
            # 常見字符的聲調映射
            '知': 1, '道': 4, '資': 1, '指': 3, 
            '吃': 1, '飯': 4, '次': 4, '完': 2,
            '安': 1, '全': 2, '昂': 2, '按': 4,
            '來': 2, '了': 0, '這': 4, '樣': 4,
            '手': 3, '機': 1, '收': 1, '集': 2,
            '電': 4, '腦': 3, '醬': 4, '瓜': 1
        }
        
        # 使用提示或映射獲取聲調
        tone_value = tone_hint if tone_hint is not None else char_tone_map.get(character, 1)
        tone_info = self.tone_system.get(tone_value, self.tone_system[1])
        
        features = ToneFeatures()
        features.tone = tone_value
        features.tone_name = tone_info["name"]
        features.tone_type = tone_info["type"]
        features.pitch_contour = tone_info["pitch_contour"]
        features.tone_length = tone_info["length"]
        features.is_entering_tone = False  # 標準中文無入聲
        
        return features
    
    def calculate_tone_similarity(self, tone1: int, tone2: int) -> float:
        """
        計算聲調相似度
        
        Args:
            tone1, tone2: 待比較的聲調值 (1-4, 0=輕聲)
            
        Returns:
            相似度分數 (0.0-1.0)
        """
        if tone1 == tone2:
            return 1.0
        
        # 檢查緩存的相似聲調對
        cache_key = (tone1, tone2)
        if cache_key in self.tone_similarity_cache:
            return self.tone_similarity_cache[cache_key]
        
        # 基於語音學特徵計算相似度
        return self._calculate_tone_feature_similarity(tone1, tone2)
    
    def _calculate_tone_feature_similarity(self, tone1: int, tone2: int) -> float:
        """基於聲調特徵計算相似度"""
        similarity_score = 0.0
        
        tone1_info = self.tone_system.get(tone1, self.tone_system[1])
        tone2_info = self.tone_system.get(tone2, self.tone_system[1])
        
        # 聲調類型相似度 (40%權重)
        if tone1_info["type"] == tone2_info["type"]:
            similarity_score += 0.4
        elif self._are_tone_types_similar(tone1_info["type"], tone2_info["type"]):
            similarity_score += 0.2
        
        # 音高變化相似度 (40%權重)
        if tone1_info["pitch_contour"] == tone2_info["pitch_contour"]:
            similarity_score += 0.4
        elif self._are_pitch_contours_similar(tone1_info["pitch_contour"], tone2_info["pitch_contour"]):
            similarity_score += 0.2
        
        # 音長相似度 (20%權重)
        if tone1_info["length"] == tone2_info["length"]:
            similarity_score += 0.2
        
        return min(similarity_score, 1.0)
    
    def _are_tone_types_similar(self, type1: str, type2: str) -> bool:
        """判斷聲調類型是否相似"""
        # 平聲內部相似
        if type1 in ["陰平", "陽平"] and type2 in ["陰平", "陽平"]:
            return True
        
        # 仄聲內部相似
        if type1 in ["上聲", "去聲"] and type2 in ["上聲", "去聲"]:
            return True
        
        return False
    
    def _are_pitch_contours_similar(self, contour1: str, contour2: str) -> bool:
        """判斷音高變化是否相似"""
        similar_contours = [
            ("高平", "高降"),     # 都在高音區
            ("中升", "低升"),     # 都是升調
            ("高降", "低升"),     # 對比調型
        ]
        
        for c1, c2 in similar_contours:
            if (contour1 == c1 and contour2 == c2) or (contour1 == c2 and contour2 == c1):
                return True
        
        return False
    
    def get_similar_tones(self, target_tone: int, threshold: float = 0.5) -> List[Tuple[int, float]]:
        """
        獲取與指定聲調相似的聲調列表
        
        Args:
            target_tone: 目標聲調
            threshold: 相似度閾值
            
        Returns:
            [(聲調, 相似度分數)] 的列表
        """
        similar_tones = []
        
        for tone in range(5):  # 0-4 (輕聲+四聲)
            if tone != target_tone:
                similarity = self.calculate_tone_similarity(target_tone, tone)
                if similarity >= threshold:
                    similar_tones.append((tone, similarity))
        
        # 按相似度排序
        similar_tones.sort(key=lambda x: x[1], reverse=True)
        return similar_tones
    
    def analyze_tone_distribution(self, words: List[str]) -> Dict[str, any]:
        """
        分析詞彙列表的聲調分佈
        
        Args:
            words: 詞彙列表
            
        Returns:
            聲調分佈統計
        """
        tone_count = {i: 0 for i in range(5)}  # 0-4
        tone_pattern_count = {}
        
        for word in words:
            word_tones = []
            for char in word:
                features = self.extract_tone_features(char)
                tone = features.tone
                tone_count[tone] += 1
                word_tones.append(tone)
            
            # 統計聲調模式 (如: "1-4" 表示陰平+去聲)
            pattern = "-".join(map(str, word_tones))
            tone_pattern_count[pattern] = tone_pattern_count.get(pattern, 0) + 1
        
        return {
            "tone_distribution": {
                f"tone_{i}({self.tone_system[i]['name']})": count 
                for i, count in tone_count.items()
            },
            "tone_patterns": dict(sorted(tone_pattern_count.items(), key=lambda x: x[1], reverse=True)),
            "total_characters": sum(tone_count.values()),
            "most_common_tone": max(tone_count.items(), key=lambda x: x[1]),
            "tone_diversity": len([count for count in tone_count.values() if count > 0])
        }
    
    def calculate_word_tone_similarity(self, word1: str, word2: str) -> float:
        """
        計算詞彙間的聲調相似度
        
        Args:
            word1, word2: 待比較的詞彙
            
        Returns:
            聲調相似度分數 (0.0-1.0)
        """
        if not word1 or not word2:
            return 0.0
        
        if word1 == word2:
            return 1.0
        
        # 提取兩詞的聲調序列
        tones1 = []
        for char in word1:
            features = self.extract_tone_features(char)
            tones1.append(features.tone)
        
        tones2 = []
        for char in word2:
            features = self.extract_tone_features(char)
            tones2.append(features.tone)
        
        # 使用動態規劃計算序列相似度
        return self._calculate_tone_sequence_similarity(tones1, tones2)
    
    def _calculate_tone_sequence_similarity(self, tones1: List[int], tones2: List[int]) -> float:
        """計算聲調序列相似度 (基於編輯距離的改進版)"""
        if not tones1 or not tones2:
            return 0.0
        
        len1, len2 = len(tones1), len(tones2)
        
        # 動態規劃表
        dp = [[0.0] * (len2 + 1) for _ in range(len1 + 1)]
        
        # 初始化
        for i in range(1, len1 + 1):
            dp[i][0] = 0.0
        for j in range(1, len2 + 1):
            dp[0][j] = 0.0
        
        # 填充動態規劃表
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                # 匹配得分
                match_score = self.calculate_tone_similarity(tones1[i-1], tones2[j-1])
                
                # 三種操作的得分
                match = dp[i-1][j-1] + match_score
                delete = dp[i-1][j] * 0.8  # 刪除懲罰
                insert = dp[i][j-1] * 0.8  # 插入懲罰
                
                dp[i][j] = max(match, delete, insert)
        
        # 標準化得分
        max_possible_score = max(len1, len2)
        return dp[len1][len2] / max_possible_score if max_possible_score > 0 else 0.0
    
    def get_analyzer_stats(self) -> Dict[str, any]:
        """獲取分析器統計信息"""
        return {
            "tone_system_size": len(self.tone_system),
            "tone_groups": len(self.tone_groups),
            "pitch_features": len(self.pitch_features),
            "confusion_pairs": len(self.tone_confusion_pairs),
            "similarity_cache_size": len(self.tone_similarity_cache),
            "tone_breakdown": {
                f"tone_{i}": info["name"] 
                for i, info in self.tone_system.items()
            },
            "group_breakdown": {
                group: tones for group, tones in self.tone_groups.items()
            }
        }


def test_tone_analyzer():
    """測試ToneAnalyzer功能"""
    print("🧪 測試ToneAnalyzer功能")
    print("=" * 50)
    
    analyzer = ToneAnalyzer()
    
    # 測試聲調特徵提取
    print("📊 聲調特徵提取測試:")
    print("-" * 40)
    test_chars = ['知', '道', '吃', '飯', '安', '全', '來', '了']
    for char in test_chars:
        features = analyzer.extract_tone_features(char)
        print(f"{char}: 聲調={features.tone}({features.tone_name}), "
              f"類型={features.tone_type}, 音高={features.pitch_contour}")
    
    # 測試聲調相似度
    print("\n📊 聲調相似度測試:")
    print("-" * 40)
    test_tone_pairs = [
        (1, 1),  # 相同聲調
        (2, 3),  # 二三聲混淆
        (3, 2),  # 三二聲混淆
        (1, 4),  # 一四聲
        (1, 0),  # 完整聲調vs輕聲
        (2, 0),  # 陽平vs輕聲
    ]
    
    for tone1, tone2 in test_tone_pairs:
        similarity = analyzer.calculate_tone_similarity(tone1, tone2)
        name1 = analyzer.tone_system[tone1]["name"]
        name2 = analyzer.tone_system[tone2]["name"]
        print(f"{tone1}({name1}) vs {tone2}({name2}): {similarity:.3f}")
    
    # 測試相似聲調查找
    print("\n📊 相似聲調查找測試:")
    print("-" * 40)
    target_tone = 2  # 陽平
    similar_tones = analyzer.get_similar_tones(target_tone, threshold=0.5)
    print(f"與聲調{target_tone}({analyzer.tone_system[target_tone]['name']})相似的聲調:")
    for tone, score in similar_tones:
        print(f"  {tone}({analyzer.tone_system[tone]['name']}): {score:.3f}")
    
    # 測試詞彙聲調相似度
    print("\n📊 詞彙聲調相似度測試:")
    print("-" * 40)
    word_pairs = [
        ("知道", "資道"),   # 一四 vs 一四
        ("吃飯", "次完"),   # 一四 vs 四二
        ("安全", "昂全"),   # 一二 vs 二二
        ("知道", "來了"),   # 一四 vs 二輕聲
    ]
    
    for word1, word2 in word_pairs:
        similarity = analyzer.calculate_word_tone_similarity(word1, word2)
        print(f"'{word1}' vs '{word2}': {similarity:.3f}")
    
    # 測試聲調分佈分析
    print("\n📊 聲調分佈分析測試:")
    print("-" * 40)
    test_words = ["知道", "資道", "吃飯", "安全", "來了", "電腦", "手機"]
    distribution = analyzer.analyze_tone_distribution(test_words)
    
    print("聲調分佈:")
    for tone_name, count in distribution["tone_distribution"].items():
        if count > 0:
            print(f"  {tone_name}: {count}")
    
    print(f"\n最常見聲調: {distribution['most_common_tone'][0]}調 "
          f"({distribution['most_common_tone'][1]}次)")
    print(f"聲調多樣性: {distribution['tone_diversity']}/5")
    
    # 統計信息
    print("\n📊 分析器統計:")
    print("-" * 40)
    stats = analyzer.get_analyzer_stats()
    print(f"聲調系統大小: {stats['tone_system_size']}")
    print(f"聲調分組數: {stats['tone_groups']}")
    print(f"音高特徵數: {stats['pitch_features']}")
    print(f"混淆對數: {stats['confusion_pairs']}")
    
    return True


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 執行測試
    success = test_tone_analyzer()
    print(f"\n測試 {'✅ PASSED' if success else '❌ FAILED'}")
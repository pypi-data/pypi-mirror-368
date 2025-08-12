"""
FinalsAnalyzer - 韻母相似度分析器
實現基於語音學特徵的韻母分組與相似度計算，支援L2首尾字重排
"""

import logging
from typing import Dict, List, Set, Optional, Tuple, Union
from dataclasses import dataclass
import re


@dataclass
class FinalsFeatures:
    """韻母語音特徵結構"""
    finals: str = ""                    # 韻母符號
    main_vowel: str = ""                # 主要元音
    medial: str = ""                    # 介音 (i, u, ü)
    ending: str = ""                    # 尾音 (n, ng, 等)
    tone: int = 0                       # 聲調
    finals_group: str = ""              # 韻母分組 (開口呼、齊齒呼等)
    vowel_type: str = ""                # 元音類型 (前元音、後元音等)


class FinalsAnalyzer:
    """
    韻母相似度分析器
    
    功能：
    1. 韻母語音學特徵提取與分組
    2. 基於特徵計算韻母相似度
    3. 支援台灣國語變異 (前後鼻音不分、撮口呼變化等)
    4. 為L2重排器提供精確的韻母相似度分數
    """
    
    def __init__(self):
        """初始化韻母分析器"""
        self.logger = logging.getLogger(__name__)
        
        # 韻母分組定義 (基於四呼分類)
        self.finals_groups = {
            "開口呼": {
                # 無介音的韻母
                "single_vowels": ["ㄚ", "ㄛ", "ㄜ", "ㄦ"],
                "compound_finals": ["ㄞ", "ㄟ", "ㄠ", "ㄡ"],
                "nasal_finals": ["ㄢ", "ㄣ", "ㄤ", "ㄥ"]
            },
            "齊齒呼": {
                # 以i(ㄧ)為介音
                "i_finals": ["ㄧ", "ㄧㄚ", "ㄧㄛ", "ㄧㄝ"],
                "i_compound": ["ㄧㄞ", "ㄧㄠ", "ㄧㄡ"],
                "i_nasal": ["ㄧㄢ", "ㄧㄣ", "ㄧㄤ", "ㄧㄥ"]
            },
            "合口呼": {
                # 以u(ㄨ)為介音
                "u_finals": ["ㄨ", "ㄨㄚ", "ㄨㄛ"],
                "u_compound": ["ㄨㄞ", "ㄨㄟ"],
                "u_nasal": ["ㄨㄢ", "ㄨㄣ", "ㄨㄤ", "ㄨㄥ"]
            },
            "撮口呼": {
                # 以ü(ㄩ)為介音
                "v_finals": ["ㄩ", "ㄩㄝ"],
                "v_nasal": ["ㄩㄢ", "ㄩㄣ", "ㄩㄥ"]
            }
        }
        
        # 元音特徵分類
        self.vowel_features = {
            # 主要元音特徵 (前/央/後, 高/中/低)
            "ㄚ": {"position": "央", "height": "低", "roundness": "不圓"},
            "ㄛ": {"position": "後", "height": "中", "roundness": "圓"},
            "ㄜ": {"position": "央", "height": "中", "roundness": "不圓"},
            "ㄞ": {"position": "前", "height": "低-中", "roundness": "不圓"},
            "ㄟ": {"position": "前", "height": "中-高", "roundness": "不圓"},
            "ㄠ": {"position": "後", "height": "低-中", "roundness": "圓"},
            "ㄡ": {"position": "後", "height": "中-高", "roundness": "圓"},
            "ㄧ": {"position": "前", "height": "高", "roundness": "不圓"},
            "ㄨ": {"position": "後", "height": "高", "roundness": "圓"},
            "ㄩ": {"position": "前", "height": "高", "roundness": "圓"}
        }
        
        # 鼻音尾音分類 (前後鼻音不分的核心)
        self.nasal_endings = {
            "前鼻音": ["ㄢ", "ㄣ", "ㄧㄢ", "ㄧㄣ", "ㄨㄢ", "ㄨㄣ", "ㄩㄢ", "ㄩㄣ"],
            "後鼻音": ["ㄤ", "ㄥ", "ㄧㄤ", "ㄧㄥ", "ㄨㄤ", "ㄨㄥ", "ㄩㄥ"]
        }
        
        # 相似韻母對照表 (台灣國語常見變異)
        self.similar_finals_pairs = [
            # 前後鼻音不分
            ("ㄢ", "ㄤ", 0.8),    # an vs ang
            ("ㄣ", "ㄥ", 0.8),    # en vs eng  
            ("ㄧㄢ", "ㄧㄤ", 0.8), # ian vs iang
            ("ㄧㄣ", "ㄧㄥ", 0.8), # in vs ing
            ("ㄨㄢ", "ㄨㄤ", 0.8), # uan vs uang
            ("ㄨㄣ", "ㄨㄥ", 0.8), # un vs ong
            ("ㄩㄢ", "ㄩㄥ", 0.8), # van vs vng
            
            # 撮口呼變化
            ("ㄩㄝ", "ㄧㄝ", 0.7), # üe vs ie
            ("ㄩㄢ", "ㄧㄢ", 0.7), # üan vs ian
            ("ㄩㄣ", "ㄧㄣ", 0.7), # ün vs in
            
            # 合口呼相似
            ("ㄨㄟ", "ㄟ", 0.6),   # uei vs ei
            ("ㄨㄞ", "ㄞ", 0.6),   # uai vs ai
        ]
        
        # 建立反向索引
        self._build_reverse_mappings()
        
        self.logger.info(f"FinalsAnalyzer initialized with {len(self.finals_groups)} groups")
    
    def _build_reverse_mappings(self):
        """建立韻母到分組的反向映射"""
        self.finals_to_group = {}
        self.finals_to_category = {}
        
        for group_name, categories in self.finals_groups.items():
            for category_name, finals_list in categories.items():
                for finals in finals_list:
                    self.finals_to_group[finals] = group_name
                    self.finals_to_category[finals] = category_name
        
        # 建立相似度快速查找表
        self.similarity_cache = {}
        for finals1, finals2, similarity in self.similar_finals_pairs:
            self.similarity_cache[(finals1, finals2)] = similarity
            self.similarity_cache[(finals2, finals1)] = similarity  # 對稱性
    
    def extract_finals_features(self, character: str) -> FinalsFeatures:
        """
        提取單字韻母特徵
        
        Args:
            character: 中文字符
            
        Returns:
            FinalsFeatures: 韻母特徵結構
        """
        # 簡化實現：基於字符映射 (實際需要拼音庫)
        char_finals_map = {
            # 常見字符的韻母映射
            '道': 'ㄠ', '知': 'ㄧ', '資': 'ㄨ', '指': 'ㄧ',
            '吃': 'ㄧ', '次': 'ㄨ', '飯': 'ㄢ', '安': 'ㄢ', 
            '全': 'ㄧㄢ', '昂': 'ㄤ', '來': 'ㄞ', '內': 'ㄟ',
            '了': 'ㄜ', '這': 'ㄜ', '醬': 'ㄧㄤ', '樣': 'ㄧㄤ',
            '手': 'ㄡ', '收': 'ㄡ', '機': 'ㄧ', '雞': 'ㄧ'
        }
        
        finals_symbol = char_finals_map.get(character, 'ㄚ')  # 默認韻母
        
        features = FinalsFeatures()
        features.finals = finals_symbol
        features.finals_group = self.finals_to_group.get(finals_symbol, "未知分組")
        
        # 分析韻母結構
        features.main_vowel, features.medial, features.ending = self._parse_finals_structure(finals_symbol)
        
        # 設置元音類型
        if features.main_vowel in self.vowel_features:
            vowel_info = self.vowel_features[features.main_vowel]
            features.vowel_type = f"{vowel_info['position']}{vowel_info['height']}"
        
        return features
    
    def _parse_finals_structure(self, finals: str) -> Tuple[str, str, str]:
        """
        分析韻母內部結構
        
        Returns:
            (主要元音, 介音, 尾音)
        """
        if not finals:
            return "", "", ""
        
        # 簡化分析邏輯
        medial = ""
        main_vowel = ""
        ending = ""
        
        # 檢測介音
        if finals.startswith('ㄧ'):
            medial = 'ㄧ'
            remaining = finals[1:]
        elif finals.startswith('ㄨ'):
            medial = 'ㄨ'
            remaining = finals[1:]
        elif finals.startswith('ㄩ'):
            medial = 'ㄩ'
            remaining = finals[1:]
        else:
            remaining = finals
        
        # 檢測尾音
        if remaining.endswith('ㄢ') or remaining.endswith('ㄣ'):
            ending = '前鼻音'
            main_vowel = remaining[:-1] if len(remaining) > 1 else remaining
        elif remaining.endswith('ㄤ') or remaining.endswith('ㄥ'):
            ending = '後鼻音'
            main_vowel = remaining[:-1] if len(remaining) > 1 else remaining
        else:
            main_vowel = remaining
        
        return main_vowel, medial, ending
    
    def calculate_finals_similarity(self, finals1: str, finals2: str) -> float:
        """
        計算韻母相似度
        
        Args:
            finals1, finals2: 待比較的韻母
            
        Returns:
            相似度分數 (0.0-1.0)
        """
        if finals1 == finals2:
            return 1.0
        
        # 檢查緩存的相似韻母對
        cache_key = (finals1, finals2)
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        # 基於韻母分組計算相似度
        group1 = self.finals_to_group.get(finals1, "未知")
        group2 = self.finals_to_group.get(finals2, "未知")
        
        if group1 == group2 and group1 != "未知":
            # 同分組韻母有較高相似度
            return 0.7
        
        # 基於語音特徵計算
        features1 = self.extract_finals_features(finals1)
        features2 = self.extract_finals_features(finals2)
        
        return self._calculate_feature_similarity(features1, features2)
    
    def _calculate_feature_similarity(self, features1: FinalsFeatures, 
                                    features2: FinalsFeatures) -> float:
        """基於特徵計算相似度"""
        similarity_score = 0.0
        
        # 主要元音相似度 (權重40%)
        if features1.main_vowel == features2.main_vowel:
            similarity_score += 0.4
        elif self._are_vowels_similar(features1.main_vowel, features2.main_vowel):
            similarity_score += 0.2
        
        # 介音相似度 (權重30%)
        if features1.medial == features2.medial:
            similarity_score += 0.3
        elif self._are_medials_similar(features1.medial, features2.medial):
            similarity_score += 0.15
        
        # 尾音相似度 (權重30%)
        if features1.ending == features2.ending:
            similarity_score += 0.3
        elif self._are_endings_similar(features1.ending, features2.ending):
            similarity_score += 0.15
        
        return min(similarity_score, 1.0)
    
    def _are_vowels_similar(self, vowel1: str, vowel2: str) -> bool:
        """判斷元音是否相似"""
        if vowel1 not in self.vowel_features or vowel2 not in self.vowel_features:
            return False
        
        v1_features = self.vowel_features[vowel1]
        v2_features = self.vowel_features[vowel2]
        
        # 位置相同或高度相同
        return (v1_features["position"] == v2_features["position"] or
                v1_features["height"] == v2_features["height"])
    
    def _are_medials_similar(self, medial1: str, medial2: str) -> bool:
        """判斷介音是否相似"""
        # 撮口呼與齊齒呼的相似性
        similar_medials = [("ㄧ", "ㄩ")]
        
        for m1, m2 in similar_medials:
            if (medial1 == m1 and medial2 == m2) or (medial1 == m2 and medial2 == m1):
                return True
        return False
    
    def _are_endings_similar(self, ending1: str, ending2: str) -> bool:
        """判斷尾音是否相似 - 前後鼻音不分的核心"""
        # 前鼻音與後鼻音的相似性 (台灣國語特色)
        return ((ending1 == "前鼻音" and ending2 == "後鼻音") or
                (ending1 == "後鼻音" and ending2 == "前鼻音"))
    
    def get_similar_finals(self, finals: str, threshold: float = 0.5) -> List[Tuple[str, float]]:
        """
        獲取與指定韻母相似的韻母列表
        
        Args:
            finals: 目標韻母
            threshold: 相似度閾值
            
        Returns:
            [(韻母, 相似度分數)] 的列表
        """
        similar_finals = []
        
        # 從所有已知韻母中查找
        all_finals = set()
        for group_data in self.finals_groups.values():
            for finals_list in group_data.values():
                all_finals.update(finals_list)
        
        for candidate_finals in all_finals:
            if candidate_finals != finals:
                similarity = self.calculate_finals_similarity(finals, candidate_finals)
                if similarity >= threshold:
                    similar_finals.append((candidate_finals, similarity))
        
        # 按相似度排序
        similar_finals.sort(key=lambda x: x[1], reverse=True)
        return similar_finals
    
    def analyze_finals_distribution(self, words: List[str]) -> Dict[str, any]:
        """
        分析詞彙列表的韻母分佈
        
        Args:
            words: 詞彙列表
            
        Returns:
            韻母分佈統計
        """
        finals_count = {}
        group_count = {}
        
        for word in words:
            for char in word:
                features = self.extract_finals_features(char)
                finals = features.finals
                group = features.finals_group
                
                finals_count[finals] = finals_count.get(finals, 0) + 1
                group_count[group] = group_count.get(group, 0) + 1
        
        return {
            "finals_distribution": dict(sorted(finals_count.items(), key=lambda x: x[1], reverse=True)),
            "group_distribution": dict(sorted(group_count.items(), key=lambda x: x[1], reverse=True)),
            "total_characters": sum(finals_count.values()),
            "unique_finals": len(finals_count),
            "unique_groups": len(group_count)
        }
    
    def get_analyzer_stats(self) -> Dict[str, any]:
        """獲取分析器統計信息"""
        total_finals = sum(
            len(finals_list) 
            for group_data in self.finals_groups.values() 
            for finals_list in group_data.values()
        )
        
        return {
            "finals_groups": len(self.finals_groups),
            "total_finals": total_finals,
            "vowel_features": len(self.vowel_features),
            "similar_pairs": len(self.similar_finals_pairs),
            "similarity_cache_size": len(self.similarity_cache),
            "group_breakdown": {
                group: sum(len(finals_list) for finals_list in group_data.values())
                for group, group_data in self.finals_groups.items()
            }
        }


def test_finals_analyzer():
    """測試FinalsAnalyzer功能"""
    print("🧪 測試FinalsAnalyzer功能")
    print("=" * 50)
    
    analyzer = FinalsAnalyzer()
    
    # 測試韻母特徵提取
    print("📊 韻母特徵提取測試:")
    print("-" * 40)
    test_chars = ['道', '知', '安', '昂', '來', '內']
    for char in test_chars:
        features = analyzer.extract_finals_features(char)
        print(f"{char}: 韻母={features.finals}, 分組={features.finals_group}, "
              f"主元音={features.main_vowel}, 介音={features.medial}, 尾音={features.ending}")
    
    # 測試韻母相似度
    print("\n📊 韻母相似度測試:")
    print("-" * 40)
    test_pairs = [
        ('ㄢ', 'ㄤ'),     # 前後鼻音不分
        ('ㄣ', 'ㄥ'),     # 前後鼻音不分
        ('ㄧㄢ', 'ㄧㄤ'), # 前後鼻音不分 + 齊齒呼
        ('ㄩㄝ', 'ㄧㄝ'), # 撮口呼變化
        ('ㄚ', 'ㄛ'),     # 不同元音
        ('ㄞ', 'ㄟ'),     # 復韻母
    ]
    
    for finals1, finals2 in test_pairs:
        similarity = analyzer.calculate_finals_similarity(finals1, finals2)
        print(f"{finals1} vs {finals2}: {similarity:.3f}")
    
    # 測試相似韻母查找
    print("\n📊 相似韻母查找測試:")
    print("-" * 40)
    target_finals = 'ㄢ'
    similar = analyzer.get_similar_finals(target_finals, threshold=0.6)
    print(f"與 '{target_finals}' 相似的韻母:")
    for finals, score in similar[:5]:  # 顯示前5個
        print(f"  {finals}: {score:.3f}")
    
    # 統計信息
    print("\n📊 分析器統計:")
    print("-" * 40)
    stats = analyzer.get_analyzer_stats()
    print(f"韻母分組數: {stats['finals_groups']}")
    print(f"總韻母數: {stats['total_finals']}")
    print(f"元音特徵數: {stats['vowel_features']}")
    print(f"相似韻母對數: {stats['similar_pairs']}")
    
    print("\n各分組韻母數:")
    for group, count in stats['group_breakdown'].items():
        print(f"  {group}: {count}")
    
    return True


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 執行測試
    success = test_finals_analyzer()
    print(f"\n測試 {'✅ PASSED' if success else '❌ FAILED'}")
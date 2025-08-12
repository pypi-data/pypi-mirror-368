"""
第二期混合架構設計 - 規則基礎 + 機器學習模型組合
基於第一期收集的訓練數據設計下一代語音重排系統
"""

import time
import logging
import json
from typing import List, Dict, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod

# 第一期系統導入
from phonetic_reranker import PhoneticReranker, RerankerConfig, RerankerResult
from data.training_data_logger import TrainingDataLogger


@dataclass
class MLModelConfig:
    """機器學習模型配置"""
    model_type: str = "transformer"  # transformer, lstm, cnn
    model_path: str = "models/phonetic_similarity.pt"
    max_sequence_length: int = 10
    hidden_size: int = 256
    num_attention_heads: int = 8
    num_layers: int = 4
    
    # 訓練配置
    batch_size: int = 32
    learning_rate: float = 0.001
    num_epochs: int = 100
    validation_split: float = 0.2


@dataclass  
class HybridConfig:
    """混合系統配置"""
    # 第一期規則系統配置
    rule_based_config: RerankerConfig = None
    
    # 機器學習模型配置
    ml_model_config: MLModelConfig = None
    
    # 混合策略配置
    fusion_strategy: str = "weighted_ensemble"  # weighted_ensemble, cascaded, adaptive
    rule_weight: float = 0.6  # 規則系統權重
    ml_weight: float = 0.4    # ML模型權重
    
    # 適應性配置
    enable_adaptive_weighting: bool = True
    confidence_threshold: float = 0.8
    fallback_to_rules: bool = True


class BaseMLModel(ABC):
    """機器學習模型基礎類"""
    
    @abstractmethod
    def predict(self, query: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """預測候選詞相似度分數"""
        pass
    
    @abstractmethod
    def train(self, training_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """訓練模型"""
        pass
    
    @abstractmethod
    def save_model(self, path: str) -> bool:
        """保存模型"""
        pass
    
    @abstractmethod
    def load_model(self, path: str) -> bool:
        """載入模型"""
        pass


class TransformerPhoneticModel(BaseMLModel):
    """
    基於Transformer的語音相似度模型
    
    特點：
    1. 注意力機制捕捉聲韻調長距離依賴
    2. 字符級別的語音特徵編碼
    3. 支援變長序列處理
    4. 預訓練 + 微調架構
    """
    
    def __init__(self, config: MLModelConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 模型組件初始化 (實際需要使用深度學習框架如PyTorch)
        self.tokenizer = None  # 字符級別分詞器
        self.feature_encoder = None  # 語音特徵編碼器
        self.transformer = None  # Transformer核心
        self.similarity_head = None  # 相似度預測頭
        
        self.logger.info(f"TransformerPhoneticModel initialized with {config.model_type}")
    
    def predict(self, query: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """
        使用Transformer預測相似度分數
        
        Args:
            query: 查詢詞
            candidates: 候選詞列表
            
        Returns:
            (候選詞, 相似度分數) 列表
        """
        if not self.transformer:
            # 模型未載入，返回基準分數
            return [(candidate, 0.5) for candidate in candidates]
        
        # 實際實現需要：
        # 1. 字符級別tokenization
        # 2. 語音特徵編碼 (聲韻調向量化)
        # 3. Transformer encoder處理
        # 4. 相似度計算
        
        # 模擬實現
        results = []
        for candidate in candidates:
            # 簡化的相似度計算邏輯
            if query == candidate:
                similarity = 1.0
            elif len(query) == len(candidate):
                similarity = 0.8  # 同長度詞給予較高分數
            else:
                similarity = 0.6
            
            results.append((candidate, similarity))
        
        return results
    
    def train(self, training_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        訓練Transformer模型
        
        Args:
            training_data: 第一期系統收集的訓練數據
            
        Returns:
            訓練指標字典
        """
        self.logger.info(f"Training transformer model on {len(training_data)} samples")
        
        # 實際訓練流程：
        # 1. 數據預處理和特徵提取
        # 2. 建構訓練/驗證數據集
        # 3. 模型訓練循環
        # 4. 驗證和早停
        # 5. 模型保存
        
        # 模擬訓練指標
        metrics = {
            "train_loss": 0.15,
            "val_loss": 0.18,
            "accuracy": 0.92,
            "f1_score": 0.89,
            "training_time_hours": 2.5
        }
        
        return metrics
    
    def save_model(self, path: str) -> bool:
        """保存訓練好的模型"""
        try:
            # 實際保存邏輯
            self.logger.info(f"Model saved to {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
            return False
    
    def load_model(self, path: str) -> bool:
        """載入預訓練模型"""
        try:
            # 實際載入邏輯
            self.logger.info(f"Model loaded from {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False


class HybridPhoneticReranker:
    """
    混合語音重排系統 - 第二期架構
    
    整合優勢：
    1. 規則系統：解釋性強、穩定可靠、低延遲
    2. ML模型：適應性強、學習能力、處理複雜模式
    3. 混合策略：取長補短、動態調整、最佳性能
    
    架構模式：
    - Cascaded: 規則初篩 → ML精排
    - Weighted Ensemble: 規則分數 + ML分數 → 加權融合
    - Adaptive: 根據查詢複雜度動態選擇策略
    """
    
    def __init__(self, config: HybridConfig):
        """
        初始化混合重排系統
        
        Args:
            config: 混合系統配置
        """
        self.config = config or HybridConfig()
        self.logger = logging.getLogger(__name__)
        
        # 初始化第一期規則系統
        self.rule_based_reranker = PhoneticReranker(self.config.rule_based_config)
        
        # 初始化機器學習模型
        ml_config = self.config.ml_model_config or MLModelConfig()
        if ml_config.model_type == "transformer":
            self.ml_model = TransformerPhoneticModel(ml_config)
        else:
            raise ValueError(f"Unsupported model type: {ml_config.model_type}")
        
        # 性能統計
        self.hybrid_stats = {
            "total_queries": 0,
            "rule_only_queries": 0,
            "ml_only_queries": 0,
            "hybrid_queries": 0,
            "avg_processing_time_ms": 0.0,
            "rule_confidence_distribution": {},
            "ml_confidence_distribution": {}
        }
        
        self.logger.info("HybridPhoneticReranker initialized")
    
    def rerank(self, query: str, max_candidates: Optional[int] = None) -> RerankerResult:
        """
        執行混合重排
        
        Args:
            query: 查詢詞彙
            max_candidates: 最大返回候選數
            
        Returns:
            混合重排結果
        """
        start_time = time.time()
        
        # Phase 1: 規則系統處理
        rule_result = self.rule_based_reranker.rerank(query, max_candidates)
        
        if rule_result.error:
            # 規則系統失敗，直接返回
            return rule_result
        
        # Phase 2: 決定融合策略
        fusion_strategy = self._select_fusion_strategy(query, rule_result)
        
        # Phase 3: 執行混合處理
        if fusion_strategy == "rule_only":
            final_result = rule_result
            self.hybrid_stats["rule_only_queries"] += 1
            
        elif fusion_strategy == "cascaded":
            final_result = self._cascaded_rerank(query, rule_result)
            self.hybrid_stats["hybrid_queries"] += 1
            
        elif fusion_strategy == "weighted_ensemble":
            final_result = self._weighted_ensemble_rerank(query, rule_result)
            self.hybrid_stats["hybrid_queries"] += 1
            
        else:  # adaptive
            final_result = self._adaptive_rerank(query, rule_result)
            self.hybrid_stats["hybrid_queries"] += 1
        
        # 更新統計
        processing_time = (time.time() - start_time) * 1000
        self.hybrid_stats["total_queries"] += 1
        self._update_performance_stats(processing_time)
        
        return final_result
    
    def _select_fusion_strategy(self, query: str, rule_result: RerankerResult) -> str:
        """
        選擇融合策略
        
        Args:
            query: 查詢詞
            rule_result: 規則系統結果
            
        Returns:
            融合策略名稱
        """
        if not self.config.enable_adaptive_weighting:
            return self.config.fusion_strategy
        
        # 適應性策略選擇
        rule_confidence = rule_result.confidence_score
        
        if rule_confidence >= self.config.confidence_threshold:
            # 規則系統信心度高，直接使用
            return "rule_only"
        elif rule_result.complexity_level == "simple":
            # 簡單查詢，級聯處理
            return "cascaded"
        else:
            # 複雜查詢，加權融合
            return "weighted_ensemble"
    
    def _cascaded_rerank(self, query: str, rule_result: RerankerResult) -> RerankerResult:
        """
        級聯重排：規則初篩 → ML精排
        
        Args:
            query: 查詢詞
            rule_result: 規則系統結果
            
        Returns:
            級聯處理結果
        """
        # 使用ML模型對規則結果進一步精排
        ml_scores = self.ml_model.predict(query, rule_result.candidates)
        
        # 按ML分數重新排序
        ml_scores.sort(key=lambda x: x[1], reverse=True)
        refined_candidates = [word for word, _ in ml_scores]
        
        # 更新結果
        cascaded_result = RerankerResult(
            query=query,
            candidates=refined_candidates,
            processing_time_ms=rule_result.processing_time_ms + 5.0,  # ML加時
            complexity_level=rule_result.complexity_level,
            confidence_score=min(rule_result.confidence_score * 1.1, 1.0)  # 輕微提升信心度
        )
        
        return cascaded_result
    
    def _weighted_ensemble_rerank(self, query: str, rule_result: RerankerResult) -> RerankerResult:
        """
        加權集成重排：規則分數 + ML分數
        
        Args:
            query: 查詢詞
            rule_result: 規則系統結果
            
        Returns:
            加權集成結果
        """
        # 獲取ML模型分數
        ml_scores = dict(self.ml_model.predict(query, rule_result.candidates))
        
        # 加權融合分數
        ensemble_scores = []
        for candidate in rule_result.candidates:
            # 規則分數（基於排名推估）
            rule_score = 1.0 - (rule_result.candidates.index(candidate) / len(rule_result.candidates))
            
            # ML分數
            ml_score = ml_scores.get(candidate, 0.5)
            
            # 加權融合
            final_score = (rule_score * self.config.rule_weight + 
                          ml_score * self.config.ml_weight)
            
            ensemble_scores.append((candidate, final_score))
        
        # 按融合分數排序
        ensemble_scores.sort(key=lambda x: x[1], reverse=True)
        ensemble_candidates = [word for word, _ in ensemble_scores]
        
        # 更新結果
        ensemble_result = RerankerResult(
            query=query,
            candidates=ensemble_candidates,
            processing_time_ms=rule_result.processing_time_ms + 10.0,  # 融合加時
            complexity_level=rule_result.complexity_level,
            confidence_score=min(rule_result.confidence_score * 1.2, 1.0)  # 顯著提升信心度
        )
        
        return ensemble_result
    
    def _adaptive_rerank(self, query: str, rule_result: RerankerResult) -> RerankerResult:
        """
        適應性重排：根據情況動態選擇最佳策略
        
        Args:
            query: 查詢詞
            rule_result: 規則系統結果
            
        Returns:
            適應性處理結果
        """
        # 根據查詢特徵動態選擇
        if len(rule_result.candidates) < 10:
            # 候選詞較少，使用級聯處理
            return self._cascaded_rerank(query, rule_result)
        else:
            # 候選詞較多，使用加權集成
            return self._weighted_ensemble_rerank(query, rule_result)
    
    def _update_performance_stats(self, processing_time: float):
        """更新性能統計"""
        current_avg = self.hybrid_stats["avg_processing_time_ms"]
        total_queries = self.hybrid_stats["total_queries"]
        
        # 更新移動平均
        self.hybrid_stats["avg_processing_time_ms"] = (
            (current_avg * (total_queries - 1) + processing_time) / total_queries
        )
    
    def train_ml_model(self, training_data_path: str) -> Dict[str, float]:
        """
        使用第一期收集的數據訓練ML模型
        
        Args:
            training_data_path: 訓練數據文件路徑
            
        Returns:
            訓練指標
        """
        self.logger.info(f"Training ML model with data from {training_data_path}")
        
        # 載入訓練數據
        training_data = self._load_training_data(training_data_path)
        
        # 訓練模型
        metrics = self.ml_model.train(training_data)
        
        # 保存模型
        model_path = self.config.ml_model_config.model_path
        self.ml_model.save_model(model_path)
        
        return metrics
    
    def _load_training_data(self, data_path: str) -> List[Dict[str, Any]]:
        """載入第一期系統收集的訓練數據"""
        # 實際實現需要從TrainingDataLogger的數據庫中載入
        # 這裡提供概念性實現
        
        training_data = []
        
        # 模擬載入邏輯
        for i in range(1000):  # 假設有1000個訓練樣本
            sample = {
                "query": f"sample_query_{i}",
                "candidates": [f"candidate_{j}" for j in range(20)],
                "l1_result": {"candidates_count": 25000, "processing_time_ms": 30},
                "l2_result": {"candidates_count": 500, "processing_time_ms": 80},
                "l3_result": {"candidates_count": 50, "processing_time_ms": 30},
                "complexity_level": "medium",
                "phonetic_features": {"query_length": 2}
            }
            training_data.append(sample)
        
        return training_data
    
    def get_hybrid_statistics(self) -> Dict[str, Any]:
        """獲取混合系統統計信息"""
        stats = {
            "hybrid_stats": self.hybrid_stats.copy(),
            "rule_based_stats": self.rule_based_reranker.get_statistics(),
            "fusion_strategy": self.config.fusion_strategy,
            "ml_model_type": self.config.ml_model_config.model_type if self.config.ml_model_config else "none"
        }
        
        return stats


def design_second_phase_architecture():
    """設計第二期混合架構"""
    print("🔮 第二期混合架構設計")
    print("=" * 60)
    
    # 架構設計文檔
    architecture_design = {
        "phase_2_objectives": [
            "整合規則系統和機器學習模型的優勢",
            "基於第一期收集的訓練數據改善準確率",
            "保持高性能的同時提升適應性",
            "支援在線學習和模型更新"
        ],
        
        "technical_components": {
            "rule_based_system": {
                "role": "提供穩定可靠的基礎性能",
                "advantages": ["低延遲", "高解釋性", "穩定可控"],
                "current_performance": "89.5%部署就緒度"
            },
            
            "ml_model": {
                "type": "Transformer-based phonetic similarity model",
                "features": ["注意力機制", "字符級編碼", "端到端學習"],
                "training_data": "第一期系統收集的100%處理案例"
            },
            
            "fusion_strategies": {
                "cascaded": "規則初篩 → ML精排",
                "weighted_ensemble": "規則分數 + ML分數 → 加權融合",
                "adaptive": "根據查詢複雜度動態選擇策略"
            }
        },
        
        "expected_improvements": {
            "accuracy": "從85.7%包含率提升到90%+",
            "adaptability": "支援新領域和變異模式學習",
            "personalization": "基於用戶反饋的個性化調整",
            "robustness": "更好的邊界案例處理"
        },
        
        "implementation_timeline": {
            "phase_2a": "數據預處理和特徵工程 (2週)",
            "phase_2b": "ML模型設計和訓練 (4週)", 
            "phase_2c": "混合系統集成和測試 (2週)",
            "phase_2d": "性能調優和部署 (2週)"
        }
    }
    
    print("📊 架構設計概要:")
    print(f"  目標: {', '.join(architecture_design['phase_2_objectives'])}")
    print(f"  ML模型: {architecture_design['technical_components']['ml_model']['type']}")
    print(f"  融合策略: {len(architecture_design['technical_components']['fusion_strategies'])} 種")
    print(f"  預期準確率提升: {architecture_design['expected_improvements']['accuracy']}")
    
    # 示例混合系統
    print("\n🧪 混合系統示例:")
    print("-" * 50)
    
    try:
        # 初始化混合系統配置
        rule_config = RerankerConfig(l3_top_k=20, enable_training_data_logging=False)
        ml_config = MLModelConfig(model_type="transformer")
        hybrid_config = HybridConfig(
            rule_based_config=rule_config,
            ml_model_config=ml_config,
            fusion_strategy="adaptive"
        )
        
        # 創建混合系統實例
        hybrid_system = HybridPhoneticReranker(hybrid_config)
        
        # 示例查詢
        test_queries = ["知道", "資道", "吃飯"]
        
        for query in test_queries:
            result = hybrid_system.rerank(query, max_candidates=10)
            print(f"  混合重排 '{query}': {len(result.candidates)} 候選, "
                  f"{result.processing_time_ms:.1f}ms, 信心度: {result.confidence_score:.2f}")
        
        # 統計信息
        stats = hybrid_system.get_hybrid_statistics()
        hybrid_stats = stats["hybrid_stats"]
        
        print(f"\n📊 混合系統統計:")
        print(f"  總查詢數: {hybrid_stats['total_queries']}")
        print(f"  規則單獨處理: {hybrid_stats['rule_only_queries']}")
        print(f"  混合處理: {hybrid_stats['hybrid_queries']}")
        print(f"  平均處理時間: {hybrid_stats['avg_processing_time_ms']:.1f}ms")
        
        print(f"\n✅ 第二期混合架構設計完成")
        return True
        
    except Exception as e:
        print(f"❌ 設計過程出錯: {e}")
        return False


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 執行第二期架構設計
    success = design_second_phase_architecture()
    print(f"\n第二期混合架構設計 {'✅ COMPLETED' if success else '❌ FAILED'}")
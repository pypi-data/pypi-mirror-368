"""
TrainingDataLogger - 機器學習訓練數據收集系統
收集100%語音重排案例，建立第二期機器學習模型訓練數據庫
"""

import json
import time
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass 
class TrainingCase:
    """單個訓練案例結構"""
    case_id: str = ""
    timestamp: float = 0.0
    query: str = ""
    query_length: int = 0
    
    # L1篩選結果
    l1_candidates_count: int = 0
    l1_processing_time_ms: float = 0.0
    
    # L2重排結果  
    l2_candidates_count: int = 0
    l2_processing_time_ms: float = 0.0
    
    # L3精排結果
    l3_candidates_count: int = 0
    l3_processing_time_ms: float = 0.0
    
    # 最終結果
    final_top_candidates: List[str] = None
    total_processing_time_ms: float = 0.0
    
    # 複雜度評估
    complexity_level: str = ""  # simple/medium/complex
    complexity_score: float = 0.0
    
    # 語音特徵
    phonetic_features: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.final_top_candidates is None:
            self.final_top_candidates = []
        if self.phonetic_features is None:
            self.phonetic_features = {}


@dataclass
class SessionSummary:
    """會話統計摘要"""
    session_id: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    total_queries: int = 0
    complexity_distribution: Dict[str, int] = None
    performance_stats: Dict[str, float] = None
    
    def __post_init__(self):
        if self.complexity_distribution is None:
            self.complexity_distribution = {"simple": 0, "medium": 0, "complex": 0}
        if self.performance_stats is None:
            self.performance_stats = {}


class TrainingDataLogger:
    """
    機器學習訓練數據收集系統
    
    功能：
    1. 記錄100%語音重排處理案例
    2. 收集完整管道的性能和結果數據
    3. 評估和分類案例複雜度
    4. 建立結構化數據庫供機器學習使用
    5. 支援數據導出和分析功能
    """
    
    def __init__(self, 
                 data_dir: str = "data/training_logs",
                 db_name: str = "phonetic_training.db",
                 enable_file_logging: bool = True,
                 enable_db_logging: bool = True):
        """
        初始化訓練數據記錄器
        
        Args:
            data_dir: 數據存儲目錄
            db_name: SQLite數據庫文件名
            enable_file_logging: 是否啟用文件記錄
            enable_db_logging: 是否啟用數據庫記錄
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / db_name
        self.enable_file_logging = enable_file_logging
        self.enable_db_logging = enable_db_logging
        
        # 當前會話
        self.session_id = self._generate_session_id()
        self.session_start_time = time.time()
        
        # 內存緩存
        self.training_cases: List[TrainingCase] = []
        self.session_stats = {
            "total_queries": 0,
            "complexity_counts": {"simple": 0, "medium": 0, "complex": 0},
            "total_processing_time": 0.0,
            "avg_l1_time": 0.0,
            "avg_l2_time": 0.0,
            "avg_l3_time": 0.0
        }
        
        # 初始化數據庫
        if self.enable_db_logging:
            self._init_database()
        
        self.logger.info(f"TrainingDataLogger initialized (Session: {self.session_id})")
    
    def _generate_session_id(self) -> str:
        """生成會話ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"
    
    def _init_database(self):
        """初始化SQLite數據庫"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 創建訓練案例表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_cases (
                    case_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    timestamp REAL,
                    query TEXT,
                    query_length INTEGER,
                    l1_candidates_count INTEGER,
                    l1_processing_time_ms REAL,
                    l2_candidates_count INTEGER,
                    l2_processing_time_ms REAL,
                    l3_candidates_count INTEGER,
                    l3_processing_time_ms REAL,
                    final_top_candidates TEXT,
                    total_processing_time_ms REAL,
                    complexity_level TEXT,
                    complexity_score REAL,
                    phonetic_features TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 創建會話摘要表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_summaries (
                    session_id TEXT PRIMARY KEY,
                    start_time REAL,
                    end_time REAL,
                    total_queries INTEGER,
                    complexity_distribution TEXT,
                    performance_stats TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 創建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON training_cases(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_complexity ON training_cases(complexity_level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_session ON training_cases(session_id)')
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def log_training_case(self, 
                         query: str,
                         l1_result: Dict[str, Any],
                         l2_result: Dict[str, Any], 
                         l3_result: Dict[str, Any],
                         phonetic_features: Dict[str, Any] = None) -> str:
        """
        記錄一個完整的訓練案例
        
        Args:
            query: 查詢詞彙
            l1_result: L1篩選結果
            l2_result: L2重排結果
            l3_result: L3精排結果
            phonetic_features: 語音特徵數據
            
        Returns:
            案例ID
        """
        # 生成唯一案例ID
        case_id = self._generate_case_id(query)
        
        # 創建訓練案例
        training_case = TrainingCase(
            case_id=case_id,
            timestamp=time.time(),
            query=query,
            query_length=len(query),
            
            l1_candidates_count=l1_result.get("candidates_count", 0),
            l1_processing_time_ms=l1_result.get("processing_time_ms", 0.0),
            
            l2_candidates_count=l2_result.get("candidates_count", 0),
            l2_processing_time_ms=l2_result.get("processing_time_ms", 0.0),
            
            l3_candidates_count=l3_result.get("candidates_count", 0),
            l3_processing_time_ms=l3_result.get("processing_time_ms", 0.0),
            
            final_top_candidates=l3_result.get("top_candidates", []),
            total_processing_time_ms=(
                l1_result.get("processing_time_ms", 0.0) +
                l2_result.get("processing_time_ms", 0.0) +
                l3_result.get("processing_time_ms", 0.0)
            ),
            
            complexity_level=l3_result.get("complexity_level", "medium"),
            complexity_score=l3_result.get("complexity_score", 0.5),
            
            phonetic_features=phonetic_features or {}
        )
        
        # 添加到內存緩存
        self.training_cases.append(training_case)
        
        # 更新會話統計
        self._update_session_stats(training_case)
        
        # 寫入數據庫
        if self.enable_db_logging:
            self._save_to_database(training_case)
        
        # 寫入文件
        if self.enable_file_logging:
            self._save_to_file(training_case)
        
        self.logger.debug(f"Training case logged: {case_id}")
        return case_id
    
    def _generate_case_id(self, query: str) -> str:
        """生成案例唯一ID"""
        timestamp = str(time.time())
        content = f"{query}_{timestamp}_{self.session_id}"
        case_hash = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"case_{case_hash}"
    
    def _update_session_stats(self, case: TrainingCase):
        """更新會話統計"""
        self.session_stats["total_queries"] += 1
        self.session_stats["complexity_counts"][case.complexity_level] += 1
        self.session_stats["total_processing_time"] += case.total_processing_time_ms
        
        # 更新平均時間
        total = self.session_stats["total_queries"]
        self.session_stats["avg_l1_time"] = (
            (self.session_stats["avg_l1_time"] * (total - 1) + case.l1_processing_time_ms) / total
        )
        self.session_stats["avg_l2_time"] = (
            (self.session_stats["avg_l2_time"] * (total - 1) + case.l2_processing_time_ms) / total
        )
        self.session_stats["avg_l3_time"] = (
            (self.session_stats["avg_l3_time"] * (total - 1) + case.l3_processing_time_ms) / total
        )
    
    def _save_to_database(self, case: TrainingCase):
        """保存案例到SQLite數據庫"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO training_cases (
                    case_id, session_id, timestamp, query, query_length,
                    l1_candidates_count, l1_processing_time_ms,
                    l2_candidates_count, l2_processing_time_ms,
                    l3_candidates_count, l3_processing_time_ms,
                    final_top_candidates, total_processing_time_ms,
                    complexity_level, complexity_score, phonetic_features
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case.case_id, self.session_id, case.timestamp,
                case.query, case.query_length,
                case.l1_candidates_count, case.l1_processing_time_ms,
                case.l2_candidates_count, case.l2_processing_time_ms,
                case.l3_candidates_count, case.l3_processing_time_ms,
                json.dumps(case.final_top_candidates, ensure_ascii=False),
                case.total_processing_time_ms,
                case.complexity_level, case.complexity_score,
                json.dumps(case.phonetic_features, ensure_ascii=False)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Database save failed: {e}")
    
    def _save_to_file(self, case: TrainingCase):
        """保存案例到JSON文件"""
        try:
            # 按日期組織文件
            date_str = datetime.fromtimestamp(case.timestamp).strftime("%Y%m%d")
            file_path = self.data_dir / f"training_cases_{date_str}.jsonl"
            
            # 追加寫入JSONL格式
            with open(file_path, 'a', encoding='utf-8') as f:
                json.dump(asdict(case), f, ensure_ascii=False)
                f.write('\n')
                
        except Exception as e:
            self.logger.error(f"File save failed: {e}")
    
    def finalize_session(self) -> SessionSummary:
        """結束當前會話並生成摘要"""
        session_end_time = time.time()
        
        # 創建會話摘要
        summary = SessionSummary(
            session_id=self.session_id,
            start_time=self.session_start_time,
            end_time=session_end_time,
            total_queries=self.session_stats["total_queries"],
            complexity_distribution=self.session_stats["complexity_counts"].copy(),
            performance_stats={
                "total_time_ms": self.session_stats["total_processing_time"],
                "avg_l1_time_ms": self.session_stats["avg_l1_time"],
                "avg_l2_time_ms": self.session_stats["avg_l2_time"],
                "avg_l3_time_ms": self.session_stats["avg_l3_time"],
                "session_duration_sec": session_end_time - self.session_start_time
            }
        )
        
        # 保存會話摘要
        if self.enable_db_logging:
            self._save_session_summary(summary)
        
        self.logger.info(f"Session finalized: {self.session_id} "
                        f"({summary.total_queries} queries)")
        
        return summary
    
    def _save_session_summary(self, summary: SessionSummary):
        """保存會話摘要到數據庫"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO session_summaries (
                    session_id, start_time, end_time, total_queries,
                    complexity_distribution, performance_stats
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                summary.session_id, summary.start_time, summary.end_time,
                summary.total_queries,
                json.dumps(summary.complexity_distribution, ensure_ascii=False),
                json.dumps(summary.performance_stats, ensure_ascii=False)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Session summary save failed: {e}")
    
    def export_training_data(self, 
                           output_path: str,
                           format: str = "json",
                           complexity_filter: Optional[str] = None,
                           limit: Optional[int] = None) -> int:
        """
        導出訓練數據
        
        Args:
            output_path: 輸出文件路徑
            format: 輸出格式 (json/csv)
            complexity_filter: 複雜度篩選 (simple/medium/complex)
            limit: 導出數量限制
            
        Returns:
            導出的記錄數
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            # 構建查詢
            query = "SELECT * FROM training_cases"
            params = []
            
            if complexity_filter:
                query += " WHERE complexity_level = ?"
                params.append(complexity_filter)
            
            query += " ORDER BY timestamp DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            conn.close()
            
            # 導出數據
            if format.lower() == "json":
                data = [dict(zip(columns, row)) for row in rows]
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            elif format.lower() == "csv":
                import pandas as pd
                df = pd.DataFrame(rows, columns=columns)
                df.to_csv(output_path, index=False, encoding='utf-8')
            
            self.logger.info(f"Exported {len(rows)} records to {output_path}")
            return len(rows)
            
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取訓練數據統計信息"""
        stats = {
            "session_id": self.session_id,
            "session_stats": self.session_stats.copy(),
            "memory_cache_size": len(self.training_cases),
            "data_dir": str(self.data_dir),
            "db_path": str(self.db_path),
            "logging_enabled": {
                "file": self.enable_file_logging,
                "database": self.enable_db_logging
            }
        }
        
        # 數據庫統計
        if self.enable_db_logging and self.db_path.exists():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM training_cases")
                stats["total_cases_in_db"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT session_id) FROM training_cases")
                stats["total_sessions"] = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT complexity_level, COUNT(*) 
                    FROM training_cases 
                    GROUP BY complexity_level
                """)
                complexity_dist = dict(cursor.fetchall())
                stats["db_complexity_distribution"] = complexity_dist
                
                conn.close()
                
            except Exception as e:
                stats["db_error"] = str(e)
        
        return stats


def test_training_data_logger():
    """測試TrainingDataLogger功能"""
    print("🧪 測試TrainingDataLogger功能")
    print("=" * 50)
    
    try:
        # 初始化數據記錄器
        logger = TrainingDataLogger(
            data_dir="data/training_logs",
            db_name="test_training.db"
        )
        
        # 模擬訓練案例
        test_cases = [
            ("知道", "simple", 0.9),
            ("資道", "medium", 0.6),
            ("吃飯", "simple", 0.85),
            ("安全", "complex", 0.3),
        ]
        
        print("📊 記錄訓練案例:")
        print("-" * 40)
        
        for query, complexity, score in test_cases:
            # 模擬L1/L2/L3結果
            l1_result = {
                "candidates_count": 2500,
                "processing_time_ms": 85.0
            }
            
            l2_result = {
                "candidates_count": 500,
                "processing_time_ms": 45.0
            }
            
            l3_result = {
                "candidates_count": 10,
                "processing_time_ms": 8.0,
                "top_candidates": [query, f"{query}_1", f"{query}_2"],
                "complexity_level": complexity,
                "complexity_score": score
            }
            
            phonetic_features = {
                "query_length": len(query),
                "has_tone_variation": complexity != "simple"
            }
            
            case_id = logger.log_training_case(
                query, l1_result, l2_result, l3_result, phonetic_features
            )
            
            print(f"  記錄案例: {query} → {case_id} ({complexity})")
        
        # 獲取統計信息
        print("\n📊 數據記錄器統計:")
        print("-" * 40)
        
        stats = logger.get_statistics()
        session_stats = stats["session_stats"]
        
        print(f"會話ID: {stats['session_id']}")
        print(f"總查詢數: {session_stats['total_queries']}")
        print(f"內存緩存: {stats['memory_cache_size']} 條目")
        print(f"數據庫總案例: {stats.get('total_cases_in_db', 'N/A')}")
        
        print(f"\n複雜度分佈:")
        for level, count in session_stats["complexity_counts"].items():
            print(f"  {level}: {count}")
        
        print(f"\n平均處理時間:")
        print(f"  L1: {session_stats['avg_l1_time']:.1f}ms")
        print(f"  L2: {session_stats['avg_l2_time']:.1f}ms")  
        print(f"  L3: {session_stats['avg_l3_time']:.1f}ms")
        
        # 結束會話
        print("\n📊 結束會話:")
        print("-" * 40)
        
        summary = logger.finalize_session()
        print(f"會話時長: {summary.performance_stats['session_duration_sec']:.1f}秒")
        print(f"總處理時間: {summary.performance_stats['total_time_ms']:.1f}ms")
        
        # 測試數據導出
        print("\n📊 測試數據導出:")
        print("-" * 40)
        
        export_path = "data/training_logs/test_export.json"
        exported_count = logger.export_training_data(export_path, format="json")
        print(f"導出記錄數: {exported_count}")
        
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
    success = test_training_data_logger()
    print(f"\n測試 {'✅ PASSED' if success else '❌ FAILED'}")
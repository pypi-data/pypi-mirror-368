"""
Core constants for TWGY_V3 system
Centralizes all magic numbers, thresholds, and configuration values
"""

from typing import Dict, List, Final


# Performance Constants
class Performance:
    """Performance-related constants"""
    MAX_PROCESSING_TIME_MS: Final[float] = 250.0
    DEFAULT_CACHE_SIZE: Final[int] = 10000
    DEFAULT_CACHE_TTL_SECONDS: Final[int] = 3600
    DEFAULT_BATCH_SIZE: Final[int] = 32
    DEFAULT_NUM_WORKERS: Final[int] = 4
    MEMORY_WARNING_THRESHOLD_MB: Final[int] = 500


# Filter Constants
class Filters:
    """Filter pipeline constants"""
    L1_DEFAULT_USE_FULL_DICT: Final[bool] = True
    L1_ENABLE_CACHE: Final[bool] = True
    
    L2_DEFAULT_TOP_K: Final[int] = 500
    L2_ENABLE_CACHE: Final[bool] = True
    
    L3_DEFAULT_TOP_K: Final[int] = 50
    L3_ENABLE_CACHE: Final[bool] = True
    
    # Processing thresholds
    COMPLEXITY_SIMPLE_L1_THRESHOLD: Final[int] = 1000
    COMPLEXITY_SIMPLE_L2_THRESHOLD: Final[int] = 100
    COMPLEXITY_MEDIUM_L1_THRESHOLD: Final[int] = 10000
    COMPLEXITY_MEDIUM_L2_THRESHOLD: Final[int] = 300


# Similarity Constants  
class Similarity:
    """Similarity calculation constants"""
    DEFAULT_THRESHOLD: Final[float] = 0.7
    MIN_SIMILARITY: Final[float] = 0.0
    MAX_SIMILARITY: Final[float] = 1.0
    
    # Weight distributions
    FIRST_CHAR_WEIGHT: Final[float] = 0.4
    LAST_CHAR_WEIGHT: Final[float] = 0.4
    MIDDLE_CHARS_WEIGHT: Final[float] = 0.2
    
    # Phonetic weights
    TONE_WEIGHT: Final[float] = 0.3
    INITIAL_WEIGHT: Final[float] = 0.4
    FINAL_WEIGHT: Final[float] = 0.3
    
    # Similarity scores for different relationships
    EXACT_MATCH_SCORE: Final[float] = 1.0
    SAME_GROUP_SCORE: Final[float] = 0.8
    RELATED_GROUP_SCORE: Final[float] = 0.7
    NO_MATCH_SCORE: Final[float] = 0.0


# Phonetic Constants
class Phonetic:
    """Phonetic processing constants"""
    # Consonant groups (聲母分組)
    CONSONANT_GROUPS: Final[Dict[str, List[str]]] = {
        "雙唇音": ["ㄅ", "ㄆ", "ㄇ", "ㄈ"],
        "舌尖前音": ["ㄗ", "ㄘ", "ㄙ"],
        "舌尖中音": ["ㄉ", "ㄊ", "ㄋ", "ㄌ"],
        "舌尖後音": ["ㄓ", "ㄔ", "ㄕ", "ㄖ"],
        "舌面音": ["ㄐ", "ㄑ", "ㄒ"],
        "舌根音": ["ㄍ", "ㄎ", "ㄏ"],
        "零聲母": [""]
    }
    
    # Finals groups (韻母分組)
    FINALS_GROUPS: Final[Dict[str, List[str]]] = {
        "開口呼": ["ㄚ", "ㄛ", "ㄜ", "ㄝ", "ㄞ", "ㄟ", "ㄠ", "ㄡ", "ㄢ", "ㄣ", "ㄤ", "ㄥ", "ㄦ"],
        "齊齒呼": ["ㄧ", "ㄧㄚ", "ㄧㄛ", "ㄧㄝ", "ㄧㄞ", "ㄧㄠ", "ㄧㄡ", "ㄧㄢ", "ㄧㄣ", "ㄧㄤ", "ㄧㄥ"],
        "合口呼": ["ㄨ", "ㄨㄚ", "ㄨㄛ", "ㄨㄞ", "ㄨㄟ", "ㄨㄢ", "ㄨㄣ", "ㄨㄤ", "ㄨㄥ"],
        "撮口呼": ["ㄩ", "ㄩㄝ", "ㄩㄢ", "ㄩㄣ", "ㄩㄥ"]
    }
    
    # Special variant pairs
    FLAT_RETROFLEX_PAIRS: Final[List[tuple]] = [
        ("舌尖前音", "舌尖後音"),  # z/c/s vs zh/ch/sh
    ]
    
    LATERAL_NASAL_PAIRS: Final[List[tuple]] = [
        ("ㄋ", "ㄌ"),  # n vs l confusion
    ]
    
    NASAL_PAIRS: Final[List[tuple]] = [
        ("ㄢ", "ㄤ"),  # an vs ang
        ("ㄣ", "ㄥ"),  # en vs eng
    ]


# System Constants
class System:
    """System-level constants"""
    VERSION: Final[str] = "3.0.0"
    DEFAULT_ENCODING: Final[str] = "utf-8"
    
    # File paths (relative to project root)
    DEFAULT_DATA_DIR: Final[str] = "data"
    DEFAULT_DICT_DIR: Final[str] = "data/super_dicts"
    DEFAULT_MODEL_DIR: Final[str] = "data/models"
    DEFAULT_LOG_DIR: Final[str] = "logs"
    
    # Default file names
    SUPER_DICT_COMBINED: Final[str] = "super_dict_combined.json"
    SUPER_DICT_REVERSED: Final[str] = "super_dict_reversed.json"
    ERROR_CANDIDATES_FILE: Final[str] = "error_candidates_ok.csv"
    
    # Logging defaults
    DEFAULT_LOG_LEVEL: Final[str] = "INFO"
    DEFAULT_LOG_FORMAT: Final[str] = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    MAX_LOG_FILE_SIZE: Final[str] = "10MB"
    LOG_RETENTION: Final[str] = "7 days"


# Validation Constants
class Validation:
    """Validation and constraints constants"""
    MIN_QUERY_LENGTH: Final[int] = 1
    MAX_QUERY_LENGTH: Final[int] = 100
    MIN_CANDIDATES_COUNT: Final[int] = 0
    MAX_CANDIDATES_COUNT: Final[int] = 10000
    
    # Character validation
    CJK_UNIFIED_IDEOGRAPHS_START: Final[int] = 0x4e00
    CJK_UNIFIED_IDEOGRAPHS_END: Final[int] = 0x9fff
    
    # Performance validation
    MAX_ACCEPTABLE_PROCESSING_TIME_MS: Final[float] = 1000.0
    MIN_CACHE_HIT_RATE: Final[float] = 0.3
    MAX_MEMORY_USAGE_MB: Final[int] = 1000


# Error Messages
class ErrorMessages:
    """Standardized error messages"""
    # Initialization errors
    COMPONENT_INIT_FAILED: Final[str] = "Failed to initialize component: {component}"
    DICTIONARY_LOAD_FAILED: Final[str] = "Failed to load dictionary from: {path}"
    CONFIG_VALIDATION_FAILED: Final[str] = "Configuration validation failed: {errors}"
    
    # Runtime errors
    QUERY_VALIDATION_FAILED: Final[str] = "Query validation failed: {query}"
    FILTER_PROCESSING_FAILED: Final[str] = "Filter processing failed for query: {query}"
    SIMILARITY_CALCULATION_FAILED: Final[str] = "Similarity calculation failed: {word1} vs {word2}"
    
    # Resource errors
    FILE_NOT_FOUND: Final[str] = "Required file not found: {path}"
    INSUFFICIENT_MEMORY: Final[str] = "Insufficient memory for operation: {operation}"
    PROCESSING_TIMEOUT: Final[str] = "Processing timeout after {timeout}ms for query: {query}"
    
    # Data errors
    INVALID_PHONETIC_DATA: Final[str] = "Invalid phonetic data: {data}"
    CORRUPTED_DICTIONARY: Final[str] = "Dictionary file appears corrupted: {path}"
    MISSING_REQUIRED_FIELD: Final[str] = "Missing required field: {field} in {context}"


# Success Messages
class SuccessMessages:
    """Standardized success messages"""
    COMPONENT_INITIALIZED: Final[str] = "{component} initialized successfully"
    DICTIONARY_LOADED: Final[str] = "Dictionary loaded: {count:,} entries from {path}"
    QUERY_PROCESSED: Final[str] = "Query processed: {query} → {candidates} candidates in {time:.1f}ms"
    CACHE_CLEARED: Final[str] = "Cache cleared: {cache_type}"
    SESSION_FINALIZED: Final[str] = "Session finalized: {session_id}"
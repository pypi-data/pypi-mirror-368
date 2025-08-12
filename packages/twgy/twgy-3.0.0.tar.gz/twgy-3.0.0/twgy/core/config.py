"""
System configuration for TWGY_V3
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
import os


@dataclass
class PhoneticConfig:
    """Configuration for phonetic processing"""
    use_bopomofo: bool = True
    use_pinyin: bool = True
    tone_weight: float = 0.3
    initial_weight: float = 0.4
    final_weight: float = 0.3
    dialect_support: bool = True


@dataclass
class SimilarityConfig:
    """Configuration for similarity calculation"""
    default_threshold: float = 0.7
    first_char_weight: float = 0.4
    last_char_weight: float = 0.4
    middle_chars_weight: float = 0.2
    length_penalty_factor: float = 0.1
    max_length_ratio: float = 2.0


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization"""
    use_hardware_acceleration: bool = True
    device: str = "auto"  # auto, cpu, cuda, mps
    batch_size: int = 32
    cache_size: int = 10000
    enable_cache: bool = True
    num_workers: int = 4


@dataclass
class ComparisonConfig:
    """Configuration for comparison strategies"""
    direct_comparison_threshold: int = 0  # same length
    sliding_window_threshold: int = 1     # length diff ±1
    anchor_based_threshold: int = 3       # length diff ±2-3
    edit_distance_threshold: int = 999    # length diff >3
    
    # Strategy weights
    strategy_weights: Dict[str, float] = field(default_factory=lambda: {
        "direct": 1.0,
        "sliding_window": 0.9,
        "anchor_based": 0.8,
        "edit_distance": 0.7
    })


@dataclass
class DataConfig:
    """Configuration for data sources"""
    data_dir: Path = field(default_factory=lambda: Path("data"))
    dictionaries_dir: Path = field(default_factory=lambda: Path("data/dictionaries"))
    phonetic_tables_dir: Path = field(default_factory=lambda: Path("data/phonetic_tables"))
    models_dir: Path = field(default_factory=lambda: Path("data/models"))
    
    # Dictionary files
    error_correction_dict: str = "error_candidates_ok.csv"
    moedict_file: Optional[str] = None
    custom_dict_files: List[str] = field(default_factory=list)


@dataclass
class LoggingConfig:
    """Configuration for logging"""
    level: str = "INFO"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    file_path: Optional[str] = None
    max_file_size: str = "10MB"
    retention: str = "7 days"


@dataclass
class SystemConfig:
    """Main system configuration"""
    phonetic: PhoneticConfig = field(default_factory=PhoneticConfig)
    similarity: SimilarityConfig = field(default_factory=SimilarityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    comparison: ComparisonConfig = field(default_factory=ComparisonConfig)
    data: DataConfig = field(default_factory=DataConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    @classmethod
    def from_file(cls, config_path: str) -> "SystemConfig":
        """Load configuration from YAML file"""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return cls.from_dict(config_data)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "SystemConfig":
        """Create configuration from dictionary"""
        config = cls()
        
        if "phonetic" in config_dict:
            config.phonetic = PhoneticConfig(**config_dict["phonetic"])
        
        if "similarity" in config_dict:
            config.similarity = SimilarityConfig(**config_dict["similarity"])
        
        if "performance" in config_dict:
            config.performance = PerformanceConfig(**config_dict["performance"])
        
        if "comparison" in config_dict:
            comparison_data = config_dict["comparison"]
            if "strategy_weights" not in comparison_data:
                comparison_data["strategy_weights"] = ComparisonConfig().strategy_weights
            config.comparison = ComparisonConfig(**comparison_data)
        
        if "data" in config_dict:
            data_config = config_dict["data"]
            # Convert string paths to Path objects
            for key in ["data_dir", "dictionaries_dir", "phonetic_tables_dir", "models_dir"]:
                if key in data_config:
                    data_config[key] = Path(data_config[key])
            config.data = DataConfig(**data_config)
        
        if "logging" in config_dict:
            config.logging = LoggingConfig(**config_dict["logging"])
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        def convert_dataclass(obj):
            if hasattr(obj, '__dataclass_fields__'):
                result = {}
                for field_name, field_def in obj.__dataclass_fields__.items():
                    value = getattr(obj, field_name)
                    if isinstance(value, Path):
                        result[field_name] = str(value)
                    elif hasattr(value, '__dataclass_fields__'):
                        result[field_name] = convert_dataclass(value)
                    else:
                        result[field_name] = value
                return result
            return obj
        
        return convert_dataclass(self)
    
    def save_to_file(self, config_path: str):
        """Save configuration to YAML file"""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
    
    def update_from_env(self):
        """Update configuration from environment variables"""
        # Performance settings
        if "TWGY_DEVICE" in os.environ:
            self.performance.device = os.environ["TWGY_DEVICE"]
        
        if "TWGY_BATCH_SIZE" in os.environ:
            self.performance.batch_size = int(os.environ["TWGY_BATCH_SIZE"])
        
        if "TWGY_CACHE_SIZE" in os.environ:
            self.performance.cache_size = int(os.environ["TWGY_CACHE_SIZE"])
        
        # Similarity settings
        if "TWGY_THRESHOLD" in os.environ:
            self.similarity.default_threshold = float(os.environ["TWGY_THRESHOLD"])
        
        # Logging settings
        if "TWGY_LOG_LEVEL" in os.environ:
            self.logging.level = os.environ["TWGY_LOG_LEVEL"]
        
        if "TWGY_LOG_FILE" in os.environ:
            self.logging.file_path = os.environ["TWGY_LOG_FILE"]
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate weights sum to reasonable values
        phonetic_weights = (
            self.phonetic.tone_weight + 
            self.phonetic.initial_weight + 
            self.phonetic.final_weight
        )
        if abs(phonetic_weights - 1.0) > 0.1:
            errors.append(f"Phonetic weights sum to {phonetic_weights:.2f}, should be close to 1.0")
        
        similarity_weights = (
            self.similarity.first_char_weight +
            self.similarity.last_char_weight +
            self.similarity.middle_chars_weight
        )
        if abs(similarity_weights - 1.0) > 0.1:
            errors.append(f"Similarity weights sum to {similarity_weights:.2f}, should be close to 1.0")
        
        # Validate thresholds
        if not 0.0 <= self.similarity.default_threshold <= 1.0:
            errors.append("Default threshold must be between 0.0 and 1.0")
        
        # Validate paths
        if not self.data.data_dir.exists():
            errors.append(f"Data directory does not exist: {self.data.data_dir}")
        
        # Validate performance settings
        if self.performance.batch_size <= 0:
            errors.append("Batch size must be positive")
        
        if self.performance.cache_size <= 0:
            errors.append("Cache size must be positive")
        
        return errors


def load_default_config() -> SystemConfig:
    """Load default system configuration"""
    config = SystemConfig()
    config.update_from_env()
    return config


def load_config(config_path: Optional[str] = None) -> SystemConfig:
    """Load configuration from file or use default"""
    if config_path and Path(config_path).exists():
        config = SystemConfig.from_file(config_path)
    else:
        config = load_default_config()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return config
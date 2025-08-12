"""
Unit tests for system configuration
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from src.core.config import (
    SystemConfig, 
    PhoneticConfig, 
    SimilarityConfig,
    PerformanceConfig,
    load_default_config,
    load_config
)


class TestSystemConfig:
    """Test SystemConfig class"""
    
    def test_default_config_creation(self):
        """Test creating default configuration"""
        config = SystemConfig()
        
        assert isinstance(config.phonetic, PhoneticConfig)
        assert isinstance(config.similarity, SimilarityConfig)
        assert isinstance(config.performance, PerformanceConfig)
        
        # Test default values
        assert config.phonetic.use_bopomofo is True
        assert config.similarity.default_threshold == 0.7
        assert config.performance.batch_size == 32
    
    def test_config_from_dict(self):
        """Test creating configuration from dictionary"""
        config_dict = {
            "phonetic": {
                "use_bopomofo": False,
                "tone_weight": 0.5
            },
            "similarity": {
                "default_threshold": 0.8
            }
        }
        
        config = SystemConfig.from_dict(config_dict)
        
        assert config.phonetic.use_bopomofo is False
        assert config.phonetic.tone_weight == 0.5
        assert config.similarity.default_threshold == 0.8
        # Other values should be defaults
        assert config.phonetic.use_pinyin is True
    
    def test_config_to_dict(self):
        """Test converting configuration to dictionary"""
        config = SystemConfig()
        config.phonetic.tone_weight = 0.5
        
        config_dict = config.to_dict()
        
        assert config_dict["phonetic"]["tone_weight"] == 0.5
        assert config_dict["similarity"]["default_threshold"] == 0.7
    
    def test_config_file_operations(self):
        """Test saving and loading configuration files"""
        config = SystemConfig()
        config.phonetic.tone_weight = 0.6
        config.similarity.default_threshold = 0.9
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            # Save configuration
            config.save_to_file(config_path)
            
            # Load configuration
            loaded_config = SystemConfig.from_file(config_path)
            
            assert loaded_config.phonetic.tone_weight == 0.6
            assert loaded_config.similarity.default_threshold == 0.9
            
        finally:
            Path(config_path).unlink()
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = SystemConfig()
        
        # Valid configuration should pass
        errors = config.validate()
        assert len(errors) == 0
        
        # Invalid weights should fail
        config.phonetic.tone_weight = 0.8
        config.phonetic.initial_weight = 0.8
        config.phonetic.final_weight = 0.8
        
        errors = config.validate()
        assert len(errors) > 0
        assert "Phonetic weights" in errors[0]
    
    def test_load_default_config(self):
        """Test loading default configuration"""
        config = load_default_config()
        
        assert isinstance(config, SystemConfig)
        assert config.phonetic.use_bopomofo is True
        assert config.similarity.default_threshold == 0.7
    
    def test_load_config_with_file(self):
        """Test loading configuration with file"""
        config_dict = {
            "phonetic": {"tone_weight": 0.5},
            "similarity": {"default_threshold": 0.8}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            config_path = f.name
        
        try:
            config = load_config(config_path)
            
            assert config.phonetic.tone_weight == 0.5
            assert config.similarity.default_threshold == 0.8
            
        finally:
            Path(config_path).unlink()
    
    def test_load_config_without_file(self):
        """Test loading configuration without file (should use default)"""
        config = load_config("nonexistent_file.yaml")
        
        assert isinstance(config, SystemConfig)
        assert config.phonetic.tone_weight == 0.3  # default value


class TestPhoneticConfig:
    """Test PhoneticConfig class"""
    
    def test_default_values(self):
        """Test default configuration values"""
        config = PhoneticConfig()
        
        assert config.use_bopomofo is True
        assert config.use_pinyin is True
        assert config.tone_weight == 0.3
        assert config.initial_weight == 0.4
        assert config.final_weight == 0.3
        assert config.dialect_support is True


class TestSimilarityConfig:
    """Test SimilarityConfig class"""
    
    def test_default_values(self):
        """Test default configuration values"""
        config = SimilarityConfig()
        
        assert config.default_threshold == 0.7
        assert config.first_char_weight == 0.4
        assert config.last_char_weight == 0.4
        assert config.middle_chars_weight == 0.2
        assert config.length_penalty_factor == 0.1
        assert config.max_length_ratio == 2.0


class TestPerformanceConfig:
    """Test PerformanceConfig class"""
    
    def test_default_values(self):
        """Test default configuration values"""
        config = PerformanceConfig()
        
        assert config.use_hardware_acceleration is True
        assert config.device == "auto"
        assert config.batch_size == 32
        assert config.cache_size == 10000
        assert config.enable_cache is True
        assert config.num_workers == 4
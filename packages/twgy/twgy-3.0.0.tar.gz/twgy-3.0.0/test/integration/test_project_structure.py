"""
Integration tests for project structure and basic functionality
"""

import pytest
import sys
from pathlib import Path
import subprocess
import json

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


class TestProjectStructure:
    """Test project structure and basic setup"""
    
    def test_project_directories_exist(self):
        """Test that all required directories exist"""
        required_dirs = [
            "src",
            "src/core",
            "src/phonetic", 
            "src/similarity",
            "src/comparison",
            "src/api",
            "src/utils",
            "data",
            "data/dictionaries",
            "data/phonetic_tables",
            "data/test_data",
            "data/models",
            "test",
            "test/unit",
            "test/integration",
            "test/performance",
            "test/accuracy",
            "doc",
            "doc/api",
            "doc/user_guide",
            "doc/technical",
            "doc/examples",
            "scripts",
            "docker",
        ]
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            assert full_path.exists(), f"Required directory missing: {dir_path}"
            assert full_path.is_dir(), f"Path is not a directory: {dir_path}"
    
    def test_required_files_exist(self):
        """Test that required files exist"""
        required_files = [
            "README.md",
            "requirements.txt",
            "pyproject.toml",
            ".gitignore",
            "Dockerfile",
            "docker-compose.yml",
            "src/__init__.py",
            "src/core/__init__.py",
            "src/core/config.py",
            "src/core/exceptions.py",
            "src/cli.py",
            "scripts/setup_data.py",
            "data/phonetic_tables/bopomofo_classification.yaml",
            "doc/current_phonetic_comparison_methods_analysis.md",
            "doc/user_guide/quick_start.md",
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Required file missing: {file_path}"
            assert full_path.is_file(), f"Path is not a file: {file_path}"
    
    def test_data_files_exist(self):
        """Test that data files are properly copied"""
        data_files = [
            "data/dictionaries/error_candidates_ok.csv",
        ]
        
        for file_path in data_files:
            full_path = project_root / file_path
            if full_path.exists():
                assert full_path.is_file(), f"Data path is not a file: {file_path}"
                assert full_path.stat().st_size > 0, f"Data file is empty: {file_path}"
    
    def test_kiro_specs_exist(self):
        """Test that Kiro specs are properly set up"""
        kiro_files = [
            ".kiro/specs/advanced-phonetic-similarity/requirements.md",
        ]
        
        for file_path in kiro_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Kiro spec file missing: {file_path}"
            assert full_path.is_file(), f"Kiro spec path is not a file: {file_path}"


class TestBasicImports:
    """Test basic imports work correctly"""
    
    def test_core_imports(self):
        """Test core module imports"""
        try:
            from src.core.config import SystemConfig, load_default_config
            from src.core.exceptions import TWGYError, PhoneticError
            
            # Test basic instantiation
            config = SystemConfig()
            assert config is not None
            
            default_config = load_default_config()
            assert default_config is not None
            
        except ImportError as e:
            pytest.fail(f"Failed to import core modules: {e}")
    
    def test_config_functionality(self):
        """Test configuration functionality"""
        from src.core.config import SystemConfig
        
        config = SystemConfig()
        
        # Test basic properties
        assert hasattr(config, 'phonetic')
        assert hasattr(config, 'similarity')
        assert hasattr(config, 'performance')
        assert hasattr(config, 'data')
        
        # Test validation
        errors = config.validate()
        assert isinstance(errors, list)
        
        # Test serialization
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert 'phonetic' in config_dict
        assert 'similarity' in config_dict


class TestCLIBasics:
    """Test CLI basic functionality"""
    
    def test_cli_help(self):
        """Test CLI help command"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "--help"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            assert result.returncode == 0, f"CLI help failed: {result.stderr}"
            assert "TWGY_V3" in result.stdout
            assert "similarity" in result.stdout
            
        except subprocess.TimeoutExpired:
            pytest.fail("CLI help command timed out")
        except Exception as e:
            pytest.fail(f"CLI help command failed: {e}")
    
    def test_cli_system_info(self):
        """Test CLI system info command"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "system-info"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Should succeed or fail gracefully
            if result.returncode == 0:
                # Try to parse JSON output
                try:
                    info = json.loads(result.stdout)
                    assert "system" in info
                    assert info["system"] == "TWGY_V3"
                except json.JSONDecodeError:
                    pytest.fail("CLI system-info output is not valid JSON")
            else:
                # If it fails, it should be due to missing dependencies or data
                assert "error" in result.stderr.lower() or "not found" in result.stderr.lower()
                
        except subprocess.TimeoutExpired:
            pytest.fail("CLI system-info command timed out")
        except Exception as e:
            pytest.fail(f"CLI system-info command failed: {e}")


class TestDataValidation:
    """Test data validation functionality"""
    
    def test_phonetic_tables_structure(self):
        """Test phonetic tables have correct structure"""
        import yaml
        
        phonetic_table_path = project_root / "data/phonetic_tables/bopomofo_classification.yaml"
        
        if phonetic_table_path.exists():
            with open(phonetic_table_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Test required sections
            required_sections = ['initials', 'finals', 'tones']
            for section in required_sections:
                assert section in data, f"Missing section in phonetic table: {section}"
            
            # Test initials structure
            assert isinstance(data['initials'], dict)
            for row_name, row_data in data['initials'].items():
                assert 'name' in row_data
                assert 'phonemes' in row_data
                assert isinstance(row_data['phonemes'], list)
    
    def test_dictionary_file_format(self):
        """Test dictionary file format"""
        dict_path = project_root / "data/dictionaries/error_candidates_ok.csv"
        
        if dict_path.exists():
            try:
                import pandas as pd
                df = pd.read_csv(dict_path, header=None)
                
                # Should have at least 2 columns
                assert df.shape[1] >= 2, "Dictionary file should have at least 2 columns"
                
                # Should have some data
                assert df.shape[0] > 0, "Dictionary file should not be empty"
                
                # Check for obvious issues
                non_null_rows = df.dropna()
                assert non_null_rows.shape[0] > 0, "Dictionary file should have valid entries"
                
            except Exception as e:
                pytest.fail(f"Failed to validate dictionary file: {e}")


class TestDocumentation:
    """Test documentation completeness"""
    
    def test_readme_content(self):
        """Test README has essential content"""
        readme_path = project_root / "README.md"
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        essential_sections = [
            "TWGY_V3",
            "安裝",
            "使用",
            "API",
            "性能",
        ]
        
        for section in essential_sections:
            assert section in content, f"README missing essential section: {section}"
    
    def test_quick_start_guide(self):
        """Test quick start guide completeness"""
        guide_path = project_root / "doc/user_guide/quick_start.md"
        
        with open(guide_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        essential_sections = [
            "安裝",
            "基本使用",
            "配置",
            "故障排除",
        ]
        
        for section in essential_sections:
            assert section in content, f"Quick start guide missing section: {section}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
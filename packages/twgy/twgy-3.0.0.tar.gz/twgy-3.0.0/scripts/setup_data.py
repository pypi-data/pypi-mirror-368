#!/usr/bin/env python3
"""
Data setup script for TWGY_V3
Initializes data directories and validates data files
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import yaml
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import load_default_config
from core.exceptions import DataError


def setup_directories(config) -> None:
    """Create necessary data directories"""
    directories = [
        config.data.data_dir,
        config.data.dictionaries_dir,
        config.data.phonetic_tables_dir,
        config.data.models_dir,
        Path("data/test_data"),
        Path("data/cache"),
        Path("logs"),
        Path("output"),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def validate_dictionary_file(file_path: Path) -> Dict[str, Any]:
    """Validate dictionary CSV file"""
    if not file_path.exists():
        raise DataError(f"Dictionary file not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path, header=None, names=['error', 'correction'])
        
        # Basic validation
        total_rows = len(df)
        valid_rows = df.dropna().shape[0]
        duplicate_rows = df.duplicated().sum()
        
        # Check for empty values
        empty_errors = df['error'].isna().sum()
        empty_corrections = df['correction'].isna().sum()
        
        validation_result = {
            'file_path': str(file_path),
            'total_rows': total_rows,
            'valid_rows': valid_rows,
            'duplicate_rows': duplicate_rows,
            'empty_errors': empty_errors,
            'empty_corrections': empty_corrections,
            'is_valid': valid_rows > 0 and empty_errors == 0 and empty_corrections == 0
        }
        
        return validation_result
        
    except Exception as e:
        raise DataError(f"Error validating dictionary file {file_path}: {e}")


def validate_phonetic_tables(tables_dir: Path) -> List[Dict[str, Any]]:
    """Validate phonetic classification tables"""
    results = []
    
    for yaml_file in tables_dir.glob("*.yaml"):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Basic structure validation
            required_sections = ['initials', 'finals', 'tones']
            missing_sections = [section for section in required_sections if section not in data]
            
            validation_result = {
                'file_path': str(yaml_file),
                'has_initials': 'initials' in data,
                'has_finals': 'finals' in data,
                'has_tones': 'tones' in data,
                'missing_sections': missing_sections,
                'is_valid': len(missing_sections) == 0
            }
            
            results.append(validation_result)
            
        except Exception as e:
            results.append({
                'file_path': str(yaml_file),
                'error': str(e),
                'is_valid': False
            })
    
    return results


def check_test_data(test_data_dir: Path) -> Dict[str, Any]:
    """Check test data availability"""
    json_files = list(test_data_dir.glob("*.json"))
    txt_files = list(test_data_dir.glob("*.txt"))
    
    return {
        'test_data_dir': str(test_data_dir),
        'json_files_count': len(json_files),
        'txt_files_count': len(txt_files),
        'sample_files': [f.name for f in json_files[:5]],  # First 5 files
        'has_test_data': len(json_files) > 0 or len(txt_files) > 0
    }


def generate_sample_config(output_path: Path) -> None:
    """Generate sample configuration file"""
    config = load_default_config()
    config.save_to_file(output_path)
    print(f"✓ Generated sample configuration: {output_path}")


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup TWGY_V3 data and configuration")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--generate-config", help="Generate sample configuration file")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing data")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        if args.config:
            from core.config import load_config
            config = load_config(args.config)
        else:
            config = load_default_config()
        
        print("🚀 TWGY_V3 Data Setup")
        print("=" * 50)
        
        # Generate sample configuration if requested
        if args.generate_config:
            generate_sample_config(Path(args.generate_config))
            return
        
        # Setup directories
        if not args.validate_only:
            print("\n📁 Setting up directories...")
            setup_directories(config)
        
        # Validate dictionary files
        print("\n📚 Validating dictionary files...")
        dict_file = config.data.dictionaries_dir / config.data.error_correction_dict
        
        if dict_file.exists():
            dict_validation = validate_dictionary_file(dict_file)
            
            if dict_validation['is_valid']:
                print(f"✓ Dictionary file is valid: {dict_validation['valid_rows']} entries")
            else:
                print(f"⚠️  Dictionary file has issues:")
                print(f"   - Empty errors: {dict_validation['empty_errors']}")
                print(f"   - Empty corrections: {dict_validation['empty_corrections']}")
                print(f"   - Duplicate rows: {dict_validation['duplicate_rows']}")
            
            if args.verbose:
                print(f"   Total rows: {dict_validation['total_rows']}")
                print(f"   Valid rows: {dict_validation['valid_rows']}")
        else:
            print(f"⚠️  Dictionary file not found: {dict_file}")
            print("   Please copy error_candidates_ok.csv to data/dictionaries/")
        
        # Validate phonetic tables
        print("\n🔤 Validating phonetic tables...")
        phonetic_validations = validate_phonetic_tables(config.data.phonetic_tables_dir)
        
        for validation in phonetic_validations:
            if validation['is_valid']:
                print(f"✓ Phonetic table is valid: {Path(validation['file_path']).name}")
            else:
                print(f"⚠️  Phonetic table has issues: {Path(validation['file_path']).name}")
                if 'missing_sections' in validation:
                    print(f"   Missing sections: {validation['missing_sections']}")
                if 'error' in validation:
                    print(f"   Error: {validation['error']}")
        
        # Check test data
        print("\n🧪 Checking test data...")
        test_data_info = check_test_data(Path("data/test_data"))
        
        if test_data_info['has_test_data']:
            print(f"✓ Test data available:")
            print(f"   - JSON files: {test_data_info['json_files_count']}")
            print(f"   - TXT files: {test_data_info['txt_files_count']}")
            
            if args.verbose and test_data_info['sample_files']:
                print(f"   Sample files: {', '.join(test_data_info['sample_files'])}")
        else:
            print("⚠️  No test data found in data/test_data/")
            print("   Consider copying some JSON/TXT files for testing")
        
        print("\n✅ Setup completed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run tests: python -m pytest test/")
        print("3. Try the CLI: python -m src.cli --help")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
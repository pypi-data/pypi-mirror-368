#!/usr/bin/env python3
"""
Command Line Interface for TWGY_V3
"""

import sys
import argparse
import json
import csv
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.config import load_config, load_default_config
from core.exceptions import TWGYError


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    try:
        from loguru import logger
        logger.remove()  # Remove default handler
        logger.add(
            sys.stderr,
            level=level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
        )
        return logger
    except ImportError:
        import logging
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s'
        )
        return logging.getLogger(__name__)


def calculate_similarity_command(args) -> None:
    """Calculate similarity between two words"""
    logger = setup_logging(args.log_level)
    
    try:
        # For now, use a simple placeholder implementation
        # TODO: Replace with actual PhoneticSimilaritySystem
        word1, word2 = args.words
        
        # Simple placeholder calculation
        if word1 == word2:
            similarity = 1.0
        else:
            # Very basic similarity based on character overlap
            set1, set2 = set(word1), set(word2)
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            similarity = intersection / union if union > 0 else 0.0
        
        result = {
            "word1": word1,
            "word2": word2,
            "similarity": similarity,
            "method": "placeholder"
        }
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Result saved to {args.output}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        sys.exit(1)


def batch_process_command(args) -> None:
    """Process batch of word pairs"""
    logger = setup_logging(args.log_level)
    
    try:
        input_path = Path(args.input)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Read input pairs
        pairs = []
        if input_path.suffix.lower() == '.csv':
            with open(input_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        pairs.append((row[0].strip(), row[1].strip()))
        elif input_path.suffix.lower() == '.json':
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    pairs = [(item[0], item[1]) for item in data if len(item) >= 2]
        else:
            # Assume text file with pairs separated by tabs or spaces
            with open(input_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        pairs.append((parts[0], parts[1]))
        
        if not pairs:
            raise ValueError("No valid word pairs found in input file")
        
        logger.info(f"Processing {len(pairs)} word pairs...")
        
        # Process pairs (placeholder implementation)
        results = []
        for i, (word1, word2) in enumerate(pairs):
            if word1 == word2:
                similarity = 1.0
            else:
                set1, set2 = set(word1), set(word2)
                intersection = len(set1 & set2)
                union = len(set1 | set2)
                similarity = intersection / union if union > 0 else 0.0
            
            results.append({
                "word1": word1,
                "word2": word2,
                "similarity": similarity,
                "method": "placeholder"
            })
            
            if (i + 1) % 100 == 0:
                logger.info(f"Processed {i + 1}/{len(pairs)} pairs")
        
        # Save results
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Results saved to {output_path}")
        logger.info(f"Processed {len(results)} pairs successfully")
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        sys.exit(1)


def find_similar_command(args) -> None:
    """Find similar words for a given word"""
    logger = setup_logging(args.log_level)
    
    try:
        # Placeholder implementation
        # TODO: Replace with actual similarity search
        target_word = args.word
        
        # For now, just return the target word itself
        similar_words = [
            {"word": target_word, "similarity": 1.0},
        ]
        
        result = {
            "target_word": target_word,
            "similar_words": similar_words,
            "method": "placeholder",
            "threshold": args.threshold,
            "top_k": args.top_k
        }
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Result saved to {args.output}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
    except Exception as e:
        logger.error(f"Error finding similar words: {e}")
        sys.exit(1)


def system_info_command(args) -> None:
    """Display system information"""
    logger = setup_logging(args.log_level)
    
    try:
        config = load_config(args.config) if args.config else load_default_config()
        
        info = {
            "system": "TWGY_V3",
            "version": "3.0.0",
            "configuration": config.to_dict(),
            "data_directories": {
                "data_dir": str(config.data.data_dir),
                "dictionaries_dir": str(config.data.dictionaries_dir),
                "phonetic_tables_dir": str(config.data.phonetic_tables_dir),
                "models_dir": str(config.data.models_dir),
            },
            "available_files": {
                "error_correction_dict": (config.data.dictionaries_dir / config.data.error_correction_dict).exists(),
                "phonetic_tables": len(list(config.data.phonetic_tables_dir.glob("*.yaml"))),
            }
        }
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
            logger.info(f"System info saved to {args.output}")
        else:
            print(json.dumps(info, ensure_ascii=False, indent=2))
            
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        sys.exit(1)


def validate_data_command(args) -> None:
    """Validate data files"""
    logger = setup_logging(args.log_level)
    
    try:
        config = load_config(args.config) if args.config else load_default_config()
        
        validation_results = {
            "dictionary_validation": {},
            "phonetic_tables_validation": [],
            "overall_status": "unknown"
        }
        
        # Validate dictionary file
        dict_file = config.data.dictionaries_dir / config.data.error_correction_dict
        if dict_file.exists():
            try:
                import pandas as pd
                df = pd.read_csv(dict_file, header=None)
                validation_results["dictionary_validation"] = {
                    "file_exists": True,
                    "total_rows": len(df),
                    "valid_rows": df.dropna().shape[0],
                    "is_valid": df.dropna().shape[0] > 0
                }
            except Exception as e:
                validation_results["dictionary_validation"] = {
                    "file_exists": True,
                    "error": str(e),
                    "is_valid": False
                }
        else:
            validation_results["dictionary_validation"] = {
                "file_exists": False,
                "is_valid": False
            }
        
        # Validate phonetic tables
        for yaml_file in config.data.phonetic_tables_dir.glob("*.yaml"):
            try:
                import yaml
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                validation_results["phonetic_tables_validation"].append({
                    "file": yaml_file.name,
                    "has_initials": "initials" in data,
                    "has_finals": "finals" in data,
                    "has_tones": "tones" in data,
                    "is_valid": all(section in data for section in ["initials", "finals", "tones"])
                })
            except Exception as e:
                validation_results["phonetic_tables_validation"].append({
                    "file": yaml_file.name,
                    "error": str(e),
                    "is_valid": False
                })
        
        # Determine overall status
        dict_valid = validation_results["dictionary_validation"].get("is_valid", False)
        tables_valid = all(table.get("is_valid", False) for table in validation_results["phonetic_tables_validation"])
        
        if dict_valid and tables_valid and validation_results["phonetic_tables_validation"]:
            validation_results["overall_status"] = "valid"
        elif dict_valid or (tables_valid and validation_results["phonetic_tables_validation"]):
            validation_results["overall_status"] = "partial"
        else:
            validation_results["overall_status"] = "invalid"
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(validation_results, f, ensure_ascii=False, indent=2)
            logger.info(f"Validation results saved to {args.output}")
        else:
            print(json.dumps(validation_results, ensure_ascii=False, indent=2))
            
        # Exit with appropriate code
        if validation_results["overall_status"] == "invalid":
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error validating data: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="TWGY_V3 - Advanced Chinese Phonetic Similarity System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s similarity 知道 資道
  %(prog)s batch-process --input pairs.csv --output results.json
  %(prog)s find-similar 知道 --top-k 5
  %(prog)s system-info
  %(prog)s validate-data
        """
    )
    
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Similarity command
    similarity_parser = subparsers.add_parser("similarity", help="Calculate similarity between two words")
    similarity_parser.add_argument("words", nargs=2, help="Two words to compare")
    similarity_parser.add_argument("--output", "-o", help="Output file path")
    similarity_parser.set_defaults(func=calculate_similarity_command)
    
    # Batch process command
    batch_parser = subparsers.add_parser("batch-process", help="Process batch of word pairs")
    batch_parser.add_argument("--input", "-i", required=True, help="Input file (CSV, JSON, or text)")
    batch_parser.add_argument("--output", "-o", required=True, help="Output file path")
    batch_parser.set_defaults(func=batch_process_command)
    
    # Find similar command
    similar_parser = subparsers.add_parser("find-similar", help="Find similar words")
    similar_parser.add_argument("word", help="Target word")
    similar_parser.add_argument("--threshold", "-t", type=float, default=0.7, help="Similarity threshold")
    similar_parser.add_argument("--top-k", "-k", type=int, default=10, help="Number of results to return")
    similar_parser.add_argument("--output", "-o", help="Output file path")
    similar_parser.set_defaults(func=find_similar_command)
    
    # System info command
    info_parser = subparsers.add_parser("system-info", help="Display system information")
    info_parser.add_argument("--output", "-o", help="Output file path")
    info_parser.set_defaults(func=system_info_command)
    
    # Validate data command
    validate_parser = subparsers.add_parser("validate-data", help="Validate data files")
    validate_parser.add_argument("--output", "-o", help="Output file path")
    validate_parser.set_defaults(func=validate_data_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger = setup_logging(args.log_level)
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
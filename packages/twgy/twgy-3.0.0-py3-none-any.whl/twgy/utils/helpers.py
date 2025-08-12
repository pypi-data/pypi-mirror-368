"""
Utility helper functions for TWGY_V3 system
Provides common functionality to reduce code duplication
"""

import time
import logging
import psutil
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, TypeVar
from pathlib import Path
from functools import wraps
import json
from contextlib import contextmanager

from ..core.constants import Validation, Performance, ErrorMessages
from ..core.exceptions import ValidationError, PerformanceError, DataError, ErrorCode

T = TypeVar('T')
logger = logging.getLogger(__name__)


def validate_query(query: str) -> str:
    """
    Validate query string according to system constraints
    
    Args:
        query: Input query string
        
    Returns:
        Cleaned query string
        
    Raises:
        ValidationError: If query is invalid
    """
    if not query or not isinstance(query, str):
        raise ValidationError(
            ErrorMessages.QUERY_VALIDATION_FAILED.format(query=query),
            field_name="query",
            field_value=query,
            validation_rule="must_be_non_empty_string",
            error_code=ErrorCode.INVALID_INPUT
        )
    
    query = query.strip()
    
    if len(query) < Validation.MIN_QUERY_LENGTH:
        raise ValidationError(
            f"Query too short: {len(query)} < {Validation.MIN_QUERY_LENGTH}",
            field_name="query",
            field_value=query,
            validation_rule=f"min_length_{Validation.MIN_QUERY_LENGTH}"
        )
    
    if len(query) > Validation.MAX_QUERY_LENGTH:
        raise ValidationError(
            f"Query too long: {len(query)} > {Validation.MAX_QUERY_LENGTH}",
            field_name="query",
            field_value=query,
            validation_rule=f"max_length_{Validation.MAX_QUERY_LENGTH}"
        )
    
    return query


def validate_chinese_characters(text: str) -> bool:
    """
    Check if text contains primarily Chinese characters
    
    Args:
        text: Text to validate
        
    Returns:
        True if text contains primarily Chinese characters
    """
    if not text:
        return False
    
    chinese_count = 0
    for char in text:
        if Validation.CJK_UNIFIED_IDEOGRAPHS_START <= ord(char) <= Validation.CJK_UNIFIED_IDEOGRAPHS_END:
            chinese_count += 1
    
    # At least 50% should be Chinese characters
    return chinese_count / len(text) >= 0.5


def safe_file_load(file_path: Union[str, Path], encoding: str = "utf-8") -> str:
    """
    Safely load file content with proper error handling
    
    Args:
        file_path: Path to file
        encoding: File encoding
        
    Returns:
        File content as string
        
    Raises:
        DataError: If file cannot be loaded
    """
    path = Path(file_path)
    
    if not path.exists():
        raise DataError(
            ErrorMessages.FILE_NOT_FOUND.format(path=path),
            file_path=str(path),
            error_code=ErrorCode.FILE_NOT_FOUND
        )
    
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        raise DataError(
            f"Failed to read file: {path}",
            file_path=str(path),
            error_code=ErrorCode.CORRUPTED_DATA,
            cause=e
        )


def safe_json_load(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Safely load JSON file with proper error handling
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        DataError: If JSON cannot be loaded or parsed
    """
    content = safe_file_load(file_path)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise DataError(
            f"Invalid JSON format: {file_path}",
            file_path=str(file_path),
            line_number=e.lineno,
            data_format="json",
            error_code=ErrorCode.INVALID_FORMAT,
            cause=e
        )


def measure_performance(
    operation_name: str,
    threshold_ms: Optional[float] = None
) -> Callable:
    """
    Decorator to measure function performance
    
    Args:
        operation_name: Name of operation for logging
        threshold_ms: Performance threshold in milliseconds
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            start_memory = get_memory_usage_mb()
            
            try:
                result = func(*args, **kwargs)
                
                end_time = time.time()
                end_memory = get_memory_usage_mb()
                duration_ms = (end_time - start_time) * 1000
                memory_delta = end_memory - start_memory
                
                # Log performance metrics
                logger.debug(
                    f"Performance: {operation_name} completed in {duration_ms:.2f}ms "
                    f"(memory: {memory_delta:+.1f}MB)"
                )
                
                # Check performance threshold
                if threshold_ms and duration_ms > threshold_ms:
                    logger.warning(
                        f"Performance threshold exceeded: {operation_name} "
                        f"took {duration_ms:.1f}ms > {threshold_ms}ms"
                    )
                
                return result
                
            except Exception as e:
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                
                logger.error(
                    f"Performance: {operation_name} failed after {duration_ms:.2f}ms: {e}"
                )
                raise
        
        return wrapper
    return decorator


def get_memory_usage_mb() -> float:
    """
    Get current memory usage in MB
    
    Returns:
        Memory usage in megabytes
    """
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        return memory_info.rss / 1024 / 1024  # Convert bytes to MB
    except Exception:
        return 0.0


@contextmanager
def memory_monitor(operation: str, threshold_mb: float = Performance.MEMORY_WARNING_THRESHOLD_MB):
    """
    Context manager to monitor memory usage during operation
    
    Args:
        operation: Name of operation
        threshold_mb: Memory threshold for warning
    """
    start_memory = get_memory_usage_mb()
    
    try:
        yield
    finally:
        end_memory = get_memory_usage_mb()
        memory_delta = end_memory - start_memory
        
        if memory_delta > threshold_mb:
            logger.warning(
                f"High memory usage detected: {operation} used {memory_delta:.1f}MB "
                f"(threshold: {threshold_mb}MB)"
            )


def batch_process(
    items: List[T],
    processor: Callable[[List[T]], List[Any]],
    batch_size: int = Performance.DEFAULT_BATCH_SIZE,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[Any]:
    """
    Process items in batches for better performance
    
    Args:
        items: Items to process
        processor: Function to process each batch
        batch_size: Size of each batch
        progress_callback: Optional callback for progress reporting
        
    Returns:
        List of processed results
    """
    results = []
    total_items = len(items)
    
    for i in range(0, total_items, batch_size):
        batch = items[i:i + batch_size]
        batch_results = processor(batch)
        results.extend(batch_results)
        
        if progress_callback:
            progress_callback(min(i + batch_size, total_items), total_items)
    
    return results


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_duration(duration_ms: float) -> str:
    """
    Format duration in milliseconds to human-readable string
    
    Args:
        duration_ms: Duration in milliseconds
        
    Returns:
        Formatted duration string
    """
    if duration_ms < 1000:
        return f"{duration_ms:.1f}ms"
    elif duration_ms < 60000:
        return f"{duration_ms / 1000:.2f}s"
    else:
        minutes = int(duration_ms / 60000)
        seconds = (duration_ms % 60000) / 1000
        return f"{minutes}m{seconds:.1f}s"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        Percentage change
    """
    if old_value == 0:
        return float('inf') if new_value != 0 else 0.0
    
    return ((new_value - old_value) / old_value) * 100


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries
    
    Args:
        dict1: Base dictionary
        dict2: Dictionary to merge in
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    return sanitized.strip()


def create_cache_key(*args: Any, **kwargs: Any) -> str:
    """
    Create a consistent cache key from arguments
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Cache key string
    """
    key_parts = []
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            key_parts.append(str(hash(str(arg))))
    
    # Add keyword arguments (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        if isinstance(value, (str, int, float, bool)):
            key_parts.append(f"{key}={value}")
        else:
            key_parts.append(f"{key}={hash(str(value))}")
    
    return "_".join(key_parts)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if necessary
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    try:
        return Path(file_path).stat().st_size / 1024 / 1024
    except Exception:
        return 0.0


def retry_operation(
    operation: Callable[[], T],
    max_retries: int = 3,
    delay_seconds: float = 1.0,
    backoff_multiplier: float = 2.0
) -> T:
    """
    Retry an operation with exponential backoff
    
    Args:
        operation: Function to retry
        max_retries: Maximum number of retries
        delay_seconds: Initial delay between retries
        backoff_multiplier: Multiplier for exponential backoff
        
    Returns:
        Result of successful operation
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    current_delay = delay_seconds
    
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                time.sleep(current_delay)
                current_delay *= backoff_multiplier
            else:
                logger.error(f"Operation failed after {max_retries + 1} attempts: {e}")
    
    raise last_exception
"""
Custom exceptions for TWGY_V3 system
Provides structured error handling with context and error codes
"""

from typing import Any, Dict, Optional
from enum import Enum


class ErrorCode(Enum):
    """Standardized error codes"""
    # Initialization errors (1000-1099)
    COMPONENT_INIT_FAILED = 1001
    DICTIONARY_LOAD_FAILED = 1002
    CONFIG_VALIDATION_FAILED = 1003
    RESOURCE_UNAVAILABLE = 1004
    
    # Runtime errors (2000-2099)
    QUERY_VALIDATION_FAILED = 2001
    PROCESSING_TIMEOUT = 2002
    INSUFFICIENT_MEMORY = 2003
    INVALID_INPUT = 2004
    
    # Data errors (3000-3099)
    FILE_NOT_FOUND = 3001
    CORRUPTED_DATA = 3002
    INVALID_FORMAT = 3003
    MISSING_REQUIRED_FIELD = 3004
    
    # Filter errors (4000-4099)
    L1_FILTER_FAILED = 4001
    L2_RERANKER_FAILED = 4002
    L3_RERANKER_FAILED = 4003
    FILTER_CHAIN_BROKEN = 4004
    
    # Similarity errors (5000-5099)
    SIMILARITY_CALCULATION_FAILED = 5001
    PHONETIC_FEATURE_EXTRACTION_FAILED = 5002
    CLASSIFICATION_ERROR = 5003
    
    # Cache errors (6000-6099)
    CACHE_WRITE_FAILED = 6001
    CACHE_READ_FAILED = 6002
    CACHE_INVALIDATION_FAILED = 6003
    CACHE_OVERFLOW = 6004


class TWGYError(Exception):
    """
    Base exception for TWGY_V3 system
    
    Provides structured error information with context
    """
    
    def __init__(
        self, 
        message: str,
        error_code: Optional[ErrorCode] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize TWGY error
        
        Args:
            message: Human-readable error message
            error_code: Standardized error code
            context: Additional context information
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code.value if self.error_code else None,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None
        }
    
    def __str__(self) -> str:
        """String representation with error code"""
        if self.error_code:
            return f"[{self.error_code.value}] {self.message}"
        return self.message


class PhoneticError(TWGYError):
    """Exception raised for phonetic processing errors"""
    
    def __init__(
        self,
        message: str,
        character: Optional[str] = None,
        phonetic_data: Optional[Dict[str, Any]] = None,
        error_code: Optional[ErrorCode] = None,
        cause: Optional[Exception] = None
    ):
        context = {}
        if character:
            context["character"] = character
        if phonetic_data:
            context["phonetic_data"] = phonetic_data
            
        super().__init__(message, error_code, context, cause)


class SimilarityError(TWGYError):
    """Exception raised for similarity calculation errors"""
    
    def __init__(
        self,
        message: str,
        word1: Optional[str] = None,
        word2: Optional[str] = None,
        algorithm: Optional[str] = None,
        error_code: Optional[ErrorCode] = None,
        cause: Optional[Exception] = None
    ):
        context = {}
        if word1:
            context["word1"] = word1
        if word2:
            context["word2"] = word2
        if algorithm:
            context["algorithm"] = algorithm
            
        super().__init__(message, error_code, context, cause)


class ConfigurationError(TWGYError):
    """Exception raised for configuration errors"""
    
    def __init__(
        self,
        message: str,
        config_section: Optional[str] = None,
        config_key: Optional[str] = None,
        expected_type: Optional[type] = None,
        actual_value: Optional[Any] = None,
        error_code: Optional[ErrorCode] = None,
        cause: Optional[Exception] = None
    ):
        context = {}
        if config_section:
            context["config_section"] = config_section
        if config_key:
            context["config_key"] = config_key
        if expected_type:
            context["expected_type"] = expected_type.__name__
        if actual_value is not None:
            context["actual_value"] = actual_value
            
        super().__init__(message, error_code, context, cause)


class DataError(TWGYError):
    """Exception raised for data loading/processing errors"""
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        data_format: Optional[str] = None,
        error_code: Optional[ErrorCode] = None,
        cause: Optional[Exception] = None
    ):
        context = {}
        if file_path:
            context["file_path"] = file_path
        if line_number:
            context["line_number"] = line_number
        if data_format:
            context["data_format"] = data_format
            
        super().__init__(message, error_code, context, cause)


class FilterError(TWGYError):
    """Exception raised for filter processing errors"""
    
    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        filter_level: Optional[str] = None,
        candidates_count: Optional[int] = None,
        processing_time_ms: Optional[float] = None,
        error_code: Optional[ErrorCode] = None,
        cause: Optional[Exception] = None
    ):
        context = {}
        if query:
            context["query"] = query
        if filter_level:
            context["filter_level"] = filter_level
        if candidates_count is not None:
            context["candidates_count"] = candidates_count
        if processing_time_ms is not None:
            context["processing_time_ms"] = processing_time_ms
            
        super().__init__(message, error_code, context, cause)


class CacheError(TWGYError):
    """Exception raised for cache operations errors"""
    
    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        cache_type: Optional[str] = None,
        operation: Optional[str] = None,
        error_code: Optional[ErrorCode] = None,
        cause: Optional[Exception] = None
    ):
        context = {}
        if cache_key:
            context["cache_key"] = cache_key
        if cache_type:
            context["cache_type"] = cache_type
        if operation:
            context["operation"] = operation
            
        super().__init__(message, error_code, context, cause)


class ValidationError(TWGYError):
    """Exception raised for validation errors"""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        validation_rule: Optional[str] = None,
        error_code: Optional[ErrorCode] = None,
        cause: Optional[Exception] = None
    ):
        context = {}
        if field_name:
            context["field_name"] = field_name
        if field_value is not None:
            context["field_value"] = field_value
        if validation_rule:
            context["validation_rule"] = validation_rule
            
        super().__init__(message, error_code, context, cause)


class PerformanceError(TWGYError):
    """Exception raised for performance-related issues"""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        duration_ms: Optional[float] = None,
        threshold_ms: Optional[float] = None,
        memory_usage_mb: Optional[float] = None,
        error_code: Optional[ErrorCode] = None,
        cause: Optional[Exception] = None
    ):
        context = {}
        if operation:
            context["operation"] = operation
        if duration_ms is not None:
            context["duration_ms"] = duration_ms
        if threshold_ms is not None:
            context["threshold_ms"] = threshold_ms
        if memory_usage_mb is not None:
            context["memory_usage_mb"] = memory_usage_mb
            
        super().__init__(message, error_code, context, cause)


# Legacy alias for backward compatibility
IndexError = DataError  # Rename to avoid conflict with built-in IndexError


def create_error_from_exception(
    exc: Exception,
    message_override: Optional[str] = None,
    error_code: Optional[ErrorCode] = None,
    context: Optional[Dict[str, Any]] = None
) -> TWGYError:
    """
    Create a TWGYError from a generic exception
    
    Args:
        exc: Original exception
        message_override: Override message (uses exc message if None)
        error_code: Error code to assign
        context: Additional context
    
    Returns:
        Appropriate TWGYError subclass
    """
    message = message_override or str(exc)
    
    # Map common exception types to TWGY exceptions
    if isinstance(exc, FileNotFoundError):
        return DataError(
            message,
            file_path=getattr(exc, 'filename', None),
            error_code=error_code or ErrorCode.FILE_NOT_FOUND,
            cause=exc
        )
    elif isinstance(exc, MemoryError):
        return PerformanceError(
            message,
            error_code=error_code or ErrorCode.INSUFFICIENT_MEMORY,
            cause=exc
        )
    elif isinstance(exc, TimeoutError):
        return PerformanceError(
            message,
            error_code=error_code or ErrorCode.PROCESSING_TIMEOUT,
            cause=exc
        )
    elif isinstance(exc, ValueError):
        return ValidationError(
            message,
            error_code=error_code or ErrorCode.INVALID_INPUT,
            cause=exc
        )
    else:
        # Generic TWGYError for unknown exception types
        return TWGYError(message, error_code, context, exc)
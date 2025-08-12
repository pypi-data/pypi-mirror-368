"""
Core system components for TWGY_V3
"""

from .phonetic_system import PhoneticSimilaritySystem
from .config import SystemConfig
from .exceptions import TWGYError, PhoneticError, SimilarityError

__all__ = [
    "PhoneticSimilaritySystem",
    "SystemConfig", 
    "TWGYError",
    "PhoneticError",
    "SimilarityError",
]
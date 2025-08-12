"""
TWGY_V3 - Advanced Chinese Phonetic Similarity System

A comprehensive system for Chinese phonetic similarity comparison
with innovative first-last character priority strategy and 
phonetic table-based classification.
"""

__version__ = "3.0.0"
__author__ = "TWGY Team"
__email__ = "team@twgy.dev"

from .core.phonetic_system import PhoneticSimilaritySystem
from .phonetic.classifier import PhoneticClassifier
from .similarity.engine import SimilarityEngine
from .comparison.strategies import ComparisonStrategy

__all__ = [
    "PhoneticSimilaritySystem",
    "PhoneticClassifier", 
    "SimilarityEngine",
    "ComparisonStrategy",
]
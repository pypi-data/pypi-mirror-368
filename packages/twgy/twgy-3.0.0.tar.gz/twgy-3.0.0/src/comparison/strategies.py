"""
Comparison strategies for different word length scenarios
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ComparisonStrategy(ABC):
    """
    Abstract base class for comparison strategies
    """
    
    @abstractmethod
    def calculate_similarity(self, word1: str, word2: str) -> float:
        """
        Calculate similarity between two words
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def is_applicable(self, word1: str, word2: str) -> bool:
        """
        Check if this strategy is applicable for the given word pair
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            True if strategy is applicable
        """
        pass


class DirectComparisonStrategy(ComparisonStrategy):
    """
    Direct comparison strategy for words of same length
    """
    
    def calculate_similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity using direct character comparison"""
        if len(word1) != len(word2):
            return 0.0
        
        if word1 == word2:
            return 1.0
        
        # Simple character-by-character comparison
        matches = sum(1 for c1, c2 in zip(word1, word2) if c1 == c2)
        return matches / len(word1)
    
    def is_applicable(self, word1: str, word2: str) -> bool:
        """Applicable when words have same length"""
        return len(word1) == len(word2)


class SlidingWindowStrategy(ComparisonStrategy):
    """
    Sliding window strategy for words with length difference of ±1
    """
    
    def calculate_similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity using sliding window approach"""
        length_diff = abs(len(word1) - len(word2))
        if length_diff != 1:
            return 0.0
        
        shorter, longer = (word1, word2) if len(word1) < len(word2) else (word2, word1)
        
        max_similarity = 0.0
        for i in range(len(longer) - len(shorter) + 1):
            window = longer[i:i+len(shorter)]
            matches = sum(1 for c1, c2 in zip(shorter, window) if c1 == c2)
            similarity = matches / len(shorter)
            max_similarity = max(max_similarity, similarity)
        
        # Apply length penalty
        return max_similarity * 0.9  # 10% penalty for length difference
    
    def is_applicable(self, word1: str, word2: str) -> bool:
        """Applicable when length difference is exactly 1"""
        return abs(len(word1) - len(word2)) == 1
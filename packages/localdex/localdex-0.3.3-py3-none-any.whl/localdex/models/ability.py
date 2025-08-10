"""
Ability data model.

This module contains the data structure for Pokemon abilities.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class Ability:
    """A Pokemon ability with all its data."""
    
    # Basic information
    name: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    
    # Game information
    generation: Optional[int] = None
    rating: Optional[float] = None  # Competitive rating
    num: Optional[int] = None  # Ability number
    
    # Effect information
    effect: Optional[str] = None
    effect_entries: Optional[List[Dict[str, str]]] = None
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.metadata is None:
            self.metadata = {}
        if self.effect_entries is None:
            self.effect_entries = []
    
    @property
    def has_description(self) -> bool:
        """Check if the ability has a description."""
        return self.description is not None and self.description.strip() != ""
    
    @property
    def has_short_description(self) -> bool:
        """Check if the ability has a short description."""
        return self.short_description is not None and self.short_description.strip() != ""
    
    @property
    def is_competitive(self) -> bool:
        """Check if the ability is considered competitive (rating >= 2.0)."""
        return self.rating is not None and self.rating >= 2.0
    
    @property
    def is_excellent(self) -> bool:
        """Check if the ability is considered excellent (rating >= 4.0)."""
        return self.rating is not None and self.rating >= 4.0
    
    @property
    def is_poor(self) -> bool:
        """Check if the ability is considered poor (rating <= 1.0)."""
        return self.rating is not None and self.rating <= 1.0
    
    def get_effect_text(self, language: str = "en") -> Optional[str]:
        """
        Get the effect text in the specified language.
        
        Args:
            language: Language code (e.g., "en", "es", "fr")
            
        Returns:
            Effect text in the specified language, or None if not found
        """
        if not self.effect_entries:
            return None
        
        for entry in self.effect_entries:
            if entry.get("language", {}).get("name", "").lower() == language.lower():
                return entry.get("effect", "")
        
        # Fallback to English if specified language not found
        for entry in self.effect_entries:
            if entry.get("language", {}).get("name", "").lower() == "en":
                return entry.get("effect", "")
        
        return None
    
    def __str__(self) -> str:
        """String representation of the ability."""
        return self.name
    
    def __repr__(self) -> str:
        """Detailed string representation of the ability."""
        return f"Ability(name='{self.name}', rating={self.rating})" 
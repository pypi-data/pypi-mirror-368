"""
Move data model.

This module contains the data structure for Pokemon moves.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union


@dataclass
class Move:
    """A Pokemon move with all its data."""
    
    # Basic information
    name: str
    type: str
    category: str  # Physical, Special, Status
    
    # Battle properties
    base_power: Union[int, str] = 0  # Can be "variable" for moves like Acrobatics
    accuracy: Union[int, str] = 100  # Can be "always_hits" for certain moves
    pp: int = 10
    priority: int = 0
    target: str = "normal"
    
    # Additional properties
    description: Optional[str] = None
    short_description: Optional[str] = None
    contest_type: Optional[str] = None
    crit_ratio: int = 1
    
    # Effects
    secondary_effects: Optional[Dict[str, Any]] = None
    flags: Optional[Dict[str, Any]] = None
    drain: Optional[List[int]] = None  # [numerator, denominator] for moves like Absorb
    
    # Z-move and Mega evolution data
    z_move: Optional[str] = None
    z_move_type: Optional[str] = None
    z_move_from: Optional[str] = None
    
    # Game information
    generation: Optional[int] = None
    is_nonstandard: Optional[str] = None
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.secondary_effects is None:
            self.secondary_effects = {}
        if self.flags is None:
            self.flags = {}
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_physical(self) -> bool:
        """Check if the move is physical."""
        return self.category.lower() == "physical"
    
    @property
    def is_special(self) -> bool:
        """Check if the move is special."""
        return self.category.lower() == "special"
    
    @property
    def is_status(self) -> bool:
        """Check if the move is status."""
        return self.category.lower() == "status"
    
    @property
    def has_variable_power(self) -> bool:
        """Check if the move has variable power."""
        return isinstance(self.base_power, str) and "variable" in self.base_power.lower()
    
    @property
    def always_hits(self) -> bool:
        """Check if the move always hits."""
        return self.accuracy == "always_hits" or self.accuracy == 100
    
    @property
    def is_priority_move(self) -> bool:
        """Check if the move has priority."""
        return self.priority != 0
    
    @property
    def is_high_priority(self) -> bool:
        """Check if the move has high priority (positive)."""
        return self.priority > 0
    
    @property
    def is_low_priority(self) -> bool:
        """Check if the move has low priority (negative)."""
        return self.priority < 0
    
    @property
    def is_contact_move(self) -> bool:
        """Check if the move makes contact."""
        return self.flags.get("contact", False)
    
    @property
    def is_sound_move(self) -> bool:
        """Check if the move is a sound-based move."""
        return self.flags.get("sound", False)
    
    @property
    def is_punch_move(self) -> bool:
        """Check if the move is a punch move."""
        return self.flags.get("punch", False)
    
    @property
    def is_bite_move(self) -> bool:
        """Check if the move is a bite move."""
        return self.flags.get("bite", False)
    
    @property
    def is_pulse_move(self) -> bool:
        """Check if the move is a pulse move."""
        return self.flags.get("pulse", False)
    
    @property
    def is_ballistic_move(self) -> bool:
        """Check if the move is a ballistic move."""
        return self.flags.get("ballistic", False)
    
    @property
    def is_dance_move(self) -> bool:
        """Check if the move is a dance move."""
        return self.flags.get("dance", False)
    
    @property
    def is_heal_move(self) -> bool:
        """Check if the move heals the user."""
        return self.drain is not None and self.drain[0] > 0
    
    @property
    def is_recoil_move(self) -> bool:
        """Check if the move has recoil damage."""
        return self.flags.get("recoil", False)
    
    @property
    def is_z_move(self) -> bool:
        """Check if the move is a Z-move."""
        return self.z_move is not None
    
    def get_effectiveness_against(self, target_types: List[str]) -> float:
        """
        Calculate the type effectiveness against target types.
        
        Args:
            target_types: List of target Pokemon types
            
        Returns:
            Effectiveness multiplier (0.0, 0.25, 0.5, 1.0, 2.0, 4.0)
        """
        # This is a simplified implementation
        # In a full implementation, you'd have a complete type chart
        effectiveness = 1.0
        
        # Example type effectiveness (simplified)
        type_chart = {
            "Fire": {"Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Steel": 2.0, "Water": 0.5, "Rock": 0.5, "Fire": 0.5, "Dragon": 0.5},
            "Water": {"Fire": 2.0, "Ground": 2.0, "Rock": 2.0, "Grass": 0.5, "Water": 0.5, "Dragon": 0.5},
            "Electric": {"Water": 2.0, "Flying": 2.0, "Grass": 0.5, "Electric": 0.5, "Dragon": 0.5, "Ground": 0.0},
            "Grass": {"Water": 2.0, "Ground": 2.0, "Rock": 2.0, "Fire": 0.5, "Grass": 0.5, "Poison": 0.5, "Flying": 0.5, "Bug": 0.5, "Dragon": 0.5, "Steel": 0.5},
            "Ice": {"Grass": 2.0, "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0, "Fire": 0.5, "Water": 0.5, "Ice": 0.5, "Steel": 0.5},
            "Fighting": {"Normal": 2.0, "Ice": 2.0, "Rock": 2.0, "Dark": 2.0, "Steel": 2.0, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Fairy": 0.5, "Ghost": 0.0},
            "Poison": {"Grass": 2.0, "Fairy": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0.0},
            "Ground": {"Fire": 2.0, "Electric": 2.0, "Poison": 2.0, "Rock": 2.0, "Steel": 2.0, "Grass": 0.5, "Bug": 0.5, "Flying": 0.0},
            "Flying": {"Grass": 2.0, "Fighting": 2.0, "Bug": 2.0, "Electric": 0.5, "Rock": 0.5, "Steel": 0.5},
            "Psychic": {"Fighting": 2.0, "Poison": 2.0, "Dark": 0.0, "Steel": 0.5},
            "Bug": {"Grass": 2.0, "Psychic": 2.0, "Dark": 2.0, "Fire": 0.5, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Ghost": 0.5, "Steel": 0.5, "Fairy": 0.5},
            "Rock": {"Fire": 2.0, "Ice": 2.0, "Flying": 2.0, "Bug": 2.0, "Fighting": 0.5, "Ground": 0.5, "Steel": 0.5},
            "Ghost": {"Psychic": 2.0, "Ghost": 2.0, "Normal": 0.0, "Dark": 0.5},
            "Dragon": {"Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0},
            "Dark": {"Psychic": 2.0, "Ghost": 2.0, "Fighting": 0.5, "Dark": 0.5, "Fairy": 0.5},
            "Steel": {"Ice": 2.0, "Rock": 2.0, "Fairy": 2.0, "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Steel": 0.5},
            "Fairy": {"Fighting": 2.0, "Dragon": 2.0, "Dark": 2.0, "Poison": 0.5, "Steel": 0.5, "Fire": 0.5},
        }
        
        move_type_effectiveness = type_chart.get(self.type, {})
        
        for target_type in target_types:
            if target_type in move_type_effectiveness:
                effectiveness *= move_type_effectiveness[target_type]
        
        return effectiveness
    
    def __str__(self) -> str:
        """String representation of the move."""
        return f"{self.name} ({self.type}) - {self.category}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the move."""
        return f"Move(name='{self.name}', type='{self.type}', category='{self.category}')" 
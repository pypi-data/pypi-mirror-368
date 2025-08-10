"""
Pokemon data models.

This module contains the data structures for Pokemon and their base stats.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from .ability import Ability
from .move import Move


@dataclass
class BaseStats:
    """Base stats for a Pokemon."""
    
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    
    @property
    def total(self) -> int:
        """Calculate the total base stat value."""
        return self.hp + self.attack + self.defense + self.special_attack + self.special_defense + self.speed
    
    @property
    def average(self) -> float:
        """Calculate the average base stat value."""
        return self.total / 6.0


@dataclass
class Pokemon:
    """A Pokemon with all its data."""
    
    # Basic information
    id: int
    name: str
    types: List[str]
    base_stats: BaseStats
    
    # Physical characteristics
    height: Optional[float] = None  # in meters
    weight: Optional[float] = None  # in kilograms
    color: Optional[str] = None
    
    # Abilities
    abilities: Dict[str, Ability] = field(default_factory=dict)
    
    # Moves and learnsets
    moves: List[Move] = field(default_factory=list)
    learnset: Dict[str, Any] = field(default_factory=dict)
    
    # Evolution information
    evolutions: List[str] = field(default_factory=list)
    prevo: Optional[str] = None
    evo_level: Optional[int] = None
    evo_type: Optional[str] = None
    evo_condition: Optional[str] = None
    evo_item: Optional[str] = None
    
    # Breeding information
    egg_groups: List[str] = field(default_factory=list)
    gender_ratio: Dict[str, float] = field(default_factory=dict)
    
    # Game information
    generation: Optional[int] = None
    description: Optional[str] = None
    is_legendary: bool = False
    is_mythical: bool = False
    is_ultra_beast: bool = False
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.abilities is None:
            self.abilities = {}
        if self.moves is None:
            self.moves = []
        if self.learnset is None:
            self.learnset = {}
        if self.evolutions is None:
            self.evolutions = []
        if self.egg_groups is None:
            self.egg_groups = []
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def primary_type(self) -> str:
        """Get the primary type of the Pokemon."""
        return self.types[0] if self.types else "Normal"
    
    @property
    def secondary_type(self) -> Optional[str]:
        """Get the secondary type of the Pokemon, if any."""
        return self.types[1] if len(self.types) > 1 else None
    
    @property
    def is_dual_type(self) -> bool:
        """Check if the Pokemon has two types."""
        return len(self.types) == 2
    
    @property
    def best_attack_stat(self) -> int:
        """Get the higher of attack or special attack."""
        return max(self.base_stats.attack, self.base_stats.special_attack)
    
    @property
    def best_defense_stat(self) -> int:
        """Get the higher of defense or special defense."""
        return max(self.base_stats.defense, self.base_stats.special_defense)
    
    @property
    def is_physical_attacker(self) -> bool:
        """Check if the Pokemon is better suited for physical attacks."""
        return self.base_stats.attack > self.base_stats.special_attack
    
    @property
    def is_special_attacker(self) -> bool:
        """Check if the Pokemon is better suited for special attacks."""
        return self.base_stats.special_attack > self.base_stats.attack
    
    @property
    def is_mixed_attacker(self) -> bool:
        """Check if the Pokemon has balanced attack stats."""
        return abs(self.base_stats.attack - self.base_stats.special_attack) <= 10
    
    def get_ability(self, slot: str) -> Optional[Ability]:
        """Get an ability by slot (0, 1, H, S)."""
        return self.abilities.get(slot)
    
    def get_moves_by_type(self, move_type: str) -> List[Move]:
        """Get all moves of a specific type."""
        return [move for move in self.moves if move.type.lower() == move_type.lower()]
    
    def get_moves_by_category(self, category: str) -> List[Move]:
        """Get all moves of a specific category (Physical, Special, Status)."""
        return [move for move in self.moves if move.category.lower() == category.lower()]
    
    def has_move(self, move_name: str) -> bool:
        """Check if the Pokemon can learn a specific move."""
        return any(move.name.lower() == move_name.lower() for move in self.moves)
    
    def has_ability(self, ability_name: str) -> bool:
        """Check if the Pokemon has a specific ability."""
        return any(
            ability.name.lower() == ability_name.lower() 
            for ability in self.abilities.values()
        )
    
    def __str__(self) -> str:
        """String representation of the Pokemon."""
        type_str = "/".join(self.types)
        return f"{self.name} (#{self.id}) - {type_str}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the Pokemon."""
        return f"Pokemon(id={self.id}, name='{self.name}', types={self.types})" 
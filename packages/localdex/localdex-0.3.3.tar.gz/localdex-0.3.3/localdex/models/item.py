"""
Item data model.

This module contains the data structure for Pokemon items.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class Item:
    """A Pokemon item with all its data."""
    
    # Basic information
    name: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    
    # Game information
    generation: Optional[int] = None
    num: Optional[int] = None  # Item number
    spritenum: Optional[int] = None  # Sprite number
    cost: Optional[int] = None  # Item cost in PokeDollars
    
    # Item effects
    fling: Optional[Dict[str, Any]] = None  # Fling move data
    mega_stone: Optional[str] = None  # For mega evolution
    mega_evolves: Optional[str] = None  # Pokemon that mega evolves with this item
    z_move: Optional[str] = None  # Z-move this item enables
    z_move_type: Optional[str] = None  # Type of Z-move
    z_move_from: Optional[str] = None  # Move that becomes the Z-move
    item_user: Optional[List[str]] = None  # Pokemon that can use this item
    on_plate: Optional[str] = None  # For type plates
    on_drive: Optional[str] = None  # For drives
    on_memory: Optional[str] = None  # For memories
    forced_forme: Optional[str] = None  # For forme-changing items
    
    # Additional properties
    is_nonstandard: Optional[str] = None
    category: Optional[str] = None  # Item category
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.metadata is None:
            self.metadata = {}
        if self.item_user is None:
            self.item_user = []
    
    @property
    def has_description(self) -> bool:
        """Check if the item has a description."""
        return self.description is not None and self.description.strip() != ""
    
    @property
    def has_short_description(self) -> bool:
        """Check if the item has a short description."""
        return self.short_description is not None and self.short_description.strip() != ""
    
    @property
    def is_mega_stone(self) -> bool:
        """Check if the item is a mega stone."""
        return self.mega_stone is not None or self.mega_evolves is not None
    
    @property
    def is_z_crystal(self) -> bool:
        """Check if the item is a Z-crystal."""
        return self.z_move is not None
    
    @property
    def is_plate(self) -> bool:
        """Check if the item is a type plate."""
        return self.on_plate is not None
    
    @property
    def is_drive(self) -> bool:
        """Check if the item is a drive."""
        return self.on_drive is not None
    
    @property
    def is_memory(self) -> bool:
        """Check if the item is a memory."""
        return self.on_memory is not None
    
    @property
    def is_forme_changer(self) -> bool:
        """Check if the item changes a Pokemon's forme."""
        return self.forced_forme is not None
    
    @property
    def has_fling_effect(self) -> bool:
        """Check if the item has a fling effect."""
        return self.fling is not None and len(self.fling) > 0
    
    @property
    def fling_power(self) -> Optional[int]:
        """Get the fling base power of the item."""
        if self.fling and "basePower" in self.fling:
            return self.fling["basePower"]
        return None
    
    @property
    def fling_status(self) -> Optional[str]:
        """Get the status effect when the item is flung."""
        if self.fling and "status" in self.fling:
            return self.fling["status"]
        return None
    
    @property
    def fling_volatile_status(self) -> Optional[str]:
        """Get the volatile status effect when the item is flung."""
        if self.fling and "volatileStatus" in self.fling:
            return self.fling["volatileStatus"]
        return None
    
    def can_be_used_by(self, pokemon_name: str) -> bool:
        """
        Check if a Pokemon can use this item.
        
        Args:
            pokemon_name: Name of the Pokemon to check
            
        Returns:
            True if the Pokemon can use this item, False otherwise
        """
        if not self.item_user:
            return True  # If no restrictions, any Pokemon can use it
        
        return pokemon_name.lower() in [user.lower() for user in self.item_user]
    
    def __str__(self) -> str:
        """String representation of the item."""
        return self.name
    
    def __repr__(self) -> str:
        """Detailed string representation of the item."""
        return f"Item(name='{self.name}', num={self.num})" 
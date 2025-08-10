"""
Data loader for LocalDex.

This module handles loading Pokemon data from JSON files with proper
error handling and data validation.
"""

import json
import os
import glob
from pathlib import Path
from typing import Dict, List, Optional, Any
from importlib import resources

from .exceptions import DataLoadError, DataParseError


class DataLoader:
    """
    Handles loading Pokemon data from various sources.
    
    This class provides methods to load Pokemon, moves, abilities, and items
    from JSON files, with support for both package data and custom data paths.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the data loader.
        
        Args:
            data_path: Optional path to data directory. If None, uses package data.
        """
        self.data_path = data_path or self._get_package_data_path()
        self._validate_data_path()
        
        # Cache for loaded data
        self._pokemon_data: Dict[str, Dict[str, Any]] = {}
        self._pokemon_id_map: Dict[int, str] = {}
        self._move_data: Dict[str, Dict[str, Any]] = {}
        self._ability_data: Dict[str, Dict[str, Any]] = {}
        self._item_data: Dict[str, Dict[str, Any]] = {}
        
        # Load data indexes
        self._load_data_indexes()
    
    def _get_package_data_path(self) -> str:
        """Get the path to the package data directory."""
        try:
            with resources.path("localdex", "data") as data_path:
                return str(data_path)
        except Exception:
            # Fallback to relative path
            return os.path.join(os.path.dirname(__file__), "data")
    
    def _validate_data_path(self) -> None:
        """Validate that the data path exists and contains expected directories."""
        if not os.path.exists(self.data_path):
            # Don't raise an error, just log a warning and continue with empty data
            print(f"Warning: Data path does not exist: {self.data_path}")
            return
        
        expected_dirs = ["pokemon", "moves", "abilities", "items"]
        for dir_name in expected_dirs:
            dir_path = os.path.join(self.data_path, dir_name)
            if not os.path.exists(dir_path):
                print(f"Warning: Expected data directory not found: {dir_path}")
                # Don't raise an error, just continue with empty data
    
    def _load_data_indexes(self) -> None:
        """Load data indexes for faster lookups."""
        try:
            # Load Pokemon data
            pokemon_dir = os.path.join(self.data_path, "pokemon")
            if not os.path.exists(pokemon_dir):
                return  # Skip loading if directory doesn't exist
            pokemon_files = glob.glob(os.path.join(pokemon_dir, "*.json"))
            
            for file_path in pokemon_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        pokemon_data = json.load(f)
                    
                    pokemon_id = pokemon_data.get("id")
                    pokemon_name = pokemon_data.get("name", "").lower()
                    
                    if pokemon_id:
                        self._pokemon_id_map[pokemon_id] = pokemon_name
                    
                    if pokemon_name:
                        self._pokemon_data[pokemon_name] = pokemon_data
                        
                except (json.JSONDecodeError, KeyError) as e:
                    # Skip invalid files
                    continue
            
            # Load move data
            moves_dir = os.path.join(self.data_path, "moves")
            if os.path.exists(moves_dir):
                move_files = glob.glob(os.path.join(moves_dir, "*.json"))
            else:
                move_files = []
            
            for file_path in move_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        move_data = json.load(f)
                    
                    move_name = move_data.get("name", "").lower().replace(" ", "").replace("-", "")
                    if move_name:
                        self._move_data[move_name] = move_data
                        
                except (json.JSONDecodeError, KeyError) as e:
                    # Skip invalid files
                    continue
            
            # Load ability data
            abilities_dir = os.path.join(self.data_path, "abilities")
            if os.path.exists(abilities_dir):
                ability_files = glob.glob(os.path.join(abilities_dir, "*.json"))
            else:
                ability_files = []
            
            for file_path in ability_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        ability_data = json.load(f)
                    
                    ability_name = ability_data.get("name", "").lower()
                    if ability_name:
                        self._ability_data[ability_name] = ability_data
                        
                except (json.JSONDecodeError, KeyError) as e:
                    # Skip invalid files
                    continue
            
            # Load item data
            items_dir = os.path.join(self.data_path, "items")
            if os.path.exists(items_dir):
                item_files = glob.glob(os.path.join(items_dir, "*.json"))
            else:
                item_files = []
            
            for file_path in item_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        item_data = json.load(f)
                    
                    item_name = item_data.get("name", "").lower()
                    if item_name:
                        self._item_data[item_name] = item_data
                        
                except (json.JSONDecodeError, KeyError) as e:
                    # Skip invalid files
                    continue
                    
        except Exception as e:
            raise DataLoadError(f"Error loading data indexes: {e}")
    
    def load_pokemon_by_id(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        """
        Load Pokemon data by ID.
        
        Args:
            pokemon_id: Pokemon ID number
            
        Returns:
            Pokemon data dictionary or None if not found
        """
        pokemon_name = self._pokemon_id_map.get(pokemon_id)
        if pokemon_name:
            return self._pokemon_data.get(pokemon_name)
        return None
    
    def load_pokemon_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load Pokemon data by name.
        
        Args:
            name: Pokemon name (case-insensitive)
            
        Returns:
            Pokemon data dictionary or None if not found
        """
        return self._pokemon_data.get(name.lower())
    
    def load_move(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load move data by name.
        
        Args:
            name: Move name (case-insensitive)
            
        Returns:
            Move data dictionary or None if not found
        """
        return self._move_data.get(name.lower())
    
    def load_ability(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load ability data by name.
        
        Args:
            name: Ability name (case-insensitive)
            
        Returns:
            Ability data dictionary or None if not found
        """
        return self._ability_data.get(name.lower())
    
    def load_item(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load item data by name.
        
        Args:
            name: Item name (case-insensitive)
            
        Returns:
            Item data dictionary or None if not found
        """
        return self._item_data.get(name.lower())
    
    def load_all_pokemon(self) -> List[Dict[str, Any]]:
        """
        Load all Pokemon data.
        
        Returns:
            List of Pokemon data dictionaries
        """
        return list(self._pokemon_data.values())
    
    def load_all_moves(self) -> List[Dict[str, Any]]:
        """
        Load all move data.
        
        Returns:
            List of move data dictionaries
        """
        return list(self._move_data.values())
    
    def load_all_abilities(self) -> List[Dict[str, Any]]:
        """
        Load all ability data.
        
        Returns:
            List of ability data dictionaries
        """
        return list(self._ability_data.values())
    
    def load_all_items(self) -> List[Dict[str, Any]]:
        """
        Load all item data.
        
        Returns:
            List of item data dictionaries
        """
        return list(self._item_data.values())
    
    def get_data_stats(self) -> Dict[str, int]:
        """
        Get statistics about loaded data.
        
        Returns:
            Dictionary with counts of loaded data
        """
        return {
            "pokemon": len(self._pokemon_data),
            "moves": len(self._move_data),
            "abilities": len(self._ability_data),
            "items": len(self._item_data),
            "pokemon_by_id": len(self._pokemon_id_map)
        }
    
    def reload_data(self) -> None:
        """Reload all data from files."""
        # Clear existing data
        self._pokemon_data.clear()
        self._pokemon_id_map.clear()
        self._move_data.clear()
        self._ability_data.clear()
        self._item_data.clear()
        
        # Reload indexes
        self._load_data_indexes()
    
    def validate_data_integrity(self) -> Dict[str, List[str]]:
        """
        Validate the integrity of loaded data.
        
        Returns:
            Dictionary with validation errors by data type
        """
        errors = {
            "pokemon": [],
            "moves": [],
            "abilities": [],
            "items": []
        }
        
        # Validate Pokemon data
        for name, data in self._pokemon_data.items():
            if not data.get("name"):
                errors["pokemon"].append(f"Missing name for Pokemon: {name}")
            if not data.get("types"):
                errors["pokemon"].append(f"Missing types for Pokemon: {name}")
            if not data.get("baseStats"):
                errors["pokemon"].append(f"Missing base stats for Pokemon: {name}")
        
        # Validate move data
        for name, data in self._move_data.items():
            if not data.get("name"):
                errors["moves"].append(f"Missing name for move: {name}")
            if not data.get("type"):
                errors["moves"].append(f"Missing type for move: {name}")
            if not data.get("category"):
                errors["moves"].append(f"Missing category for move: {name}")
        
        # Validate ability data
        for name, data in self._ability_data.items():
            if not data.get("name"):
                errors["abilities"].append(f"Missing name for ability: {name}")
        
        # Validate item data
        for name, data in self._item_data.items():
            if not data.get("name"):
                errors["items"].append(f"Missing name for item: {name}")
        
        return errors 
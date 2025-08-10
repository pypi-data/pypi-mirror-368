"""
Comprehensive test suite for LocalDex core functionality.

This module tests the main LocalDex class including initialization,
data retrieval, caching, search capabilities, and error handling.
"""

import pytest
import tempfile
import json
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from localdex.core import LocalDex
from localdex.models import Pokemon, Move, Ability, Item, BaseStats
from localdex.exceptions import (
    PokemonNotFoundError, MoveNotFoundError, AbilityNotFoundError,
    ItemNotFoundError, SearchError
)


class TestLocalDexInitialization:
    """Test LocalDex initialization and configuration."""
    
    def test_init_with_defaults(self):
        """Test LocalDex initialization with default parameters."""
        dex = LocalDex()
        assert dex.enable_caching is True
        assert dex.data_loader is not None
        assert len(dex._pokemon_cache) == 0
        assert len(dex._move_cache) == 0
        assert len(dex._ability_cache) == 0
        assert len(dex._item_cache) == 0
    
    def test_init_with_custom_data_path(self):
        """Test LocalDex initialization with custom data path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dex = LocalDex(data_path=temp_dir)
            assert dex.data_dir == temp_dir
    
    def test_init_with_data_dir_alias(self):
        """Test LocalDex initialization with data_dir parameter (backward compatibility)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dex = LocalDex(data_dir=temp_dir)
            assert dex.data_dir == temp_dir
    
    def test_init_with_caching_disabled(self):
        """Test LocalDex initialization with caching disabled."""
        dex = LocalDex(enable_caching=False)
        assert dex.enable_caching is False
        # Should not build indexes when caching is disabled
        assert len(dex._pokemon_by_type) == 0
        assert len(dex._pokemon_by_generation) == 0
    
    def test_init_builds_indexes_when_caching_enabled(self):
        """Test that indexes are built when caching is enabled."""
        # Mock the data loader to return some test data
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            
            # Mock get_all_pokemon to return test data
            test_pokemon = [
                Pokemon(
                    id=1, name="Bulbasaur", types=["Grass", "Poison"],
                    base_stats=BaseStats(45, 49, 49, 65, 65, 45),
                    generation=1
                ),
                Pokemon(
                    id=4, name="Charmander", types=["Fire"],
                    base_stats=BaseStats(39, 52, 43, 60, 50, 65),
                    generation=1
                )
            ]
            
            with patch.object(LocalDex, 'get_all_pokemon', return_value=test_pokemon):
                with patch.object(LocalDex, 'get_all_moves', return_value=[]):
                    dex = LocalDex(enable_caching=True)
                    
                    # Check that indexes were built
                    assert "grass" in dex._pokemon_by_type
                    assert "poison" in dex._pokemon_by_type
                    assert "fire" in dex._pokemon_by_type
                    assert 1 in dex._pokemon_by_generation
                    assert "bulbasaur" in dex._pokemon_by_type["grass"]
                    assert "charmander" in dex._pokemon_by_type["fire"]


class TestLocalDexPokemonRetrieval:
    """Test Pokemon retrieval functionality."""
    
    @pytest.fixture
    def mock_dex(self):
        """Create a LocalDex instance with mocked data loader."""
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            dex = LocalDex(enable_caching=False)  # Disable caching for cleaner tests
            return dex
    
    def test_get_pokemon_by_id(self, mock_dex):
        """Test getting Pokemon by ID."""
        # Mock data
        pokemon_data = {
            "id": 25,
            "name": "Pikachu",
            "types": ["Electric"],
            "baseStats": {"hp": 35, "attack": 55, "defense": 40, 
                         "special_attack": 50, "special_defense": 50, "speed": 90},
            "generation": 1
        }
        
        mock_dex.data_loader.load_pokemon_by_id.return_value = pokemon_data
        
        pokemon = mock_dex.get_pokemon_by_id(25)
        
        assert pokemon.id == 25
        assert pokemon.name == "Pikachu"
        assert pokemon.types == ["Electric"]
        assert pokemon.base_stats.hp == 35
        assert pokemon.base_stats.speed == 90
        assert pokemon.generation == 1
        
        mock_dex.data_loader.load_pokemon_by_id.assert_called_once_with(25)
    
    def test_get_pokemon_by_id_not_found(self, mock_dex):
        """Test getting Pokemon by ID when not found."""
        mock_dex.data_loader.load_pokemon_by_id.return_value = None
        
        with pytest.raises(PokemonNotFoundError) as exc_info:
            mock_dex.get_pokemon_by_id(99999)
        
        assert "99999" in str(exc_info.value)
    
    def test_get_pokemon_by_name(self, mock_dex):
        """Test getting Pokemon by name."""
        pokemon_data = {
            "id": 6,
            "name": "Charizard",
            "types": ["Fire", "Flying"],
            "baseStats": {"hp": 78, "attack": 84, "defense": 78, 
                         "special_attack": 109, "special_defense": 85, "speed": 100},
            "generation": 1
        }
        
        mock_dex.data_loader.load_pokemon_by_name.return_value = pokemon_data
        
        pokemon = mock_dex.get_pokemon_by_name("Charizard")
        
        assert pokemon.id == 6
        assert pokemon.name == "Charizard"
        assert pokemon.types == ["Fire", "Flying"]
        assert pokemon.base_stats.special_attack == 109
        
        mock_dex.data_loader.load_pokemon_by_name.assert_called_once_with("Charizard")
    
    def test_get_pokemon_by_name_case_insensitive(self, mock_dex):
        """Test getting Pokemon by name with different case."""
        pokemon_data = {
            "id": 1,
            "name": "Bulbasaur",
            "types": ["Grass", "Poison"],
            "baseStats": {"hp": 45, "attack": 49, "defense": 49, 
                         "special_attack": 65, "special_defense": 65, "speed": 45}
        }
        
        mock_dex.data_loader.load_pokemon_by_name.return_value = pokemon_data
        
        pokemon = mock_dex.get_pokemon_by_name("BULBASAUR")
        
        assert pokemon.name == "Bulbasaur"
        mock_dex.data_loader.load_pokemon_by_name.assert_called_with("BULBASAUR")
    
    def test_get_pokemon_by_name_not_found(self, mock_dex):
        """Test getting Pokemon by name when not found."""
        mock_dex.data_loader.load_pokemon_by_name.return_value = None
        
        with pytest.raises(PokemonNotFoundError) as exc_info:
            mock_dex.get_pokemon_by_name("NonexistentPokemon")
        
        assert "NonexistentPokemon" in str(exc_info.value)
    
    def test_get_pokemon_with_id(self, mock_dex):
        """Test get_pokemon method with ID."""
        pokemon_data = {
            "id": 150,
            "name": "Mewtwo",
            "types": ["Psychic"],
            "baseStats": {"hp": 106, "attack": 110, "defense": 90, 
                         "special_attack": 154, "special_defense": 90, "speed": 130}
        }
        
        mock_dex.data_loader.load_pokemon_by_id.return_value = pokemon_data
        
        pokemon = mock_dex.get_pokemon(150)
        
        assert pokemon.id == 150
        assert pokemon.name == "Mewtwo"
        mock_dex.data_loader.load_pokemon_by_id.assert_called_once_with(150)
    
    def test_get_pokemon_with_name(self, mock_dex):
        """Test get_pokemon method with name."""
        pokemon_data = {
            "id": 151,
            "name": "Mew",
            "types": ["Psychic"],
            "baseStats": {"hp": 100, "attack": 100, "defense": 100, 
                         "special_attack": 100, "special_defense": 100, "speed": 100}
        }
        
        mock_dex.data_loader.load_pokemon_by_name.return_value = pokemon_data
        
        pokemon = mock_dex.get_pokemon("Mew")
        
        assert pokemon.id == 151
        assert pokemon.name == "Mew"
        mock_dex.data_loader.load_pokemon_by_name.assert_called_once_with("Mew")


class TestLocalDexMoveRetrieval:
    """Test move retrieval functionality."""
    
    @pytest.fixture
    def mock_dex(self):
        """Create a LocalDex instance with mocked data loader."""
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            dex = LocalDex(enable_caching=False)
            return dex
    
    def test_get_move(self, mock_dex):
        """Test getting a move by name."""
        move_data = {
            "name": "Thunderbolt",
            "type": "Electric",
            "category": "Special",
            "basePower": 90,
            "accuracy": 100,
            "pp": 15,
            "priority": 0,
            "target": "normal",
            "desc": "A strong electric blast"
        }
        
        mock_dex.data_loader.load_move.return_value = move_data
        
        move = mock_dex.get_move("Thunderbolt")
        
        assert move.name == "Thunderbolt"
        assert move.type == "Electric"
        assert move.category == "Special"
        assert move.base_power == 90
        assert move.accuracy == 100
        assert move.pp == 15
        
        mock_dex.data_loader.load_move.assert_called_once_with("Thunderbolt")
    
    def test_get_move_not_found(self, mock_dex):
        """Test getting a move that doesn't exist."""
        mock_dex.data_loader.load_move.return_value = None
        
        with pytest.raises(MoveNotFoundError) as exc_info:
            mock_dex.get_move("NonexistentMove")
        
        assert "NonexistentMove" in str(exc_info.value)


class TestLocalDexAbilityRetrieval:
    """Test ability retrieval functionality."""
    
    @pytest.fixture
    def mock_dex(self):
        """Create a LocalDex instance with mocked data loader."""
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            dex = LocalDex(enable_caching=False)
            return dex
    
    def test_get_ability(self, mock_dex):
        """Test getting an ability by name."""
        ability_data = {
            "name": "Levitate",
            "description": "This Pokemon is immune to Ground-type moves.",
            "generation": 3,
            "rating": 3.5
        }
        
        mock_dex.data_loader.load_ability.return_value = ability_data
        
        ability = mock_dex.get_ability("Levitate")
        
        assert ability.name == "Levitate"
        assert ability.description == "This Pokemon is immune to Ground-type moves."
        assert ability.generation == 3
        assert ability.rating == 3.5
        
        mock_dex.data_loader.load_ability.assert_called_once_with("Levitate")
    
    def test_get_ability_not_found(self, mock_dex):
        """Test getting an ability that doesn't exist."""
        mock_dex.data_loader.load_ability.return_value = None
        
        with pytest.raises(AbilityNotFoundError) as exc_info:
            mock_dex.get_ability("NonexistentAbility")
        
        assert "NonexistentAbility" in str(exc_info.value)


class TestLocalDexItemRetrieval:
    """Test item retrieval functionality."""
    
    @pytest.fixture
    def mock_dex(self):
        """Create a LocalDex instance with mocked data loader."""
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            dex = LocalDex(enable_caching=False)
            return dex
    
    def test_get_item(self, mock_dex):
        """Test getting an item by name."""
        item_data = {
            "name": "Leftovers",
            "description": "Restores HP each turn.",
            "generation": 2,
            "category": "held"
        }
        
        mock_dex.data_loader.load_item.return_value = item_data
        
        item = mock_dex.get_item("Leftovers")
        
        assert item.name == "Leftovers"
        assert item.description == "Restores HP each turn."
        assert item.generation == 2
        assert item.category == "held"
        
        mock_dex.data_loader.load_item.assert_called_once_with("Leftovers")
    
    def test_get_item_not_found(self, mock_dex):
        """Test getting an item that doesn't exist."""
        mock_dex.data_loader.load_item.return_value = None
        
        with pytest.raises(ItemNotFoundError) as exc_info:
            mock_dex.get_item("NonexistentItem")
        
        assert "NonexistentItem" in str(exc_info.value)


class TestLocalDexCaching:
    """Test caching functionality."""
    
    @pytest.fixture
    def mock_dex(self):
        """Create a LocalDex instance with mocked data loader."""
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            dex = LocalDex(enable_caching=True)
            return dex
    
    def test_pokemon_caching(self, mock_dex):
        """Test that Pokemon are cached after retrieval."""
        pokemon_data = {
            "id": 1,
            "name": "Bulbasaur",
            "types": ["Grass", "Poison"],
            "baseStats": {"hp": 45, "attack": 49, "defense": 49, 
                         "special_attack": 65, "special_defense": 65, "speed": 45}
        }
        
        mock_dex.data_loader.load_pokemon_by_name.return_value = pokemon_data
        
        # First call should load from data
        pokemon1 = mock_dex.get_pokemon_by_name("Bulbasaur")
        
        # Second call should use cache
        pokemon2 = mock_dex.get_pokemon_by_name("Bulbasaur")
        
        assert pokemon1 is pokemon2  # Same object from cache
        mock_dex.data_loader.load_pokemon_by_name.assert_called_once()
    
    def test_move_caching(self, mock_dex):
        """Test that moves are cached after retrieval."""
        move_data = {
            "name": "Tackle",
            "type": "Normal",
            "category": "Physical",
            "basePower": 40,
            "accuracy": 100,
            "pp": 35
        }
        
        mock_dex.data_loader.load_move.return_value = move_data
        
        # First call should load from data
        move1 = mock_dex.get_move("Tackle")
        
        # Second call should use cache
        move2 = mock_dex.get_move("Tackle")
        
        assert move1 is move2  # Same object from cache
        mock_dex.data_loader.load_move.assert_called_once()
    
    def test_clear_cache(self, mock_dex):
        """Test clearing all caches."""
        # Add some data to caches
        mock_dex._pokemon_cache["test"] = Mock()
        mock_dex._move_cache["test"] = Mock()
        mock_dex._ability_cache["test"] = Mock()
        mock_dex._item_cache["test"] = Mock()
        
        mock_dex.clear_cache()
        
        assert len(mock_dex._pokemon_cache) == 0
        assert len(mock_dex._move_cache) == 0
        assert len(mock_dex._ability_cache) == 0
        assert len(mock_dex._item_cache) == 0
    
    def test_get_cache_stats(self, mock_dex):
        """Test getting cache statistics."""
        # Add some data to caches
        mock_dex._pokemon_cache["pokemon1"] = Mock()
        mock_dex._pokemon_cache["pokemon2"] = Mock()
        mock_dex._move_cache["move1"] = Mock()
        mock_dex._pokemon_id_cache["1"] = Mock()
        
        stats = mock_dex.get_cache_stats()
        
        assert stats["pokemon_by_name"] == 2
        assert stats["pokemon_by_id"] == 1
        assert stats["moves"] == 1
        assert stats["abilities"] == 0
        assert stats["items"] == 0


class TestLocalDexSearch:
    """Test search functionality."""
    
    @pytest.fixture
    def mock_dex(self):
        """Create a LocalDex instance with test data."""
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            
            dex = LocalDex(enable_caching=True)
            
            # Add test Pokemon to indexes
            dex._pokemon_by_type = {
                "fire": {"charizard", "charmander", "charmeleon"},
                "water": {"squirtle", "wartortle", "blastoise"},
                "grass": {"bulbasaur", "ivysaur", "venusaur"}
            }
            
            dex._pokemon_by_generation = {
                1: {"bulbasaur", "charmander", "squirtle", "charizard", "venusaur", "blastoise"}
            }
            
            return dex
    
    def test_search_pokemon_by_type(self, mock_dex):
        """Test searching Pokemon by type."""
        # Mock get_pokemon_by_name to return test Pokemon
        def mock_get_pokemon(name):
            pokemon = Mock()
            pokemon.name = name
            pokemon.types = ["Fire"] if "char" in name else ["Water"] if "squirt" in name else ["Grass"]
            pokemon.base_stats = Mock()
            pokemon.base_stats.attack = 80
            pokemon.base_stats.special_attack = 85
            pokemon.base_stats.speed = 100
            pokemon.base_stats.hp = 78
            pokemon.generation = 1
            pokemon.is_legendary = False
            pokemon.is_mythical = False
            return pokemon
        
        mock_dex.get_pokemon_by_name = mock_get_pokemon
        
        results = mock_dex.search_pokemon(type="Fire")
        
        assert len(results) == 3
        names = {pokemon.name for pokemon in results}
        assert names == {"charizard", "charmander", "charmeleon"}
    
    def test_search_pokemon_by_generation(self, mock_dex):
        """Test searching Pokemon by generation."""
        def mock_get_pokemon(name):
            pokemon = Mock()
            pokemon.name = name
            pokemon.types = ["Normal"]
            pokemon.base_stats = Mock()
            pokemon.base_stats.attack = 80
            pokemon.base_stats.special_attack = 85
            pokemon.base_stats.speed = 100
            pokemon.base_stats.hp = 78
            pokemon.generation = 1
            pokemon.is_legendary = False
            pokemon.is_mythical = False
            return pokemon
        
        mock_dex.get_pokemon_by_name = mock_get_pokemon
        
        results = mock_dex.search_pokemon(generation=1)
        
        assert len(results) == 6
        names = {pokemon.name for pokemon in results}
        assert "bulbasaur" in names
        assert "charmander" in names
        assert "squirtle" in names
    
    def test_search_pokemon_by_stats(self, mock_dex):
        """Test searching Pokemon by stat filters."""
        def mock_get_pokemon(name):
            pokemon = Mock()
            pokemon.name = name
            pokemon.types = ["Normal"]
            pokemon.base_stats = Mock()
            pokemon.base_stats.attack = 100 if "strong" in name else 50
            pokemon.base_stats.special_attack = 90 if "special" in name else 60
            pokemon.base_stats.speed = 120 if "fast" in name else 70
            pokemon.base_stats.hp = 80
            pokemon.generation = 1
            pokemon.is_legendary = False
            pokemon.is_mythical = False
            return pokemon

        # Mock the data loader to return proper data
        mock_dex.data_loader.load_all_pokemon.return_value = []
        mock_dex.get_pokemon_by_name = mock_get_pokemon
        mock_dex._pokemon_by_type["normal"] = {"strongpokemon", "specialpokemon", "fastpokemon"}

        results = mock_dex.search_pokemon(type="Normal", min_attack=90)

        assert len(results) == 1
        assert results[0].name == "strongpokemon"
    
    def test_search_pokemon_multiple_filters(self, mock_dex):
        """Test searching Pokemon with multiple filters."""
        def mock_get_pokemon(name):
            pokemon = Mock()
            pokemon.name = name
            pokemon.types = ["Fire"] if "char" in name else ["Water"]
            pokemon.base_stats = Mock()
            pokemon.base_stats.attack = 100 if "charizard" in name else 50
            pokemon.base_stats.special_attack = 85
            pokemon.base_stats.speed = 100
            pokemon.base_stats.hp = 78
            pokemon.generation = 1
            pokemon.is_legendary = False
            pokemon.is_mythical = False
            return pokemon
        
        mock_dex.get_pokemon_by_name = mock_get_pokemon
        
        results = mock_dex.search_pokemon(type="Fire", min_attack=90)
        
        assert len(results) == 1
        assert results[0].name == "charizard"
    
    def test_search_pokemon_name_contains(self, mock_dex):
        """Test searching Pokemon by partial name match."""
        def mock_get_pokemon(name):
            pokemon = Mock()
            pokemon.name = name
            pokemon.types = ["Normal"]
            pokemon.base_stats = Mock()
            pokemon.base_stats.attack = 80
            pokemon.base_stats.special_attack = 85
            pokemon.base_stats.speed = 100
            pokemon.base_stats.hp = 78
            pokemon.generation = 1
            pokemon.is_legendary = False
            pokemon.is_mythical = False
            return pokemon

        # Mock the data loader to return proper data
        mock_dex.data_loader.load_all_pokemon.return_value = []
        mock_dex.get_pokemon_by_name = mock_get_pokemon
        mock_dex._pokemon_by_type["normal"] = {"charizard", "charmander", "charmeleon"}

        results = mock_dex.search_pokemon(type="Normal", name_contains="char")

        assert len(results) == 3
        names = {pokemon.name for pokemon in results}
        assert names == {"charizard", "charmander", "charmeleon"}
    
    def test_search_pokemon_legendary_filter(self, mock_dex):
        """Test searching Pokemon by legendary status."""
        def mock_get_pokemon(name):
            pokemon = Mock()
            pokemon.name = name
            pokemon.types = ["Psychic"]
            pokemon.base_stats = Mock()
            pokemon.base_stats.attack = 110
            pokemon.base_stats.special_attack = 154
            pokemon.base_stats.speed = 130
            pokemon.base_stats.hp = 106
            pokemon.generation = 1
            pokemon.is_legendary = True if "mewtwo" in name else False
            pokemon.is_mythical = False
            return pokemon

        # Mock the data loader to return proper data
        mock_dex.data_loader.load_all_pokemon.return_value = []
        mock_dex.get_pokemon_by_name = mock_get_pokemon
        mock_dex._pokemon_by_type["psychic"] = {"mewtwo", "alakazam"}

        results = mock_dex.search_pokemon(type="Psychic", is_legendary=True)

        assert len(results) == 1
        assert results[0].name == "mewtwo"


class TestLocalDexDataCreation:
    """Test data object creation from raw data."""
    
    @pytest.fixture
    def mock_dex(self):
        """Create a LocalDex instance with mocked data loader."""
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            dex = LocalDex(enable_caching=False)
            return dex
    
    def test_create_pokemon_from_data(self, mock_dex):
        """Test creating Pokemon object from raw data."""
        pokemon_data = {
            "id": 25,
            "name": "Pikachu",
            "types": ["Electric"],
            "baseStats": {
                "hp": 35,
                "attack": 55,
                "defense": 40,
                "special_attack": 50,
                "special_defense": 50,
                "speed": 90
            },
            "height": 0.4,
            "weight": 6.0,
            "color": "Yellow",
            "abilities": {"0": "Static", "1": "Lightning Rod"},
            "generation": 1,
            "description": "A mouse Pokemon",
            "isLegendary": False,
            "isMythical": False,
            "isUltraBeast": False
        }
        
        pokemon = mock_dex._create_pokemon_from_data(pokemon_data)
        
        assert pokemon.id == 25
        assert pokemon.name == "Pikachu"
        assert pokemon.types == ["Electric"]
        assert pokemon.base_stats.hp == 35
        assert pokemon.base_stats.speed == 90
        assert pokemon.height == 0.4
        assert pokemon.weight == 6.0
        assert pokemon.color == "Yellow"
        assert pokemon.abilities == {"0": "Static", "1": "Lightning Rod"}
        assert pokemon.generation == 1
        assert pokemon.description == "A mouse Pokemon"
        assert pokemon.is_legendary is False
        assert pokemon.is_mythical is False
        assert pokemon.is_ultra_beast is False
    
    def test_create_move_from_data(self, mock_dex):
        """Test creating Move object from raw data."""
        move_data = {
            "name": "Thunderbolt",
            "type": "Electric",
            "category": "Special",
            "basePower": 90,
            "accuracy": 100,
            "pp": 15,
            "priority": 0,
            "target": "normal",
            "desc": "A strong electric blast",
            "shortDesc": "Strong electric attack",
            "contestType": "Cool",
            "critRatio": 1,
            "flags": {"protect": True, "mirror": True},
            "drain": 0,
            "isZ": False,
            "num": 85
        }
        
        move = mock_dex._create_move_from_data(move_data)
        
        assert move.name == "Thunderbolt"
        assert move.type == "Electric"
        assert move.category == "Special"
        assert move.base_power == 90
        assert move.accuracy == 100
        assert move.pp == 15
        assert move.priority == 0
        assert move.target == "normal"
        assert move.description == "A strong electric blast"
        assert move.short_description == "Strong electric attack"
        assert move.contest_type == "Cool"
        assert move.crit_ratio == 1
        assert move.flags == {"protect": True, "mirror": True}
        assert move.drain == 0
        assert move.z_move is False
        assert move.generation == 85
    
    def test_create_ability_from_data(self, mock_dex):
        """Test creating Ability object from raw data."""
        ability_data = {
            "name": "Levitate",
            "description": "This Pokemon is immune to Ground-type moves.",
            "short_description": "Immune to Ground moves",
            "generation": 3,
            "rating": 3.5,
            "num": 26,
            "effect": "This Pokemon is immune to Ground-type moves."
        }
        
        ability = mock_dex._create_ability_from_data(ability_data)
        
        assert ability.name == "Levitate"
        assert ability.description == "This Pokemon is immune to Ground-type moves."
        assert ability.short_description == "Immune to Ground moves"
        assert ability.generation == 3
        assert ability.rating == 3.5
        assert ability.num == 26
        assert ability.effect == "This Pokemon is immune to Ground-type moves."
    
    def test_create_item_from_data(self, mock_dex):
        """Test creating Item object from raw data."""
        item_data = {
            "name": "Leftovers",
            "description": "Restores HP each turn.",
            "shortDesc": "Restores HP",
            "gen": 2,
            "num": 234,
            "spritenum": 2,
            "fling": {"basePower": 10},
            "megaStone": False,
            "megaEvolves": None,
            "zMove": False,
            "zMoveType": None,
            "zMoveFrom": None,
            "itemUser": None,
            "onPlate": False,
            "onDrive": False,
            "onMemory": False,
            "forcedForme": None,
            "isNonstandard": False,
            "category": "held"
        }
        
        item = mock_dex._create_item_from_data(item_data)
        
        assert item.name == "Leftovers"
        assert item.description == "Restores HP each turn."
        assert item.short_description == "Restores HP"
        assert item.generation == 2
        assert item.num == 234
        assert item.spritenum == 2
        assert item.fling == {"basePower": 10}
        assert item.mega_stone is False
        assert item.mega_evolves is None
        assert item.z_move is False
        assert item.category == "held"


class TestLocalDexBulkOperations:
    """Test bulk data retrieval operations."""
    
    @pytest.fixture
    def mock_dex(self):
        """Create a LocalDex instance with mocked data loader."""
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            dex = LocalDex(enable_caching=False)
            return dex
    
    def test_get_all_pokemon(self, mock_dex):
        """Test getting all Pokemon."""
        pokemon_data_list = [
            {"id": 1, "name": "Bulbasaur", "types": ["Grass", "Poison"], 
             "baseStats": {"hp": 45, "attack": 49, "defense": 49, 
                          "special_attack": 65, "special_defense": 65, "speed": 45}},
            {"id": 4, "name": "Charmander", "types": ["Fire"], 
             "baseStats": {"hp": 39, "attack": 52, "defense": 43, 
                          "special_attack": 60, "special_defense": 50, "speed": 65}}
        ]
        
        mock_dex.data_loader.load_all_pokemon.return_value = pokemon_data_list
        
        pokemon_list = mock_dex.get_all_pokemon()
        
        assert len(pokemon_list) == 2
        assert pokemon_list[0].name == "Bulbasaur"
        assert pokemon_list[1].name == "Charmander"
        
        mock_dex.data_loader.load_all_pokemon.assert_called_once()
    
    def test_get_all_moves(self, mock_dex):
        """Test getting all moves."""
        move_data_list = [
            {"name": "Tackle", "type": "Normal", "category": "Physical", 
             "basePower": 40, "accuracy": 100, "pp": 35},
            {"name": "Thunderbolt", "type": "Electric", "category": "Special", 
             "basePower": 90, "accuracy": 100, "pp": 15}
        ]
        
        mock_dex.data_loader.load_all_moves.return_value = move_data_list
        
        move_list = mock_dex.get_all_moves()
        
        assert len(move_list) == 2
        assert move_list[0].name == "Tackle"
        assert move_list[1].name == "Thunderbolt"
        
        mock_dex.data_loader.load_all_moves.assert_called_once()
    
    def test_get_all_abilities(self, mock_dex):
        """Test getting all abilities."""
        ability_data_list = [
            {"name": "Levitate", "description": "Immune to Ground moves"},
            {"name": "Static", "description": "May paralyze on contact"}
        ]
        
        mock_dex.data_loader.load_all_abilities.return_value = ability_data_list
        
        ability_list = mock_dex.get_all_abilities()
        
        assert len(ability_list) == 2
        assert ability_list[0].name == "Levitate"
        assert ability_list[1].name == "Static"
        
        mock_dex.data_loader.load_all_abilities.assert_called_once()
    
    def test_get_all_items(self, mock_dex):
        """Test getting all items."""
        item_data_list = [
            {"name": "Leftovers", "description": "Restores HP each turn"},
            {"name": "Choice Band", "description": "Boosts Attack but locks moves"}
        ]
        
        mock_dex.data_loader.load_all_items.return_value = item_data_list
        
        item_list = mock_dex.get_all_items()
        
        assert len(item_list) == 2
        assert item_list[0].name == "Leftovers"
        assert item_list[1].name == "Choice Band"
        
        mock_dex.data_loader.load_all_items.assert_called_once()


class TestLocalDexStatGuesser:
    """Test stat guessing functionality."""
    
    @pytest.fixture
    def mock_dex(self):
        """Create a LocalDex instance with mocked dependencies."""
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            dex = LocalDex(enable_caching=False)
            return dex
    
    def test_create_stat_guesser(self, mock_dex):
        """Test creating a BattleStatGuesser instance."""
        with patch('localdex.core.BattleStatGuesser') as mock_guesser_class:
            mock_guesser = Mock()
            mock_guesser_class.return_value = mock_guesser
            
            guesser = mock_dex.create_stat_guesser("gen9ou")
            
            mock_guesser_class.assert_called_once_with("gen9ou", mock_dex)
            assert guesser == mock_guesser
    
    def test_guess_pokemon_stats(self, mock_dex):
        """Test guessing Pokemon stats."""
        with patch('localdex.core.BattleStatGuesser') as mock_guesser_class:
            mock_guesser = Mock()
            mock_guesser_class.return_value = mock_guesser
            
            pokemon_set = Mock()
            expected_result = {"role": "attacker", "evs": {"atk": 252, "spe": 252}}
            mock_guesser.guess.return_value = expected_result
            
            result = mock_dex.guess_pokemon_stats(pokemon_set, "gen9ou")
            
            assert result == expected_result
            mock_guesser.guess.assert_called_once_with(pokemon_set)
    
    def test_optimize_pokemon_stats(self, mock_dex):
        """Test optimizing Pokemon stats."""
        with patch('localdex.core.battle_stat_optimizer') as mock_optimizer:
            pokemon_set = Mock()
            expected_result = {"optimized_evs": {"atk": 252, "spe": 252}}
            mock_optimizer.return_value = expected_result
            
            result = mock_dex.optimize_pokemon_stats(pokemon_set, "gen9ou")
            
            assert result == expected_result
            mock_optimizer.assert_called_once_with(pokemon_set, "gen9ou", mock_dex)


class TestLocalDexErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.fixture
    def mock_dex(self):
        """Create a LocalDex instance with mocked data loader."""
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            dex = LocalDex(enable_caching=False)
            return dex
    
    def test_search_error_handling(self, mock_dex):
        """Test that search errors are properly handled."""
        # Mock get_all_pokemon to raise an exception
        mock_dex.get_all_pokemon = Mock(side_effect=Exception("Test error"))
        
        with pytest.raises(SearchError) as exc_info:
            mock_dex.search_pokemon(type="Fire")
        
        assert "Error during Pokemon search" in str(exc_info.value)
    
    def test_index_building_error_handling(self, mock_dex):
        """Test that index building errors don't crash initialization."""
        # Mock get_all_pokemon to raise an exception during index building
        with patch.object(LocalDex, 'get_all_pokemon', side_effect=Exception("Index error")):
            # Should not raise an exception, just continue without indexes
            dex = LocalDex(enable_caching=True)
            assert len(dex._pokemon_by_type) == 0
            assert len(dex._pokemon_by_generation) == 0
    
    def test_missing_data_handling(self, mock_dex):
        """Test handling of missing or incomplete data."""
        # Test with minimal Pokemon data
        minimal_data = {
            "id": 1,
            "name": "TestPokemon",
            "types": ["Normal"],
            "baseStats": {"hp": 50, "attack": 50, "defense": 50, 
                         "special_attack": 50, "special_defense": 50, "speed": 50}
        }
        
        pokemon = mock_dex._create_pokemon_from_data(minimal_data)
        
        assert pokemon.id == 1
        assert pokemon.name == "TestPokemon"
        assert pokemon.types == ["Normal"]
        # Optional fields should have default values
        assert pokemon.height is None
        assert pokemon.weight is None
        assert pokemon.generation is None
        assert pokemon.is_legendary is False
        assert pokemon.is_mythical is False
        assert pokemon.is_ultra_beast is False


class TestLocalDexIntegration:
    """Integration tests for LocalDex functionality."""
    
    def test_full_workflow(self):
        """Test a complete workflow with LocalDex."""
        with patch('localdex.core.DataLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            
            # Mock data
            pokemon_data = {
                "id": 25,
                "name": "Pikachu",
                "types": ["Electric"],
                "baseStats": {"hp": 35, "attack": 55, "defense": 40, 
                             "special_attack": 50, "special_defense": 50, "speed": 90},
                "generation": 1
            }
            
            move_data = {
                "name": "Thunderbolt",
                "type": "Electric",
                "category": "Special",
                "basePower": 90,
                "accuracy": 100,
                "pp": 15
            }
            
            mock_loader.load_pokemon_by_name.return_value = pokemon_data
            mock_loader.load_move.return_value = move_data
            
            # Create LocalDex instance
            dex = LocalDex(enable_caching=True)
            
            # Get Pokemon and move
            pokemon = dex.get_pokemon("Pikachu")
            move = dex.get_move("Thunderbolt")
            
            # Verify data
            assert pokemon.name == "Pikachu"
            assert pokemon.types == ["Electric"]
            assert move.name == "Thunderbolt"
            assert move.type == "Electric"
            
            # Check cache stats
            stats = dex.get_cache_stats()
            assert stats["pokemon_by_name"] == 1
            assert stats["moves"] == 1
            
            # Clear cache
            dex.clear_cache()
            stats = dex.get_cache_stats()
            assert stats["pokemon_by_name"] == 0
            assert stats["moves"] == 0


if __name__ == "__main__":
    pytest.main([__file__])
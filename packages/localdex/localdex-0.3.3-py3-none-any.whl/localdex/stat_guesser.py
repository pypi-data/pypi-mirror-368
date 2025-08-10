"""
Stat guessing functionality for LocalDex.

This module provides functionality for guessing Pokemon stats and optimizing EV spreads,
replicating the functionality from stat_utils.ts.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum

from .models import Pokemon, Move, Ability, Item, BaseStats
from .stat_calculator import StatCalculator


class StatName(str, Enum):
    """Pokemon stat names."""
    HP = "hp"
    ATK = "atk"
    DEF = "def"
    SPA = "spa"
    SPD = "spd"
    SPE = "spe"


class MoveCategory(str, Enum):
    """Move categories."""
    PHYSICAL = "Physical"
    SPECIAL = "Special"
    STATUS = "Status"


# Nature modifier system
NATURE_MODIFIERS = {
    "Hardy": {"plus": None, "minus": None},
    "Lonely": {"plus": "attack", "minus": "defense"},
    "Brave": {"plus": "attack", "minus": "speed"},
    "Adamant": {"plus": "attack", "minus": "special_attack"},
    "Naughty": {"plus": "attack", "minus": "special_defense"},
    "Bold": {"plus": "defense", "minus": "attack"},
    "Docile": {"plus": None, "minus": None},
    "Relaxed": {"plus": "defense", "minus": "speed"},
    "Impish": {"plus": "defense", "minus": "special_attack"},
    "Lax": {"plus": "defense", "minus": "special_defense"},
    "Timid": {"plus": "speed", "minus": "attack"},
    "Hasty": {"plus": "speed", "minus": "defense"},
    "Serious": {"plus": None, "minus": None},
    "Jolly": {"plus": "speed", "minus": "special_attack"},
    "Naive": {"plus": "speed", "minus": "special_defense"},
    "Modest": {"plus": "special_attack", "minus": "attack"},
    "Mild": {"plus": "special_attack", "minus": "defense"},
    "Quiet": {"plus": "special_attack", "minus": "speed"},
    "Bashful": {"plus": None, "minus": None},
    "Rash": {"plus": "special_attack", "minus": "special_defense"},
    "Calm": {"plus": "special_defense", "minus": "attack"},
    "Gentle": {"plus": "special_defense", "minus": "defense"},
    "Sassy": {"plus": "special_defense", "minus": "speed"},
    "Careful": {"plus": "special_defense", "minus": "special_attack"},
    "Quirky": {"plus": None, "minus": None},
}


@dataclass
class PokemonSet:
    """Represents a Pokemon set with moves, items, abilities, etc."""
    species: str
    name: Optional[str] = None
    item: Optional[str] = None
    ability: Optional[str] = None
    nature: Optional[str] = None
    level: int = 100
    moves: List[str] = None
    evs: Optional[Dict[str, int]] = None
    ivs: Optional[Dict[str, int]] = None
    
    def __post_init__(self):
        if self.moves is None:
            self.moves = []
        if self.evs is None:
            self.evs = {}
        if self.ivs is None:
            self.ivs = {}


class BattleStatGuesser:
    """
    A class for guessing Pokemon stats and roles based on moves, items, and abilities.
    
    This replicates the functionality from the TypeScript BattleStatGuesser class.
    """
    
    def __init__(self, format_id: str, localdex):
        """
        Initialize the BattleStatGuesser.
        
        Args:
            format_id: The format ID (e.g., "gen9ou")
            localdex: LocalDex instance for accessing Pokemon data
        """
        self.format_id = format_id
        self.localdex = localdex
        self.stat_calculator = StatCalculator(localdex)
        self.move_count = None
        self.has_move = None
        
        # Format-specific settings
        self.ignore_ev_limits = self._should_ignore_ev_limits(format_id)
        self.supports_evs = "letsgo" not in format_id.lower()
        self.supports_avs = "letsgo" in format_id.lower()
    
    def _should_ignore_ev_limits(self, format_id: str) -> bool:
        """Determine if EV limits should be ignored for this format."""
        format_lower = format_id.lower()
        return (
            format_lower.startswith("gen1") or format_lower.startswith("gen2") or
            format_lower.endswith("hackmons") or format_lower.endswith("bh") or
            "metronomebattle" in format_lower or format_lower.endswith("norestrictions")
        )
    
    def guess(self, pokemon_set: PokemonSet) -> Dict[str, Any]:
        """
        Guess the role and EV spread for a Pokemon set.
        
        Args:
            pokemon_set: The Pokemon set to analyze
            
        Returns:
            Dictionary containing role, EVs, plus/minus stats, and move information
        """
        role = self.guess_role(pokemon_set)
        combo_evs = self.guess_evs(pokemon_set, role)
        
        evs = {stat.value: 0 for stat in StatName}
        for stat in evs:
            evs[stat] = combo_evs.get(stat, 0)
        
        plus_stat = combo_evs.get('plusStat', '')
        minus_stat = combo_evs.get('minusStat', '')
        
        return {
            'role': role,
            'evs': evs,
            'plusStat': plus_stat,
            'minusStat': minus_stat,
            'moveCount': self.move_count,
            'hasMove': self.has_move
        }
    
    def guess_role(self, pokemon_set: PokemonSet) -> str:
        """
        Guess the role of a Pokemon based on its moves, stats, and items.
        
        Args:
            pokemon_set: The Pokemon set to analyze
            
        Returns:
            The guessed role as a string
        """
        if not pokemon_set or not pokemon_set.moves:
            return '?'
        
        # Initialize move counters
        move_count = {
            'Physical': 0,
            'Special': 0,
            'PhysicalAttack': 0,
            'SpecialAttack': 0,
            'PhysicalSetup': 0,
            'SpecialSetup': 0,
            'Support': 0,
            'Setup': 0,
            'Restoration': 0,
            'Offense': 0,
            'Stall': 0,
            'SpecialStall': 0,
            'PhysicalStall': 0,
            'Fast': 0,
            'Ultrafast': 0,
            'bulk': 0,
            'specialBulk': 0,
            'physicalBulk': 0,
        }
        
        has_move = {}
        item_id = self._to_id(pokemon_set.item) if pokemon_set.item else ""
        ability_id = self._to_id(pokemon_set.ability) if pokemon_set.ability else ""
        
        try:
            species = self.localdex.get_pokemon(pokemon_set.species)
        except:
            return '?'
        
        # Handle mega evolution
        if pokemon_set.item:
            try:
                item = self.localdex.get_item(pokemon_set.item)
                if hasattr(item, 'mega_evolves') and item.mega_evolves == species.name:
                    species = self.localdex.get_pokemon(item.mega_stone)
            except:
                pass
        
        stats = species.base_stats
        
        if len(pokemon_set.moves) < 1:
            return '?'
        
        needs_four_moves = species.name.lower() not in ['unown', 'ditto']
        has_four_valid_moves = len(pokemon_set.moves) >= 4 and all(move for move in pokemon_set.moves)
        move_ids = [self._to_id(move) for move in pokemon_set.moves]
        
        if 'lastresort' in move_ids:
            needs_four_moves = False
        
        if not has_four_valid_moves and needs_four_moves and 'metronomebattle' not in self.format_id:
            return '?'
        
        # Analyze moves
        for move_name in pokemon_set.moves:
            try:
                move = self.localdex.get_move(move_name)
                has_move[move.name.lower()] = 1
                
                if move.category == MoveCategory.STATUS:
                    self._analyze_status_move(move, move_count, has_move)
                else:
                    self._analyze_attack_move(move, move_count, has_move)
                    
            except:
                continue
        
        # Post-process move counts
        if has_move.get('batonpass'):
            move_count['Support'] += move_count['Setup']
        
        move_count['PhysicalAttack'] = move_count['Physical']
        move_count['Physical'] += move_count['PhysicalSetup']
        move_count['SpecialAttack'] = move_count['Special']
        move_count['Special'] += move_count['SpecialSetup']
        
        if has_move.get('dragondance') or has_move.get('quiverdance'):
            move_count['Ultrafast'] = 1
        
        # Calculate bulk and speed characteristics
        is_fast = stats.speed >= 80
        physical_bulk = (stats.hp + 75) * (stats.defense + 87)
        special_bulk = (stats.hp + 75) * (stats.special_defense + 87)
        
        # Apply bulk modifiers based on moves and abilities
        physical_bulk, special_bulk = self._apply_bulk_modifiers(
            physical_bulk, special_bulk, has_move, ability_id, item_id, move_count
        )
        
        bulk = physical_bulk + special_bulk
        if bulk < 46000 and stats.speed >= 70:
            is_fast = True
        if has_move.get('trickroom'):
            is_fast = False
        
        move_count['bulk'] = bulk
        move_count['physicalBulk'] = physical_bulk
        move_count['specialBulk'] = special_bulk
        
        # Determine speed characteristics
        is_fast = self._determine_speed_characteristics(
            is_fast, has_move, ability_id, item_id, move_count
        )
        
        self.move_count = move_count
        self.has_move = has_move
        
        # Special cases
        if species.name.lower() == 'ditto':
            return 'Physically Defensive' if ability_id == 'imposter' else 'Fast Bulky Support'
        if species.name.lower() == 'shedinja':
            return 'Fast Physical Sweeper'
        
        # Determine role based on item and move patterns
        role = self._determine_role_from_patterns(
            item_id, move_count, is_fast, stats, has_move, ability_id, physical_bulk, special_bulk
        )
        
        return role
    
    def _analyze_status_move(self, move, move_count, has_move):
        """Analyze a status move and update move counts."""
        move_id = move.name.lower()
        
        if move_id in ['batonpass', 'healingwish', 'lunardance']:
            move_count['Support'] += 1
        elif move_id in ['metronome', 'assist', 'copycat', 'mefirst', 'photongeyser', 'shellsidearm']:
            move_count['Physical'] += 0.5
            move_count['Special'] += 0.5
        elif move_id == 'naturepower':
            move_count['Special'] += 1
        elif move_id in ['protect', 'detect', 'spikyshield', 'kingsshield']:
            move_count['Stall'] += 1
        elif move_id == 'wish':
            move_count['Restoration'] += 1
            move_count['Stall'] += 1
            move_count['Support'] += 1
        elif move.drain and move.drain[0] > 0:  # Use drain instead of heal
            move_count['Restoration'] += 1
            move_count['Stall'] += 1
        elif move.target == 'self':  # target is always available
            if move_id in ['agility', 'rockpolish', 'shellsmash', 'growth', 'workup']:
                move_count['PhysicalSetup'] += 1
                move_count['SpecialSetup'] += 1
            elif move_id in ['dragondance', 'swordsdance', 'coil', 'bulkup', 'curse', 'bellydrum']:
                move_count['PhysicalSetup'] += 1
            elif move_id in ['nastyplot', 'tailglow', 'quiverdance', 'calmmind', 'geomancy']:
                move_count['SpecialSetup'] += 1
            
            if move_id == 'substitute':
                move_count['Stall'] += 1
            move_count['Setup'] += 1
        else:
            if move_id in ['toxic', 'leechseed', 'willowisp']:
                move_count['Stall'] += 1
            move_count['Support'] += 1
    
    def _analyze_attack_move(self, move, move_count, has_move):
        """Analyze an attack move and update move counts."""
        move_id = move.name.lower()
        
        if move_id in ['counter', 'endeavor', 'metalburst', 'mirrorcoat', 'rapidspin']:
            move_count['Support'] += 1
        elif move_id in [
            'nightshade', 'seismictoss', 'psywave', 'superfang', 'naturesmadness', 
            'foulplay', 'endeavor', 'finalgambit', 'bodypress'
        ]:
            move_count['Offense'] += 1
        elif move_id == 'fellstinger':
            move_count['PhysicalSetup'] += 1
            move_count['Setup'] += 1
        else:
            move_count[move.category] += 1
            move_count['Offense'] += 1
            
            if move_id == 'knockoff':
                move_count['Support'] += 1
            
            if move_id in ['scald', 'voltswitch', 'uturn', 'flipturn']:
                move_count[move.category] -= 0.2
    
    def _apply_bulk_modifiers(self, physical_bulk, special_bulk, has_move, ability_id, item_id, move_count):
        """Apply bulk modifiers based on moves, abilities, and items."""
        # Physical bulk modifiers
        if has_move.get('willowisp') or has_move.get('acidarmor') or has_move.get('irondefense') or has_move.get('cottonguard'):
            physical_bulk *= 1.6
            move_count['PhysicalStall'] += 1
        elif has_move.get('scald') or has_move.get('bulkup') or has_move.get('coil') or has_move.get('cosmicpower'):
            physical_bulk *= 1.3
            if has_move.get('scald'):
                move_count['SpecialStall'] += 1
            else:
                move_count['PhysicalStall'] += 1
        
        if ability_id == 'flamebody':
            physical_bulk *= 1.1
        
        # Special bulk modifiers
        if has_move.get('calmmind') or has_move.get('quiverdance') or has_move.get('geomancy'):
            special_bulk *= 1.3
            move_count['SpecialStall'] += 1
        
        # Item and ability modifiers
        if item_id in ['leftovers', 'blacksludge']:
            modifier = 1 + 0.1 * (1 + move_count['Stall'] / 1.5)
            physical_bulk *= modifier
            special_bulk *= modifier
        
        if has_move.get('leechseed'):
            modifier = 1 + 0.1 * (1 + move_count['Stall'] / 1.5)
            physical_bulk *= modifier
            special_bulk *= modifier
        
        if item_id in ['flameorb', 'toxicorb'] and ability_id != 'magicguard':
            if item_id == 'toxicorb' and ability_id == 'poisonheal':
                modifier = 1 + 0.1 * (2 + move_count['Stall'])
                physical_bulk *= modifier
                special_bulk *= modifier
            else:
                physical_bulk *= 0.8
                special_bulk *= 0.8
        
        if item_id == 'lifeorb':
            physical_bulk *= 0.7
            special_bulk *= 0.7
        
        if ability_id in ['multiscale', 'magicguard', 'regenerator']:
            physical_bulk *= 1.4
            special_bulk *= 1.4
        
        if item_id == 'eviolite':
            physical_bulk *= 1.5
            special_bulk *= 1.5
        
        if item_id == 'assaultvest':
            special_bulk *= 1.5
        
        return physical_bulk, special_bulk
    
    def _determine_speed_characteristics(self, is_fast, has_move, ability_id, item_id, move_count):
        """Determine speed characteristics based on moves and abilities."""
        if (has_move.get('agility') or has_move.get('dragondance') or has_move.get('quiverdance') or
            has_move.get('rockpolish') or has_move.get('shellsmash') or has_move.get('flamecharge')):
            is_fast = True
        elif ability_id in ['unburden', 'speedboost', 'motordrive']:
            is_fast = True
            move_count['Ultrafast'] = 1
        elif ability_id in ['chlorophyll', 'swiftswim', 'sandrush']:
            is_fast = True
            move_count['Ultrafast'] = 2
        elif item_id == 'salacberry':
            is_fast = True
        
        ultrafast = (has_move.get('agility') or has_move.get('shellsmash') or
                    has_move.get('autotomize') or has_move.get('shiftgear') or has_move.get('rockpolish'))
        if ultrafast:
            move_count['Ultrafast'] = 2
        
        move_count['Fast'] = 1 if is_fast else 0
        return is_fast
    
    def _determine_role_from_patterns(self, item_id, move_count, is_fast, stats, has_move, ability_id, physical_bulk, special_bulk):
        """Determine the role based on patterns in moves, items, and stats."""
        # Choice item patterns
        if item_id == 'choiceband' and move_count['PhysicalAttack'] >= 2:
            return 'Bulky Band' if not is_fast else 'Fast Band'
        elif item_id == 'choicespecs' and move_count['SpecialAttack'] >= 2:
            return 'Bulky Specs' if not is_fast else 'Fast Specs'
        elif item_id == 'choicescarf':
            if move_count['PhysicalAttack'] == 0:
                return 'Special Scarf'
            elif move_count['SpecialAttack'] == 0:
                return 'Physical Scarf'
            elif move_count['PhysicalAttack'] > move_count['SpecialAttack']:
                return 'Physical Biased Mixed Scarf'
            elif move_count['PhysicalAttack'] < move_count['SpecialAttack']:
                return 'Special Biased Mixed Scarf'
            elif stats.special_attack < stats.attack:
                return 'Special Biased Mixed Scarf'
            else:
                return 'Physical Biased Mixed Scarf'
        
        # Special cases
        if has_move.get('unown'):
            return 'Fast Special Sweeper'
        
        # Defensive patterns
        if move_count['PhysicalStall'] and move_count['Restoration']:
            return 'Fast Bulky Support' if stats.speed > 110 and ability_id != 'prankster' else 'Specially Defensive'
        if move_count['SpecialStall'] and move_count['Restoration'] and item_id != 'lifeorb':
            return 'Fast Bulky Support' if stats.speed > 110 and ability_id != 'prankster' else 'Physically Defensive'
        
        # Offensive bias
        offense_bias = 'Physical'
        if stats.special_attack > stats.attack and move_count['Special'] > 1:
            offense_bias = 'Special'
        elif stats.attack > stats.special_attack and move_count['Physical'] > 1:
            offense_bias = 'Physical'
        elif move_count['Special'] > move_count['Physical']:
            offense_bias = 'Special'
        
        # Sweeper patterns
        if (move_count['Stall'] + move_count['Support'] / 2 <= 2 and 
            move_count['bulk'] < 135000 and move_count[offense_bias] >= 1.5):
            if is_fast:
                if move_count['bulk'] > 80000 and not move_count['Ultrafast']:
                    return f'Bulky {offense_bias} Sweeper'
                return f'Fast {offense_bias} Sweeper'
            else:
                if move_count[offense_bias] >= 3 or move_count['Stall'] <= 0:
                    return f'Bulky {offense_bias} Sweeper'
        
        # Support patterns
        if is_fast and ability_id != 'prankster':
            if stats.speed > 100 or move_count['bulk'] < 55000 or move_count['Ultrafast']:
                return 'Fast Bulky Support'
        
        # Defensive patterns
        if move_count['SpecialStall']:
            return 'Physically Defensive'
        if move_count['PhysicalStall']:
            return 'Specially Defensive'
        
        # Default defensive role
        if special_bulk >= physical_bulk:
            return 'Specially Defensive'
        return 'Physically Defensive'
    
    def guess_evs(self, pokemon_set: PokemonSet, role: str) -> Dict[str, Any]:
        """
        Guess EV spread for a Pokemon based on its role.
        
        Args:
            pokemon_set: The Pokemon set
            role: The guessed role
            
        Returns:
            Dictionary containing EV spread and nature information
        """
        if not pokemon_set or role == '?':
            return {}
        
        try:
            species = self.localdex.get_pokemon(pokemon_set.species)
        except:
            return {}
        
        stats = species.base_stats
        has_move = self.has_move
        move_count = self.move_count
        
        evs = {stat.value: 0 for stat in StatName}
        plus_stat = None
        minus_stat = None
        
        # Role-based stat priorities
        stat_chart = {
            'Bulky Band': ['atk', 'hp'],
            'Fast Band': ['spe', 'atk'],
            'Bulky Specs': ['spa', 'hp'],
            'Fast Specs': ['spe', 'spa'],
            'Physical Scarf': ['spe', 'atk'],
            'Special Scarf': ['spe', 'spa'],
            'Physical Biased Mixed Scarf': ['spe', 'atk'],
            'Special Biased Mixed Scarf': ['spe', 'spa'],
            'Fast Physical Sweeper': ['spe', 'atk'],
            'Fast Special Sweeper': ['spe', 'spa'],
            'Bulky Physical Sweeper': ['atk', 'hp'],
            'Bulky Special Sweeper': ['spa', 'hp'],
            'Fast Bulky Support': ['spe', 'hp'],
            'Physically Defensive': ['def', 'hp'],
            'Specially Defensive': ['spd', 'hp'],
        }
        
        if role not in stat_chart:
            return {}
        
        plus_stat = stat_chart[role][0]
        if role == 'Fast Bulky Support':
            move_count['Ultrafast'] = 0
        
        if plus_stat == 'spe' and move_count.get('Ultrafast'):
            if stat_chart[role][1] in ['atk', 'spa']:
                plus_stat = stat_chart[role][1]
            elif move_count.get('Physical', 0) >= 3:
                plus_stat = 'atk'
            elif stats.special_defense > stats.defense:
                plus_stat = 'spd'
            else:
                plus_stat = 'def'
        
        # Handle different EV systems
        if self.supports_avs:
            # Let's Go, AVs enabled
            evs = {stat.value: 200 for stat in StatName}
            if not move_count.get('PhysicalAttack'):
                evs['atk'] = 0
            if not move_count.get('SpecialAttack'):
                evs['spa'] = 0
            if has_move.get('gyroball') or has_move.get('trickroom'):
                evs['spe'] = 0
        elif not self.supports_evs:
            # Let's Go, AVs disabled
            pass
        elif self.ignore_ev_limits:
            # Gen 1-2, hackable EVs
            evs = {stat.value: 252 for stat in StatName}
            if not move_count.get('PhysicalAttack'):
                evs['atk'] = 0
            if not move_count.get('SpecialAttack'):
                evs['spa'] = 0
            if has_move.get('gyroball') or has_move.get('trickroom'):
                evs['spe'] = 0
        else:
            # Normal Gen 3+ EV system
            evs = self._calculate_normal_evs(pokemon_set, role, stat_chart, plus_stat, stats, has_move, move_count)
        
        # Determine minus stat
        minus_stat = self._determine_minus_stat(has_move, move_count, stats, evs, plus_stat)
        
        return {
            **evs,
            'plusStat': plus_stat,
            'minusStat': minus_stat
        }
    
    def _calculate_normal_evs(self, pokemon_set, role, stat_chart, plus_stat, stats, has_move, move_count):
        """Calculate EVs for normal Gen 3+ system."""
        evs = {stat.value: 0 for stat in StatName}
        ev_total = 0
        
        # Primary stat
        primary_stat = stat_chart[role][0]
        evs[primary_stat] = 252
        ev_total += 252
        
        # Secondary stat
        secondary_stat = stat_chart[role][1]
        if secondary_stat == 'hp' and pokemon_set.level and pokemon_set.level < 20:
            secondary_stat = 'spd'
        evs[secondary_stat] = 252
        ev_total += 252
        
        # HP optimization
        evs = self._optimize_hp_evs(pokemon_set, evs, ev_total, has_move, stats)
        
        # Special cases for specific Pokemon
        evs = self._apply_special_pokemon_evs(pokemon_set, evs, stats)
        
        # Distribute remaining EVs
        evs = self._distribute_remaining_evs(pokemon_set, evs, move_count, stats)
        
        return evs
    
    def _optimize_hp_evs(self, pokemon_set, evs, ev_total, has_move, stats):
        """Optimize HP EVs based on various factors."""
        # Stealth Rock weaknesses and resistances
        sr_weaknesses = ['Fire', 'Flying', 'Bug', 'Ice']
        sr_resistances = ['Ground', 'Steel', 'Fighting']
        
        try:
            species = self.localdex.get_pokemon(pokemon_set.species)
            sr_weak = 0
            
            if pokemon_set.ability not in ['Magic Guard', 'Mountaineer']:
                for pokemon_type in species.types:
                    if pokemon_type in sr_weaknesses:
                        sr_weak += 1
                    elif pokemon_type in sr_resistances:
                        sr_weak -= 1
            
            # Determine HP divisibility requirements
            hp_divisibility = 0
            hp_should_be_divisible = False
            hp = evs.get('hp', 0)
            
            # Check for Leftovers + Substitute
            if (pokemon_set.item in ['Leftovers', 'Black Sludge'] and 
                has_move.get('substitute')):
                hp_divisibility = 4
            
            # Check for Berry + Belly Drum
            elif (has_move.get('bellydrum') and 
                  pokemon_set.item and pokemon_set.item.endswith('Berry')):
                hp_divisibility = 2
                hp_should_be_divisible = True
            
            # Check for Berry + Substitute
            elif (has_move.get('substitute') and 
                  pokemon_set.item and pokemon_set.item.endswith('Berry')):
                hp_divisibility = 4
                hp_should_be_divisible = True
            
            # Check for Stealth Rock weakness or Belly Drum
            elif sr_weak >= 2 or has_move.get('bellydrum'):
                hp_divisibility = 2
            
            # Check for Stealth Rock weakness or Substitute
            elif sr_weak >= 1 or has_move.get('substitute') or has_move.get('transform'):
                hp_divisibility = 4
            
            # Default for other cases
            elif pokemon_set.ability != 'Magic Guard':
                hp_divisibility = 8
            
            # Optimize HP EVs based on divisibility
            if hp_divisibility:
                current_hp = self.get_stat('hp', pokemon_set, hp, 1.0)
                
                # Add EVs until we reach the right divisibility
                while (hp < 252 and ev_total < 508 and 
                       (current_hp % hp_divisibility == 0) != hp_should_be_divisible):
                    hp += 4
                    current_hp = self.get_stat('hp', pokemon_set, hp, 1.0)
                    ev_total += 4
                
                # Remove EVs if we overshot
                while (hp > 0 and 
                       (current_hp % hp_divisibility == 0) != hp_should_be_divisible):
                    hp -= 4
                    current_hp = self.get_stat('hp', pokemon_set, hp, 1.0)
                    ev_total -= 4
                
                # Remove redundant EVs
                while (hp > 0 and 
                       current_hp == self.get_stat('hp', pokemon_set, hp - 4, 1.0)):
                    hp -= 4
                    ev_total -= 4
                
                if hp > 0 or evs.get('hp'):
                    evs['hp'] = hp
            
        except:
            pass
        
        return evs
    
    def _apply_special_pokemon_evs(self, pokemon_set, evs, stats):
        """Apply special EV requirements for specific Pokemon."""
        try:
            species = self.localdex.get_pokemon(pokemon_set.species)
            species_id = species.name.lower()
            
            # Special cases for specific Pokemon
            if species_id == 'tentacruel':
                evs = self._ensure_min_evs(evs, 'spe', 16)
            elif species_id == 'skarmory':
                evs = self._ensure_min_evs(evs, 'spe', 24)
            elif species_id == 'jirachi':
                evs = self._ensure_min_evs(evs, 'spe', 32)
            elif species_id == 'celebi':
                evs = self._ensure_min_evs(evs, 'spe', 36)
            elif species_id == 'volcarona':
                evs = self._ensure_min_evs(evs, 'spe', 52)
            elif species_id == 'gliscor':
                evs = self._ensure_min_evs(evs, 'spe', 72)
            elif species_id == 'dragonite' and evs.get('hp'):
                evs = self._ensure_max_evs(evs, 'spe', 220)
                
        except:
            pass
        
        return evs
    
    def _distribute_remaining_evs(self, pokemon_set, evs, move_count, stats):
        """Distribute any remaining EVs."""
        ev_total = sum(evs.values())
        
        if ev_total < 508:
            remaining = 508 - ev_total
            if remaining > 252:
                remaining = 252
            
            # Determine secondary stat to invest in
            secondary_stat = None
            
            if not evs.get('atk') and move_count.get('PhysicalAttack', 0) >= 1:
                secondary_stat = 'atk'
            elif not evs.get('spa') and move_count.get('SpecialAttack', 0) >= 1:
                secondary_stat = 'spa'
            elif stats.hp == 1 and not evs.get('def'):
                secondary_stat = 'def'
            elif stats.defense == stats.special_defense and not evs.get('spd'):
                secondary_stat = 'spd'
            elif not evs.get('spd'):
                secondary_stat = 'spd'
            elif not evs.get('def'):
                secondary_stat = 'def'
            
            if secondary_stat:
                ev = remaining
                stat_value = self.get_stat(secondary_stat, pokemon_set, ev)
                
                # Reduce EVs until we get a different stat value
                while ev > 0 and stat_value == self.get_stat(secondary_stat, pokemon_set, ev - 4):
                    ev -= 4
                
                if ev > 0:
                    evs[secondary_stat] = ev
                    remaining -= ev
            
            # Distribute any remaining EVs to speed
            if remaining > 0 and not evs.get('spe'):
                ev = remaining
                stat_value = self.get_stat('spe', pokemon_set, ev)
                
                while ev > 0 and stat_value == self.get_stat('spe', pokemon_set, ev - 4):
                    ev -= 4
                
                if ev > 0:
                    evs['spe'] = ev
        
        return evs
    
    def _ensure_min_evs(self, evs, stat, min_evs):
        """Ensure a stat has at least the minimum EVs."""
        if not evs.get(stat):
            evs[stat] = 0
        
        diff = min_evs - evs[stat]
        if diff <= 0:
            return evs
        
        ev_total = sum(evs.values())
        
        if ev_total <= 504:
            change = min(508 - ev_total, diff)
            ev_total += change
            evs[stat] += change
            diff -= change
        
        if diff <= 0:
            return evs
        
        # Try to take EVs from other stats
        ev_priority = {'def': 1, 'spd': 1, 'hp': 1, 'atk': 1, 'spa': 1, 'spe': 1}
        
        for prio_stat in ev_priority:
            if prio_stat == stat:
                continue
            if evs.get(prio_stat, 0) > 128:
                evs[prio_stat] -= diff
                evs[stat] += diff
                break
        
        return evs
    
    def _ensure_max_evs(self, evs, stat, max_evs):
        """Ensure a stat has at most the maximum EVs."""
        if not evs.get(stat):
            evs[stat] = 0
        
        diff = evs[stat] - max_evs
        if diff <= 0:
            return evs
        
        evs[stat] -= diff
        return evs
    
    def _determine_minus_stat(self, has_move, move_count, stats, evs, plus_stat):
        """Determine which stat should be reduced by nature."""
        if has_move.get('gyroball') or has_move.get('trickroom'):
            return 'spe'
        elif not move_count.get('PhysicalAttack'):
            return 'atk'
        elif move_count.get('SpecialAttack', 0) < 1 and not evs.get('spa'):
            if move_count.get('SpecialAttack', 0) < move_count.get('PhysicalAttack', 0):
                return 'spa'
            elif not evs.get('atk'):
                return 'atk'
        elif move_count.get('PhysicalAttack', 0) < 1 and not evs.get('atk'):
            return 'atk'
        elif stats.defense > stats.speed and stats.special_defense > stats.speed and not evs.get('spe'):
            return 'spe'
        elif stats.defense > stats.special_defense:
            return 'spd'
        else:
            return 'def'
    
    def get_stat(self, stat: str, pokemon_set: PokemonSet, ev_override: Optional[int] = None, nature_override: Optional[float] = None) -> int:
        """
        Calculate a Pokemon's stat value.
        
        Args:
            stat: The stat to calculate
            pokemon_set: The Pokemon set
            ev_override: Override EV value
            nature_override: Override nature modifier
            
        Returns:
            The calculated stat value
        """
        try:
            species = self.localdex.get_pokemon(pokemon_set.species)
        except:
            return 0
        
        level = pokemon_set.level or 100
        
        # Map stat names to base_stats attributes
        stat_mapping = {
            'hp': 'hp',
            'atk': 'attack',
            'def': 'defense',
            'spa': 'special_attack',
            'spd': 'special_defense',
            'spe': 'speed'
        }
        
        base_stat_name = stat_mapping.get(stat, stat)
        base_stat = getattr(species.base_stats, base_stat_name, 0)
        
        # Get IV
        iv = pokemon_set.ivs.get(stat, 31)
        
        # Get EV
        ev = pokemon_set.evs.get(stat, 0)
        if ev_override is not None:
            ev = ev_override
        
        # Calculate stat using StatCalculator
        if stat == 'hp':
            return self.stat_calculator.calculate_hp(base_stat, iv, ev, level)
        else:
            # Apply nature modifier
            nature_modifier = 1.0
            if nature_override:
                nature_modifier = nature_override
            elif pokemon_set.nature:
                nature_mod = NATURE_MODIFIERS.get(pokemon_set.nature, {})
                if nature_mod.get('plus') == base_stat_name:
                    nature_modifier = 1.1
                elif nature_mod.get('minus') == base_stat_name:
                    nature_modifier = 0.9
            
            return self.stat_calculator.calculate_other_stat(base_stat, iv, ev, level, nature_modifier)
    
    def _to_id(self, text: Optional[str]) -> str:
        """Convert text to ID format (lowercase, no spaces)."""
        if not text:
            return ""
        return text.lower().replace(' ', '').replace('-', '')


def battle_stat_optimizer(pokemon_set: PokemonSet, format_id: str, localdex) -> Optional[Dict[str, Any]]:
    """
    Optimize a Pokemon's EV spread and nature.
    
    This replicates the functionality from the TypeScript BattleStatOptimizer function.
    
    Args:
        pokemon_set: The Pokemon set to optimize
        format_id: The format ID
        localdex: LocalDex instance
        
    Returns:
        Optimized spread or None if no optimization is possible
    """
    if not pokemon_set.evs:
        return None
    
    # This is a placeholder - the full implementation would be quite complex
    # and would need to implement the full optimization logic from the TypeScript version
    
    return None
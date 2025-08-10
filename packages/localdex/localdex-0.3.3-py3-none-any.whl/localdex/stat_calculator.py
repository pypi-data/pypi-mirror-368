"""
Stat calculation functionality for LocalDex.

This module contains all the stat calculation functions for Pokemon,
including HP, Attack, Defense, Special Attack, Special Defense, and Speed calculations.
"""

import math
from typing import Dict, List, Tuple, Union

from .models import BaseStats


class StatCalculator:
    """
    A class containing all Pokemon stat calculation functions.
    
    This class provides methods to calculate Pokemon stats from base stats,
    IVs, EVs, and levels, as well as reverse calculations to determine
    required EVs for target stat values.
    """
    
    def __init__(self, localdex):
        """
        Initialize the StatCalculator with a LocalDex instance.
        
        Args:
            localdex: LocalDex instance for accessing Pokemon data
        """
        self.localdex = localdex
    
    def get_base_stats_from_species(self, species: str) -> BaseStats:
        """Get base stats from species name"""
        return self.localdex.get_pokemon(name_or_id=species).base_stats
    
    def get_hp_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100) -> int:
        """Calculate HP stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_hp(base_stats.hp, iv, ev, level)

    def get_attack_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """Calculate Attack stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_other_stat(base_stats.attack, iv, ev, level, nature_modifier)
    
    def get_defense_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """Calculate Defense stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_other_stat(base_stats.defense, iv, ev, level, nature_modifier)
    
    def get_special_attack_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """Calculate Special Attack stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_other_stat(base_stats.special_attack, iv, ev, level, nature_modifier)
    
    def get_special_defense_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """Calculate Special Defense stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_other_stat(base_stats.special_defense, iv, ev, level, nature_modifier)
    
    def get_speed_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """Calculate Speed stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_other_stat(base_stats.speed, iv, ev, level, nature_modifier)
    
    def get_substitute_health_from_species(self, species: str, iv: int, ev: int, level: int = 100) -> int:
        """Calculate substitute health for a species (1/4 of max HP)"""
        max_hp = self.get_hp_stat_from_species(species, iv, ev, level)
        return int(max_hp / 4)
    
    def calculate_hp(self, base: int, iv: int, ev: int, level: int = 100) -> int:
        """
        Calculate HP using the Pokemon HP formula.
        
        Args:
            base (int): Base HP stat
            iv (int): Individual Value (0-31)
            ev (int): Effort Value (0-252)
            level (int): Pokemon level (1-100)
        
        Returns:
            int: Calculated HP value
        """
        hp = math.floor(((2 * base + iv + math.floor(ev / 4)) * level) / 100) + level + 10
        return hp
        
    def calculate_other_stat(self, base: int, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate other stats (Attack, Defense, Sp. Attack, Sp. Defense, Speed) using the Pokemon stat formula.
        
        Args:
            base (int): Base stat value
            iv (int): Individual Value (0-31)
            ev (int): Effort Value (0-252)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Calculated stat value
        """
        stat = math.floor((math.floor(((2 * base + iv + math.floor(ev / 4)) * level) / 100) + 5) * nature_modifier)
        return stat

    def calculate_hp_ev(self, total_hp: int, base_hp: int, iv: int, level: int = 100) -> int:
        """
        Calculate HP EV from total HP stat using the reverse of the Pokemon HP formula.
        
        If the target HP is impossible to achieve with any EV value, returns the EV that
        produces the closest possible HP value. For impossibly high HP values, returns 252 EVs.
        For impossibly low HP values, returns 0 EVs.
        
        Args:
            total_hp (int): Total HP stat value
            base_hp (int): Base HP stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        if level <= 0:
            raise ValueError("Level must be greater than 0")
        
        # Calculate the minimum and maximum possible HP values
        min_hp = self.calculate_hp(base_hp, iv, 0, level)
        max_hp = self.calculate_hp(base_hp, iv, 252, level)
        
        # If target HP is impossible, return the closest boundary
        if total_hp <= min_hp:
            return 0  # Return 0 EVs for impossibly low HP
        elif total_hp >= max_hp:
            return 252  # Return 252 EVs for impossibly high HP
        
        # Find the EV that gives us the closest HP value
        best_ev = 0
        best_diff = float('inf')
        
        for test_ev in range(0, 253, 4):  # EVs are always multiples of 4
            test_hp = self.calculate_hp(base_hp, iv, test_ev, level)
            diff = abs(test_hp - total_hp)
            
            if diff < best_diff:
                best_diff = diff
                best_ev = test_ev
            elif diff == best_diff and test_ev < best_ev:
                # If we have the same difference, prefer the lower EV
                best_ev = test_ev
        
        return best_ev
    
    def calculate_other_stat_ev(self, total_stat: int, base_stat: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate EV for other stats (Attack, Defense, Sp. Attack, Sp. Defense, Speed) using the reverse of the Pokemon stat formula.
        
        If the target stat is impossible to achieve with any EV value, returns the EV that
        produces the closest possible stat value. For impossibly high stat values, returns 252 EVs.
        For impossibly low stat values, returns 0 EVs.
        
        Args:
            total_stat (int): Total stat value
            base_stat (int): Base stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        if level <= 0:
            raise ValueError("Level must be greater than 0")
        if nature_modifier <= 0:
            raise ValueError("Nature modifier must be greater than 0")
        
        # Calculate the minimum and maximum possible stat values
        min_stat = self.calculate_other_stat(base_stat, iv, 0, level, nature_modifier)
        max_stat = self.calculate_other_stat(base_stat, iv, 252, level, nature_modifier)
        
        # If target stat is impossible, return the closest boundary
        if total_stat <= min_stat:
            return 0  # Return 0 EVs for impossibly low stat
        elif total_stat >= max_stat:
            return 252  # Return 252 EVs for impossibly high stat
        
        # Find the EV that gives us the closest stat value
        best_ev = 0
        best_diff = float('inf')
        
        for test_ev in range(0, 253, 4):  # EVs are always multiples of 4
            test_stat = self.calculate_other_stat(base_stat, iv, test_ev, level, nature_modifier)
            diff = abs(test_stat - total_stat)
            
            if diff < best_diff:
                best_diff = diff
                best_ev = test_ev
            elif diff == best_diff and test_ev < best_ev:
                # If we have the same difference, prefer the lower EV
                best_ev = test_ev
        
        return best_ev
    
    def calculate_attack_ev(self, total_attack: int, base_attack: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Attack EV from total Attack stat.
        
        If the target Attack is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Attack value. For impossibly high Attack values, returns 252 EVs.
        For impossibly low Attack values, returns 0 EVs.
        
        Args:
            total_attack (int): Total Attack stat value
            base_attack (int): Base Attack stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        return self.calculate_other_stat_ev(total_attack, base_attack, iv, level, nature_modifier)
    
    def calculate_defense_ev(self, total_defense: int, base_defense: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Defense EV from total Defense stat.
        
        If the target Defense is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Defense value. For impossibly high Defense values, returns 252 EVs.
        For impossibly low Defense values, returns 0 EVs.
        
        Args:
            total_defense (int): Total Defense stat value
            base_defense (int): Base Defense stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        return self.calculate_other_stat_ev(total_defense, base_defense, iv, level, nature_modifier)
    
    def calculate_special_attack_ev(self, total_special_attack: int, base_special_attack: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Special Attack EV from total Special Attack stat.
        
        If the target Special Attack is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Special Attack value. For impossibly high Special Attack values, returns 252 EVs.
        For impossibly low Special Attack values, returns 0 EVs.
        
        Args:
            total_special_attack (int): Total Special Attack stat value
            base_special_attack (int): Base Special Attack stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        return self.calculate_other_stat_ev(total_special_attack, base_special_attack, iv, level, nature_modifier)
    
    def calculate_special_defense_ev(self, total_special_defense: int, base_special_defense: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Special Defense EV from total Special Defense stat.
        
        If the target Special Defense is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Special Defense value. For impossibly high Special Defense values, returns 252 EVs.
        For impossibly low Special Defense values, returns 0 EVs.
        
        Args:
            total_special_defense (int): Total Special Defense stat value
            base_special_defense (int): Base Special Defense stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        return self.calculate_other_stat_ev(total_special_defense, base_special_defense, iv, level, nature_modifier)
    
    def calculate_speed_ev(self, total_speed: int, base_speed: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Speed EV from total Speed stat.
        
        If the target Speed is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Speed value. For impossibly high Speed values, returns 252 EVs.
        For impossibly low Speed values, returns 0 EVs.
        
        Args:
            total_speed (int): Total Speed stat value
            base_speed (int): Base Speed stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        return self.calculate_other_stat_ev(total_speed, base_speed, iv, level, nature_modifier)

    def calculate_hp_ev_from_species(self, species: str, total_hp: int, iv: int, level: int = 100) -> int:
        """
        Calculate HP EV from total HP stat using species name.
        
        If the target HP is impossible to achieve with any EV value, returns the EV that
        produces the closest possible HP value. For impossibly high HP values, returns 252 EVs.
        For impossibly low HP values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_hp (int): Total HP stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_hp_ev(total_hp, base_stats.hp, iv, level)
    
    def calculate_attack_ev_from_species(self, species: str, total_attack: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Attack EV from total Attack stat using species name.
        
        If the target Attack is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Attack value. For impossibly high Attack values, returns 252 EVs.
        For impossibly low Attack values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_attack (int): Total Attack stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_attack_ev(total_attack, base_stats.attack, iv, level, nature_modifier)
    
    def calculate_defense_ev_from_species(self, species: str, total_defense: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Defense EV from total Defense stat using species name.
        
        If the target Defense is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Defense value. For impossibly high Defense values, returns 252 EVs.
        For impossibly low Defense values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_defense (int): Total Defense stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_defense_ev(total_defense, base_stats.defense, iv, level, nature_modifier)
    
    def calculate_special_attack_ev_from_species(self, species: str, total_special_attack: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Special Attack EV from total Special Attack stat using species name.
        
        If the target Special Attack is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Special Attack value. For impossibly high Special Attack values, returns 252 EVs.
        For impossibly low Special Attack values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_special_attack (int): Total Special Attack stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_special_attack_ev(total_special_attack, base_stats.special_attack, iv, level, nature_modifier)
    
    def calculate_special_defense_ev_from_species(self, species: str, total_special_defense: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Special Defense EV from total Special Defense stat using species name.
        
        If the target Special Defense is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Special Defense value. For impossibly high Special Defense values, returns 252 EVs.
        For impossibly low Special Defense values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_special_defense (int): Total Special Defense stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_special_defense_ev(total_special_defense, base_stats.special_defense, iv, level, nature_modifier)
    
    def calculate_speed_ev_from_species(self, species: str, total_speed: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Speed EV from total Speed stat using species name.
        
        If the target Speed is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Speed value. For impossibly high Speed values, returns 252 EVs.
        For impossibly low Speed values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_speed (int): Total Speed stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_speed_ev(total_speed, base_stats.speed, iv, level, nature_modifier)
    
    def calculate_all_evs_from_species(self, species: str, stats: Dict[str, int], ivs: Dict[str, int], level: int = 100, nature_modifier: float = 1.0) -> Dict[str, int]:
        """
        Calculate all EV values for a Pokemon using species name and target stats.
        
        If any target stat is impossible to achieve with any EV value, returns the EV that
        produces the closest possible stat value. For impossibly high stat values, returns 252 EVs.
        For impossibly low stat values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            stats (Dict[str, int]): Dictionary of target stat values with keys: 'hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed'
            ivs (Dict[str, int]): Dictionary of IV values with keys: 'hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed'
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            Dict[str, int]: Dictionary of required EV values for each stat - closest possible values if targets are impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        
        evs = {}
        
        # Calculate HP EV (no nature modifier)
        if 'hp' in stats:
            evs['hp'] = self.calculate_hp_ev(stats['hp'], base_stats.hp, ivs.get('hp', 31), level)
        
        # Calculate other stat EVs (with nature modifier)
        if 'attack' in stats:
            evs['attack'] = self.calculate_attack_ev(stats['attack'], base_stats.attack, ivs.get('attack', 31), level, nature_modifier)
        
        if 'defense' in stats:
            evs['defense'] = self.calculate_defense_ev(stats['defense'], base_stats.defense, ivs.get('defense', 31), level, nature_modifier)
        
        if 'special_attack' in stats:
            evs['special_attack'] = self.calculate_special_attack_ev(stats['special_attack'], base_stats.special_attack, ivs.get('special_attack', 31), level, nature_modifier)
        
        if 'special_defense' in stats:
            evs['special_defense'] = self.calculate_special_defense_ev(stats['special_defense'], base_stats.special_defense, ivs.get('special_defense', 31), level, nature_modifier)
        
        if 'speed' in stats:
            evs['speed'] = self.calculate_speed_ev(stats['speed'], base_stats.speed, ivs.get('speed', 31), level, nature_modifier)
        
        return evs

    def calculate_hp_ev_and_nature_combinations(self, total_hp: int, base_hp: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible EV and nature modifier combinations for HP.
        Note: HP is not affected by nature, so this returns only the EV value with nature_modifier=1.0.
        
        Args:
            total_hp (int): Total HP stat value
            base_hp (int): Base HP stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        # HP is not affected by nature, so there's only one combination
        ev = self.calculate_hp_ev(total_hp, base_hp, iv, level)
        return [(ev, 1.0)]
    
    def calculate_other_stat_ev_and_nature_combinations(self, total_stat: int, base_stat: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible EV and nature modifier combinations for other stats.
        
        Args:
            total_stat (int): Total stat value
            base_stat (int): Base stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        if level <= 0:
            raise ValueError("Level must be greater than 0")
        
        combinations = []
        
        # Try each nature modifier: hindering (0.9), neutral (1.0), beneficial (1.1)
        nature_modifiers = [0.9, 1.0, 1.1]
        
        for nature_modifier in nature_modifiers:
            try:
                ev = self.calculate_other_stat_ev(total_stat, base_stat, iv, level, nature_modifier)
                
                # Verify this combination actually produces the target stat (or closest possible)
                calculated_stat = self.calculate_other_stat(base_stat, iv, ev, level, nature_modifier)
                
                # Accept the combination if it produces the target stat or the closest possible value
                if calculated_stat == total_stat or abs(calculated_stat - total_stat) <= 1:
                    combinations.append((ev, nature_modifier))
                    
            except (ValueError, ZeroDivisionError):
                # Skip invalid combinations
                continue
        
        # Remove duplicates and sort by EV (ascending)
        unique_combinations = list(set(combinations))
        unique_combinations.sort(key=lambda x: x[0])
        
        return unique_combinations
    
    def calculate_attack_ev_and_nature_combinations(self, total_attack: int, base_attack: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Attack EV and nature modifier combinations.
        
        Args:
            total_attack (int): Total Attack stat value
            base_attack (int): Base Attack stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        return self.calculate_other_stat_ev_and_nature_combinations(total_attack, base_attack, iv, level)
    
    def calculate_defense_ev_and_nature_combinations(self, total_defense: int, base_defense: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Defense EV and nature modifier combinations.
        
        Args:
            total_defense (int): Total Defense stat value
            base_defense (int): Base Defense stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        return self.calculate_other_stat_ev_and_nature_combinations(total_defense, base_defense, iv, level)
    
    def calculate_special_attack_ev_and_nature_combinations(self, total_special_attack: int, base_special_attack: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Special Attack EV and nature modifier combinations.
        
        Args:
            total_special_attack (int): Total Special Attack stat value
            base_special_attack (int): Base Special Attack stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        return self.calculate_other_stat_ev_and_nature_combinations(total_special_attack, base_special_attack, iv, level)
    
    def calculate_special_defense_ev_and_nature_combinations(self, total_special_defense: int, base_special_defense: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Special Defense EV and nature modifier combinations.
        
        Args:
            total_special_defense (int): Total Special Defense stat value
            base_special_defense (int): Base Special Defense stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        return self.calculate_other_stat_ev_and_nature_combinations(total_special_defense, base_special_defense, iv, level)
    
    def calculate_speed_ev_and_nature_combinations(self, total_speed: int, base_speed: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Speed EV and nature modifier combinations.
        
        Args:
            total_speed (int): Total Speed stat value
            base_speed (int): Base Speed stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        return self.calculate_other_stat_ev_and_nature_combinations(total_speed, base_speed, iv, level)
    
    def calculate_hp_ev_and_nature_combinations_from_species(self, species: str, total_hp: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible HP EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_hp (int): Total HP stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_hp_ev_and_nature_combinations(total_hp, base_stats.hp, iv, level)
    
    def calculate_attack_ev_and_nature_combinations_from_species(self, species: str, total_attack: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Attack EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_attack (int): Total Attack stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_attack_ev_and_nature_combinations(total_attack, base_stats.attack, iv, level)
    
    def calculate_defense_ev_and_nature_combinations_from_species(self, species: str, total_defense: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Defense EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_defense (int): Total Defense stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_defense_ev_and_nature_combinations(total_defense, base_stats.defense, iv, level)
    
    def calculate_special_attack_ev_and_nature_combinations_from_species(self, species: str, total_special_attack: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Special Attack EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_special_attack (int): Total Special Attack stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_special_attack_ev_and_nature_combinations(total_special_attack, base_stats.special_attack, iv, level)
    
    def calculate_special_defense_ev_and_nature_combinations_from_species(self, species: str, total_special_defense: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Special Defense EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_special_defense (int): Total Special Defense stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_special_defense_ev_and_nature_combinations(total_special_defense, base_stats.special_defense, iv, level)
    
    def calculate_speed_ev_and_nature_combinations_from_species(self, species: str, total_speed: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Speed EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_speed (int): Total Speed stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_speed_ev_and_nature_combinations(total_speed, base_stats.speed, iv, level) 
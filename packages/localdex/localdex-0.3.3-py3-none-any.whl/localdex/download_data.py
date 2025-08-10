"""
Data downloader for LocalDex.

This script downloads Pokemon data from online sources and converts it
to the local JSON format used by LocalDex.
"""

import json
import os
import sys
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .exceptions import DataLoadError

# --- BEGIN BASE_FORM_SOURCE mapping (from list_dash_species.py) ---
BASE_FORM_SOURCE = {
    "aegislash": "aegislash-shield",
    "basculin": "basculin-red-striped",
    "basculegion": "basculegion-male",
    "darmanitan": "darmanitan-standard",
    "deoxys": "deoxys-speed",
    "dudunsparce": "dudunsparce-two-segment",
    "eiscue": "eiscue-ice",
    "enamorus": "enamorus-therian",
    "giratina": "giratina-origin",
    "gourgeist": "gourgeist-average",
    "indeedee": "indeedee-male",
    "keldeo": "keldeo-resolute",
    "landorus": "landorus-therian",
    "lycanroc": "lycanroc-midday",
    "maushold": "maushold-family-of-three",
    "meowstic": "meowstic-male",
    "meloetta": "meloetta-aria",
    "mimikyu": "mimikyu-disguised",
    "minior": "minior-red-meteor",
    "morpeko": "morpeko-full-belly",
    "nidoran": "nidoran-f",
    "oinkologne": "oinkologne-male",
    "oricorio": "oricorio-baile",
    "palafin": "palafin-zero",
    "pumpkaboo": "pumpkaboo-average",
    "shaymin": "shaymin-land",
    "squawkabilly": "squawkabilly-white-plumage",
    "tatsugiri": "tatsugiri-curly",
    "thundurus": "thundurus-therian",
    "toxtricity": "toxtricity-amped",
    "tornadus": "tornadus-therian",
    "urshifu": "urshifu-single-strike",
    "wishiwashi": "wishiwashi-solo",
    "wormadam": "wormadam-plant",
    "zygarde": "zygarde-10",
}
# --- END BASE_FORM_SOURCE mapping ---


class DataDownloader:
    """
    Downloads and processes Pokemon data from online sources.
    
    This class handles downloading data from PokeAPI and other sources,
    then converts it to the format expected by LocalDex.
    """
    
    def __init__(self, output_dir: str = "localdex/data", max_workers: int = 5):
        """
        Initialize the data downloader.
        
        Args:
            output_dir: Directory to save downloaded data
            max_workers: Maximum number of concurrent downloads
        """
        self.output_dir = Path(output_dir)
        self.base_url = "https://pokeapi.co/api/v2"
        self.session = requests.Session()
        
        # Create output directories
        self.pokemon_dir = self.output_dir / "pokemon"
        self.moves_dir = self.output_dir / "moves"
        self.abilities_dir = self.output_dir / "abilities"
        self.items_dir = self.output_dir / "items"
        
        for directory in [self.pokemon_dir, self.moves_dir, self.abilities_dir, self.items_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.max_workers = max_workers
        self._session_lock = threading.Lock()
    
    def _get_session(self) -> requests.Session:
        """Get a thread-safe session."""
        with self._session_lock:
            return self.session
    
    def download_pokemon_data(self, limit: Optional[int] = None) -> None:
        """
        Download Pokemon data.
        
        Args:
            limit: Maximum number of Pokemon to download (None for all)
        """
        print("Downloading Pokemon data...")
        
        # Get list of Pokemon
        url = f"{self.base_url}/pokemon"
        if limit:
            url += f"?limit={limit}"
        
        session = self._get_session()
        response = session.get(url)
        response.raise_for_status()
        
        pokemon_list = response.json()["results"]
        total = len(pokemon_list)
        
        print(f"Found {total} Pokemon to download")
        
        # Thread-safe counter for progress tracking
        completed_count = 0
        lock = threading.Lock()
        
        def download_and_save_pokemon(pokemon_info):
            nonlocal completed_count
            try:
                pokemon_id = pokemon_info["url"].split("/")[-2]
                pokemon_name = pokemon_info["name"]
                
                # Download detailed Pokemon data
                pokemon_data = self._download_pokemon_detail(pokemon_id)
                
                # Save to file
                output_file = self.pokemon_dir / f"{pokemon_name}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(pokemon_data, f, indent=2, ensure_ascii=False)
                
                # Update progress
                with lock:
                    completed_count += 1
                    print(f"Downloaded {pokemon_name} ({completed_count}/{total})")
                
                return pokemon_name
                
            except Exception as e:
                with lock:
                    completed_count += 1
                    print(f"Error downloading {pokemon_info['name']}: {e}")
                return None
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(download_and_save_pokemon, pokemon_info) for pokemon_info in pokemon_list]
            for future in as_completed(futures):
                future.result()  # Wait for completion and handle any exceptions

        # --- BEGIN: Add extra convenience mappings for base species ---
        # For each base in BASE_FORM_SOURCE, if a file named after the base does not exist,
        # copy the data from the mapped dash species file (if it exists). Avoid duplicates.
        for base, dash_species in BASE_FORM_SOURCE.items():
            base_file = self.pokemon_dir / f"{base}.json"
            dash_file = self.pokemon_dir / f"{dash_species}.json"
            if not base_file.exists() and dash_file.exists():
                # Read dash species data
                with open(dash_file, 'r', encoding='utf-8') as f:
                    dash_data = json.load(f)
                # Set the name to the base name for the new file
                dash_data["name"] = base
                # Write to base file
                with open(base_file, 'w', encoding='utf-8') as f:
                    json.dump(dash_data, f, indent=2, ensure_ascii=False)
                print(f"[Convenience] Created {base}.json from {dash_species}.json")
            elif base_file.exists():
                print(f"[Convenience] {base}.json already exists, skipping.")
            else:
                print(f"[Convenience] Could not create {base}.json (source {dash_species}.json missing)")
        # --- END: Add extra convenience mappings for base species ---
    
    def download_move_data(self, limit: Optional[int] = None) -> None:
        """
        Download move data.
        
        Args:
            limit: Maximum number of moves to download (None for all)
        """
        print("Downloading move data...")
        
        # Get list of moves
        url = f"{self.base_url}/move"
        if limit:
            url += f"?limit={limit}"
        
        session = self._get_session()
        response = session.get(url)
        response.raise_for_status()
        
        move_list = response.json()["results"]
        total = len(move_list)
        
        print(f"Found {total} moves to download")
        
        # Thread-safe counter for progress tracking
        completed_count = 0
        lock = threading.Lock()
        
        def download_and_save_move(move_info):
            nonlocal completed_count
            try:
                move_id = move_info["url"].split("/")[-2]
                move_name = move_info["name"]
                
                # Download detailed move data
                move_data = self._download_move_detail(move_id)
                
                # Save to file
                output_file = self.moves_dir / f"{move_name}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(move_data, f, indent=2, ensure_ascii=False)
                
                # Update progress
                with lock:
                    completed_count += 1
                    print(f"Downloaded {move_name} ({completed_count}/{total})")
                
                return move_name
                
            except Exception as e:
                with lock:
                    completed_count += 1
                    print(f"Error downloading {move_info['name']}: {e}")
                return None
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(download_and_save_move, move_info) for move_info in move_list]
            for future in as_completed(futures):
                future.result()  # Wait for completion and handle any exceptions
    
    def download_ability_data(self, limit: Optional[int] = None) -> None:
        """
        Download ability data.
        
        Args:
            limit: Maximum number of abilities to download (None for all)
        """
        print("Downloading ability data...")
        
        # Get list of abilities
        url = f"{self.base_url}/ability"
        if limit:
            url += f"?limit={limit}"
        
        session = self._get_session()
        response = session.get(url)
        response.raise_for_status()
        
        ability_list = response.json()["results"]
        total = len(ability_list)
        
        print(f"Found {total} abilities to download")
        
        # Thread-safe counter for progress tracking
        completed_count = 0
        lock = threading.Lock()
        
        def download_and_save_ability(ability_info):
            nonlocal completed_count
            try:
                ability_id = ability_info["url"].split("/")[-2]
                ability_name = ability_info["name"]
                
                # Download detailed ability data
                ability_data = self._download_ability_detail(ability_id)
                
                # Save to file
                output_file = self.abilities_dir / f"{ability_name}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(ability_data, f, indent=2, ensure_ascii=False)
                
                # Update progress
                with lock:
                    completed_count += 1
                    print(f"Downloaded {ability_name} ({completed_count}/{total})")
                
                return ability_name
                
            except Exception as e:
                with lock:
                    completed_count += 1
                    print(f"Error downloading {ability_info['name']}: {e}")
                return None
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(download_and_save_ability, ability_info) for ability_info in ability_list]
            for future in as_completed(futures):
                future.result()  # Wait for completion and handle any exceptions
    
    def download_item_data(self, limit: Optional[int] = None) -> None:
        """
        Download item data.
        
        Args:
            limit: Maximum number of items to download (None for all)
        """
        print("Downloading item data...")
        
        # Get list of items
        url = f"{self.base_url}/item"
        if limit:
            url += f"?limit={limit}"
        
        session = self._get_session()
        response = session.get(url)
        response.raise_for_status()
        
        item_list = response.json()["results"]
        total = len(item_list)
        
        print(f"Found {total} items to download")
        
        # Thread-safe counter for progress tracking
        completed_count = 0
        lock = threading.Lock()
        
        def download_and_save_item(item_info):
            nonlocal completed_count
            try:
                item_id = item_info["url"].split("/")[-2]
                item_name = item_info["name"]
                
                # Download detailed item data
                item_data = self._download_item_detail(item_id)
                
                # Save to file
                output_file = self.items_dir / f"{item_name}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(item_data, f, indent=2, ensure_ascii=False)
                
                # Update progress
                with lock:
                    completed_count += 1
                    print(f"Downloaded {item_name} ({completed_count}/{total})")
                
                return item_name
                
            except Exception as e:
                with lock:
                    completed_count += 1
                    print(f"Error downloading {item_info['name']}: {e}")
                return None
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(download_and_save_item, item_info) for item_info in item_list]
            for future in as_completed(futures):
                future.result()  # Wait for completion and handle any exceptions
    
    def _download_pokemon_detail(self, pokemon_id: str) -> Dict[str, Any]:
        """Download detailed Pokemon data."""
        url = f"{self.base_url}/pokemon/{pokemon_id}"
        session = self._get_session()
        response = session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert to LocalDex format
        pokemon_data = {
            "id": data["id"],
            "name": data["name"],
            "types": [t["type"]["name"] for t in data["types"]],
            "baseStats": {
                "hp": data["stats"][0]["base_stat"],
                "attack": data["stats"][1]["base_stat"],
                "defense": data["stats"][2]["base_stat"],
                "special_attack": data["stats"][3]["base_stat"],
                "special_defense": data["stats"][4]["base_stat"],
                "speed": data["stats"][5]["base_stat"]
            },
            "height": data["height"] / 10.0,  # Convert to meters
            "weight": data["weight"] / 10.0,  # Convert to kg
            "abilities": {},
            "moves": [],
            "generation": self._get_generation_from_id(data["id"])
        }
        
        # Add abilities
        for i, ability in enumerate(data["abilities"]):
            slot = str(i) if not ability["is_hidden"] else "H"
            pokemon_data["abilities"][slot] = {
                "name": ability["ability"]["name"]
            }
        
        # Add moves (just names for now)
        pokemon_data["moves"] = [move["move"]["name"] for move in data["moves"]]
        
        return pokemon_data
    
    def _download_move_detail(self, move_id: str) -> Dict[str, Any]:
        """Download detailed move data."""
        url = f"{self.base_url}/move/{move_id}"
        session = self._get_session()
        response = session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert to LocalDex format
        move_data = {
            "name": data["name"],
            "type": data["type"]["name"],
            "category": data["damage_class"]["name"],
            "basePower": data["power"] or 0,
            "accuracy": data["accuracy"] or 100,
            "pp": data["pp"],
            "priority": data["priority"],
            "target": data["target"]["name"],
            "generation": data["generation"]["name"].split("-")[-1]
        }
        
        # Add descriptions
        for flavor_text in data["flavor_text_entries"]:
            if flavor_text["language"]["name"] == "en":
                move_data["description"] = flavor_text["flavor_text"].replace("\n", " ")
                break
        
        return move_data
    
    def _download_ability_detail(self, ability_id: str) -> Dict[str, Any]:
        """Download detailed ability data."""
        url = f"{self.base_url}/ability/{ability_id}"
        session = self._get_session()
        response = session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert to LocalDex format
        ability_data = {
            "name": data["name"],
            "generation": data["generation"]["name"].split("-")[-1]
        }
        
        # Add descriptions
        for effect_entry in data["effect_entries"]:
            if effect_entry["language"]["name"] == "en":
                ability_data["description"] = effect_entry["effect"].replace("\n", " ")
                ability_data["short_description"] = effect_entry["short_effect"]
                break
        
        return ability_data
    
    def _download_item_detail(self, item_id: str) -> Dict[str, Any]:
        """Download detailed item data."""
        url = f"{self.base_url}/item/{item_id}"
        session = self._get_session()
        response = session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert to LocalDex format
        item_data = {
            "name": data["name"]
        }
        
        # Add descriptions
        for flavor_text in data["flavor_text_entries"]:
            if flavor_text["language"]["name"] == "en":
                item_data["description"] = flavor_text["text"].replace("\n", " ")
                break
        
        return item_data
    
    def _get_generation_from_id(self, pokemon_id: int) -> int:
        """Get generation from Pokemon ID."""
        if pokemon_id <= 151:
            return 1
        elif pokemon_id <= 251:
            return 2
        elif pokemon_id <= 386:
            return 3
        elif pokemon_id <= 493:
            return 4
        elif pokemon_id <= 649:
            return 5
        elif pokemon_id <= 721:
            return 6
        elif pokemon_id <= 809:
            return 7
        elif pokemon_id <= 898:
            return 8
        else:
            return 9
    
    def download_all_data(self, pokemon_limit: Optional[int] = None, 
                         move_limit: Optional[int] = None,
                         ability_limit: Optional[int] = None,
                         item_limit: Optional[int] = None) -> None:
        """
        Download all data types.
        
        Args:
            pokemon_limit: Limit for Pokemon downloads (None for all)
            move_limit: Limit for move downloads (None for all)
            ability_limit: Limit for ability downloads (None for all)
            item_limit: Limit for item downloads (None for all)
        """
        print("Starting data download...")
        print("Note: When no limits are specified, all available data will be downloaded.")
        
        try:
            self.download_pokemon_data(pokemon_limit)
            self.download_move_data(move_limit)
            self.download_ability_data(ability_limit)
            self.download_item_data(item_limit)
            
            print("Data download completed successfully!")
            
        except Exception as e:
            print(f"Error during data download: {e}")
            raise DataLoadError(f"Failed to download data: {e}")


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Pokemon data for LocalDex")
    parser.add_argument("--output", default="localdex/data", help="Output directory")
    parser.add_argument("--max-workers", type=int, default=5, help="Maximum number of concurrent downloads (default: 5)")
    parser.add_argument("--pokemon-limit", type=int, help="Limit number of Pokemon to download (default: all)")
    parser.add_argument("--move-limit", type=int, help="Limit number of moves to download (default: all)")
    parser.add_argument("--ability-limit", type=int, help="Limit number of abilities to download (default: all)")
    parser.add_argument("--item-limit", type=int, help="Limit number of items to download (default: all)")
    parser.add_argument("--pokemon-only", action="store_true", help="Download only Pokemon data")
    parser.add_argument("--moves-only", action="store_true", help="Download only move data")
    parser.add_argument("--abilities-only", action="store_true", help="Download only ability data")
    parser.add_argument("--items-only", action="store_true", help="Download only item data")
    
    args = parser.parse_args()
    
    downloader = DataDownloader(args.output, max_workers=args.max_workers)
    
    try:
        if args.pokemon_only:
            downloader.download_pokemon_data(args.pokemon_limit)
        elif args.moves_only:
            downloader.download_move_data(args.move_limit)
        elif args.abilities_only:
            downloader.download_ability_data(args.ability_limit)
        elif args.items_only:
            downloader.download_item_data(args.item_limit)
        else:
            downloader.download_all_data(
                pokemon_limit=args.pokemon_limit or 99999,
                move_limit=args.move_limit or 99999,
                ability_limit=args.ability_limit or 99999,
                item_limit=args.item_limit or 99999
            )
        
        print(f"Data saved to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 
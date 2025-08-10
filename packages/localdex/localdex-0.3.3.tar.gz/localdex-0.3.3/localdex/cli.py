"""
Command-line interface for LocalDex.

This module provides a CLI for querying Pokemon data from the command line.
"""

import argparse
import json
import sys
from typing import List, Optional

from . import LocalDex
from .exceptions import LocalDexError


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LocalDex - Fast, offline Pokemon data access",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  localdex pokemon pikachu
  localdex pokemon 25
  localdex search --type Fire --generation 1
  localdex move thunderbolt
  localdex ability lightningrod
  localdex list-pokemon --generation 1
  localdex export --format json --output pokemon_data.json
  localdex demo
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Pokemon command
    pokemon_parser = subparsers.add_parser("pokemon", help="Get Pokemon information")
    pokemon_parser.add_argument("identifier", help="Pokemon name or ID")
    pokemon_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search Pokemon")
    search_parser.add_argument("--type", help="Pokemon type")
    search_parser.add_argument("--generation", type=int, help="Generation number (1-9)")
    search_parser.add_argument("--min-attack", type=int, help="Minimum attack stat")
    search_parser.add_argument("--max-attack", type=int, help="Maximum attack stat")
    search_parser.add_argument("--min-speed", type=int, help="Minimum speed stat")
    search_parser.add_argument("--max-speed", type=int, help="Maximum speed stat")
    search_parser.add_argument("--legendary", action="store_true", help="Legendary Pokemon only")
    search_parser.add_argument("--mythical", action="store_true", help="Mythical Pokemon only")
    search_parser.add_argument("--name-contains", help="Name contains text")
    search_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    search_parser.add_argument("--limit", type=int, help="Limit number of results")
    
    # Move command
    move_parser = subparsers.add_parser("move", help="Get move information")
    move_parser.add_argument("name", help="Move name")
    move_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    # Ability command
    ability_parser = subparsers.add_parser("ability", help="Get ability information")
    ability_parser.add_argument("name", help="Ability name")
    ability_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    # Item command
    item_parser = subparsers.add_parser("item", help="Get item information")
    item_parser.add_argument("name", help="Item name")
    item_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    # List commands
    list_pokemon_parser = subparsers.add_parser("list-pokemon", help="List Pokemon")
    list_pokemon_parser.add_argument("--generation", type=int, help="Filter by generation")
    list_pokemon_parser.add_argument("--type", help="Filter by type")
    list_pokemon_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    list_pokemon_parser.add_argument("--limit", type=int, help="Limit number of results")
    
    list_moves_parser = subparsers.add_parser("list-moves", help="List moves")
    list_moves_parser.add_argument("--type", help="Filter by type")
    list_moves_parser.add_argument("--category", help="Filter by category (Physical, Special, Status)")
    list_moves_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    list_moves_parser.add_argument("--limit", type=int, help="Limit number of results")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export data")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")
    export_parser.add_argument("--output", help="Output file path")
    export_parser.add_argument("--type", choices=["pokemon", "moves", "abilities", "items"], help="Data type to export")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show data statistics")
    stats_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run the LocalDex demo")
    demo_parser.add_argument("--quiet", action="store_true", help="Suppress output (for testing)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        dex = LocalDex()
        
        if args.command == "pokemon":
            return handle_pokemon_command(dex, args)
        elif args.command == "search":
            return handle_search_command(dex, args)
        elif args.command == "move":
            return handle_move_command(dex, args)
        elif args.command == "ability":
            return handle_ability_command(dex, args)
        elif args.command == "item":
            return handle_item_command(dex, args)
        elif args.command == "list-pokemon":
            return handle_list_pokemon_command(dex, args)
        elif args.command == "list-moves":
            return handle_list_moves_command(dex, args)
        elif args.command == "export":
            return handle_export_command(dex, args)
        elif args.command == "stats":
            return handle_stats_command(dex, args)
        elif args.command == "demo":
            return handle_demo_command(dex, args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except LocalDexError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def handle_pokemon_command(dex: LocalDex, args) -> int:
    """Handle the pokemon command."""
    try:
        # Try to parse as ID first
        try:
            pokemon_id = int(args.identifier)
            pokemon = dex.get_pokemon_by_id(pokemon_id)
        except ValueError:
            pokemon = dex.get_pokemon_by_name(args.identifier)
        
        if args.format == "json":
            print(json.dumps(pokemon_to_dict(pokemon), indent=2))
        else:
            print_pokemon_text(pokemon)
        
        return 0
        
    except Exception as e:
        print(f"Error getting Pokemon: {e}", file=sys.stderr)
        return 1


def handle_search_command(dex: LocalDex, args) -> int:
    """Handle the search command."""
    filters = {}
    
    if args.type:
        filters["type"] = args.type
    if args.generation:
        filters["generation"] = args.generation
    if args.min_attack:
        filters["min_attack"] = args.min_attack
    if args.max_attack:
        filters["max_attack"] = args.max_attack
    if args.min_speed:
        filters["min_speed"] = args.min_speed
    if args.max_speed:
        filters["max_speed"] = args.max_speed
    if args.legendary:
        filters["is_legendary"] = True
    if args.mythical:
        filters["is_mythical"] = True
    if args.name_contains:
        filters["name_contains"] = args.name_contains
    
    try:
        results = dex.search_pokemon(**filters)
        
        if args.limit:
            results = results[:args.limit]
        
        if args.format == "json":
            pokemon_list = [pokemon_to_dict(p) for p in results]
            print(json.dumps(pokemon_list, indent=2))
        else:
            print(f"Found {len(results)} Pokemon:")
            for pokemon in results:
                print(f"  {pokemon.name} (#{pokemon.id}) - {'/'.join(pokemon.types)}")
        
        return 0
        
    except Exception as e:
        print(f"Error searching Pokemon: {e}", file=sys.stderr)
        return 1


def handle_move_command(dex: LocalDex, args) -> int:
    """Handle the move command."""
    try:
        move = dex.get_move(args.name)
        
        if args.format == "json":
            print(json.dumps(move_to_dict(move), indent=2))
        else:
            print_move_text(move)
        
        return 0
        
    except Exception as e:
        print(f"Error getting move: {e}", file=sys.stderr)
        return 1


def handle_ability_command(dex: LocalDex, args) -> int:
    """Handle the ability command."""
    try:
        ability = dex.get_ability(args.name)
        
        if args.format == "json":
            print(json.dumps(ability_to_dict(ability), indent=2))
        else:
            print_ability_text(ability)
        
        return 0
        
    except Exception as e:
        print(f"Error getting ability: {e}", file=sys.stderr)
        return 1


def handle_item_command(dex: LocalDex, args) -> int:
    """Handle the item command."""
    try:
        item = dex.get_item(args.name)
        
        if args.format == "json":
            print(json.dumps(item_to_dict(item), indent=2))
        else:
            print_item_text(item)
        
        return 0
        
    except Exception as e:
        print(f"Error getting item: {e}", file=sys.stderr)
        return 1


def handle_list_pokemon_command(dex: LocalDex, args) -> int:
    """Handle the list-pokemon command."""
    try:
        filters = {}
        if args.generation:
            filters["generation"] = args.generation
        if args.type:
            filters["type"] = args.type
        
        if filters:
            pokemon_list = dex.search_pokemon(**filters)
        else:
            pokemon_list = dex.get_all_pokemon()
        
        if args.limit:
            pokemon_list = pokemon_list[:args.limit]
        
        if args.format == "json":
            pokemon_dicts = [pokemon_to_dict(p) for p in pokemon_list]
            print(json.dumps(pokemon_dicts, indent=2))
        else:
            print(f"Found {len(pokemon_list)} Pokemon:")
            for pokemon in pokemon_list:
                print(f"  {pokemon.name} (#{pokemon.id}) - {'/'.join(pokemon.types)}")
        
        return 0
        
    except Exception as e:
        print(f"Error listing Pokemon: {e}", file=sys.stderr)
        return 1


def handle_list_moves_command(dex: LocalDex, args) -> int:
    """Handle the list-moves command."""
    try:
        moves = dex.get_all_moves()
        
        # Apply filters
        if args.type:
            moves = [m for m in moves if m.type.lower() == args.type.lower()]
        if args.category:
            moves = [m for m in moves if m.category.lower() == args.category.lower()]
        
        if args.limit:
            moves = moves[:args.limit]
        
        if args.format == "json":
            move_dicts = [move_to_dict(m) for m in moves]
            print(json.dumps(move_dicts, indent=2))
        else:
            print(f"Found {len(moves)} moves:")
            for move in moves:
                print(f"  {move.name} ({move.type}) - {move.category}")
        
        return 0
        
    except Exception as e:
        print(f"Error listing moves: {e}", file=sys.stderr)
        return 1


def handle_export_command(dex: LocalDex, args) -> int:
    """Handle the export command."""
    try:
        if args.type == "pokemon":
            data = [pokemon_to_dict(p) for p in dex.get_all_pokemon()]
        elif args.type == "moves":
            data = [move_to_dict(m) for m in dex.get_all_moves()]
        elif args.type == "abilities":
            data = [ability_to_dict(a) for a in dex.get_all_abilities()]
        elif args.type == "items":
            data = [item_to_dict(i) for i in dex.get_all_items()]
        else:
            print("Please specify --type (pokemon, moves, abilities, or items)", file=sys.stderr)
            return 1
        
        if args.format == "json":
            output = json.dumps(data, indent=2)
        else:
            print("CSV export not yet implemented", file=sys.stderr)
            return 1
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Data exported to {args.output}")
        else:
            print(output)
        
        return 0
        
    except Exception as e:
        print(f"Error exporting data: {e}", file=sys.stderr)
        return 1


def handle_stats_command(dex: LocalDex, args) -> int:
    """Handle the stats command."""
    try:
        stats = dex.data_loader.get_data_stats()
        cache_stats = dex.get_cache_stats()
        
        if args.format == "json":
            all_stats = {
                "data": stats,
                "cache": cache_stats
            }
            print(json.dumps(all_stats, indent=2))
        else:
            print("Data Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            print("\nCache Statistics:")
            for key, value in cache_stats.items():
                print(f"  {key}: {value}")
        
        return 0
        
    except Exception as e:
        print(f"Error getting stats: {e}", file=sys.stderr)
        return 1


def handle_demo_command(dex: LocalDex, args) -> int:
    """Handle the demo command."""
    try:
        if not args.quiet:
            print("=== LocalDex Demo ===\n")
        
        # Get Pokemon by name
        pikachu = dex.get_pokemon("pikachu")
        if not args.quiet:
            print(f"{pikachu.name} - {pikachu.types}")
        
        # Get Pokemon by ID
        charizard = dex.get_pokemon_by_id(6)
        if not args.quiet:
            print(f"{charizard.name} - HP: {charizard.base_stats.hp}")
        
        # Get Pokemon stats
        bulbasaur = dex.get_pokemon("bulbasaur")
        if not args.quiet:
            print(f"{bulbasaur.name} - Attack: {bulbasaur.base_stats.attack}, Speed: {bulbasaur.base_stats.speed}")
        
        # Get moves
        thunderbolt = dex.get_move("thunderbolt")
        if not args.quiet:
            print(f"{thunderbolt.name} - Power: {thunderbolt.base_power}, Type: {thunderbolt.type}")
        
        # Get abilities (note: use dashes in names like "lightning-rod")
        lightning_rod = dex.get_ability("lightning-rod")
        if not args.quiet:
            print(f"{lightning_rod.name} - {lightning_rod.description}")
        
        # Search Pokemon by type (case-insensitive)
        fire_types = dex.search_pokemon(type="fire")
        if not args.quiet:
            print(f"Fire type Pokemon: {[p.name for p in fire_types[:5]]}")
        
        # Search Pokemon by stat
        fast_pokemon = dex.search_pokemon(min_speed=120)
        if not args.quiet:
            print(f"Very fast Pokemon: {[p.name for p in fast_pokemon[:5]]}")
        
        # Get all moves of a specific type (case-insensitive)
        all_moves = dex.get_all_moves()
        electric_moves = [m for m in all_moves if m.type.lower() == "electric"]
        if not args.quiet:
            print(f"Electric moves count: {len(electric_moves)}")
            print(f"First 5 Electric moves: {[m.name for m in electric_moves[:5]]}")
        
        if not args.quiet:
            print("\n=== Demo completed successfully! ===")
        
        return 0
        
    except Exception as e:
        print(f"Error running demo: {e}", file=sys.stderr)
        return 1


def print_pokemon_text(pokemon) -> None:
    """Print Pokemon information in text format."""
    print(f"Pokemon: {pokemon.name} (#{pokemon.id})")
    print(f"Types: {' / '.join(pokemon.types)}")
    print(f"Base Stats:")
    print(f"  HP: {pokemon.base_stats.hp}")
    print(f"  Attack: {pokemon.base_stats.attack}")
    print(f"  Defense: {pokemon.base_stats.defense}")
    print(f"  Special Attack: {pokemon.base_stats.special_attack}")
    print(f"  Special Defense: {pokemon.base_stats.special_defense}")
    print(f"  Speed: {pokemon.base_stats.speed}")
    print(f"  Total: {pokemon.base_stats.total}")
    
    if pokemon.height:
        print(f"Height: {pokemon.height}m")
    if pokemon.weight:
        print(f"Weight: {pokemon.weight}kg")
    if pokemon.generation:
        print(f"Generation: {pokemon.generation}")
    if pokemon.description:
        print(f"Description: {pokemon.description}")


def print_move_text(move) -> None:
    """Print move information in text format."""
    print(f"Move: {move.name}")
    print(f"Type: {move.type}")
    print(f"Category: {move.category}")
    print(f"Power: {move.base_power}")
    print(f"Accuracy: {move.accuracy}")
    print(f"PP: {move.pp}")
    print(f"Priority: {move.priority}")
    
    if move.description:
        print(f"Description: {move.description}")


def print_ability_text(ability) -> None:
    """Print ability information in text format."""
    print(f"Ability: {ability.name}")
    if ability.description:
        print(f"Description: {ability.description}")
    if ability.rating:
        print(f"Rating: {ability.rating}")


def print_item_text(item) -> None:
    """Print item information in text format."""
    print(f"Item: {item.name}")
    if item.description:
        print(f"Description: {item.description}")
    if item.generation:
        print(f"Generation: {item.generation}")


def pokemon_to_dict(pokemon) -> dict:
    """Convert Pokemon object to dictionary."""
    return {
        "id": pokemon.id,
        "name": pokemon.name,
        "types": pokemon.types,
        "base_stats": {
            "hp": pokemon.base_stats.hp,
            "attack": pokemon.base_stats.attack,
            "defense": pokemon.base_stats.defense,
            "special_attack": pokemon.base_stats.special_attack,
            "special_defense": pokemon.base_stats.special_defense,
            "speed": pokemon.base_stats.speed,
            "total": pokemon.base_stats.total
        },
        "height": pokemon.height,
        "weight": pokemon.weight,
        "generation": pokemon.generation,
        "description": pokemon.description,
        "is_legendary": pokemon.is_legendary,
        "is_mythical": pokemon.is_mythical
    }


def move_to_dict(move) -> dict:
    """Convert Move object to dictionary."""
    return {
        "name": move.name,
        "type": move.type,
        "category": move.category,
        "base_power": move.base_power,
        "accuracy": move.accuracy,
        "pp": move.pp,
        "priority": move.priority,
        "description": move.description
    }


def ability_to_dict(ability) -> dict:
    """Convert Ability object to dictionary."""
    return {
        "name": ability.name,
        "description": ability.description,
        "rating": ability.rating,
        "generation": ability.generation
    }


def item_to_dict(item) -> dict:
    """Convert Item object to dictionary."""
    return {
        "name": item.name,
        "description": item.description,
        "generation": item.generation
    }


if __name__ == "__main__":
    sys.exit(main()) 
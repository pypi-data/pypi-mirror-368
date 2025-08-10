# LocalDex

A local Pokemon data repository/Pokedex with fast offline access.

## Features

- Fast offline access to Pokemon data
- Comprehensive Pokemon information including stats, moves, abilities, and items
- Support for all Pokemon generations
- Easy-to-use Python API
- Command-line interface
- Extensible data loading system

## Installation

```bash
pip install localdex
```

For development installation:
```bash
pip install -e .
```

## Quick Start

```python
from localdex import LocalDex

# Initialize the Pokedex
dex = LocalDex()

# Get Pokemon by name
pikachu = dex.get_pokemon("Pikachu")
print(f"Pikachu's HP: {pikachu.base_stats.hp}")

# Get Pokemon by ID
charizard = dex.get_pokemon_by_id(6)
print(f"Charizard's type: {charizard.types}")

# Get move information
thunderbolt = dex.get_move("Thunderbolt")
print(f"Thunderbolt power: {thunderbolt.power}")
```

## Command Line Usage

```bash
# Get Pokemon information
localdex pokemon pikachu

# Get move information
localdex move thunderbolt

# Get ability information
localdex ability levitate

# Get item information
localdex item leftovers
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black localdex/
isort localdex/
```

### Type Checking

```bash
mypy localdex/
```

## License

MIT License - see LICENSE file for details. 
"""
Custom exceptions for LocalDex.

This module contains custom exception classes for handling various
error cases in the LocalDex library.
"""


class LocalDexError(Exception):
    """Base exception for LocalDex errors."""
    pass


class PokemonNotFoundError(LocalDexError):
    """Raised when a Pokemon is not found."""
    
    def __init__(self, identifier: str, message: str = None):
        self.identifier = identifier
        if message:
            super().__init__(message)
        else:
            super().__init__(f"Pokemon not found: {identifier}")


class MoveNotFoundError(LocalDexError):
    """Raised when a move is not found."""
    
    def __init__(self, name: str, message: str = None):
        self.name = name
        if message:
            super().__init__(message)
        else:
            super().__init__(f"Move not found: {name}")


class AbilityNotFoundError(LocalDexError):
    """Raised when an ability is not found."""
    
    def __init__(self, name: str, message: str = None):
        self.name = name
        if message:
            super().__init__(message)
        else:
            super().__init__(f"Ability not found: {name}")


class ItemNotFoundError(LocalDexError):
    """Raised when an item is not found."""
    
    def __init__(self, name: str, message: str = None):
        self.name = name
        if message:
            super().__init__(message)
        else:
            super().__init__(f"Item not found: {name}")


class DataLoadError(LocalDexError):
    """Raised when there's an error loading data files."""
    
    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        if file_path:
            message = f"{message} (file: {file_path})"
        super().__init__(message)


class DataParseError(LocalDexError):
    """Raised when there's an error parsing data."""
    
    def __init__(self, message: str, data_type: str = None):
        self.data_type = data_type
        if data_type:
            message = f"Error parsing {data_type}: {message}"
        super().__init__(message)


class ConfigurationError(LocalDexError):
    """Raised when there's a configuration error."""
    pass


class SearchError(LocalDexError):
    """Raised when there's an error during search operations."""
    pass


class ValidationError(LocalDexError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None):
        self.field = field
        if field:
            message = f"Validation error in field '{field}': {message}"
        super().__init__(message)


class InvalidDataError(LocalDexError):
    """Raised when data is invalid or corrupted."""
    
    def __init__(self, message: str):
        super().__init__(message) 
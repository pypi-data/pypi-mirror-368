""" Module to get any path or string in the form of the project root"""
from pathlib import Path


def get_project_root() -> Path:
    """Return the project root directory by searching for common project indicators."""
    # Common project root indicators
    project_indicators = [
        '.git',
        '.venv',
        'pyproject.toml',
        'setup.py',
        'requirements.txt',
        '.gitignore',
        'README.md',
        'Pipfile',
        'poetry.lock'
    ]
    current_path = Path(__file__).resolve()

    # Walk up the directory tree to find the project root
    for parent in current_path.parents:
        if any((parent / indicator).exists() for indicator in project_indicators):
            return parent

    # If no indicators found, use the directory containing this file
    return current_path.parent


def from_root(path) -> Path:
    """
    Convert a path to be relative to the project root.

    Args:
        path: A string or Path object representing a file path

    Returns:
        Path: The resolved path from the project root
    """
    project_root = get_project_root()

    # Convert input to Path object
    path = Path(path) if not isinstance(path, Path) else path

    # If path is absolute, return as-is
    if path.is_absolute():
        return path

    # Return path relative to project root
    return project_root.joinpath(path)

"""
Conftest.py - Robust Path Resolution for Documentation Tests

This file provides robust path resolution that works regardless of:
- Where pytest is run from (repo root, Trading_Bot, or tests directory)
- How the repo was cloned (nested directories, different paths)
- The operating system (Windows, Linux, macOS)

The path resolution finds the project root by looking for marker files/directories.
"""

import pytest
import sys
from pathlib import Path


def find_project_root(start_path: Path) -> Path:
    """
    Find the project root by traversing up from start_path.
    
    Looks for these markers to identify the project root:
    1. A directory containing both 'Trading_Bot' and 'Trading_Bot_Documentation'
    2. A directory named 'ZepixTradingBot-old-v2-main' containing 'Trading_Bot'
    
    Args:
        start_path: Starting path to search from
        
    Returns:
        Path to the project root (ZepixTradingBot-old-v2-main level)
    """
    current = start_path.resolve()
    
    # Traverse up to find the project root
    for _ in range(10):  # Limit traversal depth
        # Check if this is the project root (has Trading_Bot and Trading_Bot_Documentation)
        if (current / "Trading_Bot").is_dir() and (current / "Trading_Bot_Documentation").is_dir():
            return current
        
        # Check if we're inside Trading_Bot and need to go up
        if current.name == "Trading_Bot" and (current / "src").is_dir():
            parent = current.parent
            if (parent / "Trading_Bot_Documentation").is_dir():
                return parent
        
        # Move up one level
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent
    
    # Fallback: try to find by looking for ZepixTradingBot-old-v2-main in path
    for part in start_path.resolve().parts:
        if "ZepixTradingBot" in part or "Trading_Bot" in part:
            # Reconstruct path up to this point
            idx = start_path.resolve().parts.index(part)
            potential_root = Path(*start_path.resolve().parts[:idx+1])
            if (potential_root / "Trading_Bot").is_dir():
                return potential_root
    
    # Last resort: use the old calculation method
    # This assumes tests are in Trading_Bot/tests/documentation_tests/*/
    return start_path.parent.parent.parent.parent.parent


# Calculate paths once at module load time
_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = find_project_root(_THIS_FILE)
TRADING_BOT_ROOT = PROJECT_ROOT / "Trading_Bot"
SRC_ROOT = TRADING_BOT_ROOT / "src"
DOC_ROOT = PROJECT_ROOT / "Trading_Bot_Documentation" / "V5_BIBLE"

# Add Trading_Bot to sys.path for imports
if str(TRADING_BOT_ROOT) not in sys.path:
    sys.path.insert(0, str(TRADING_BOT_ROOT))


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Fixture providing the project root path."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def trading_bot_root() -> Path:
    """Fixture providing the Trading_Bot root path."""
    return TRADING_BOT_ROOT


@pytest.fixture(scope="session")
def src_root() -> Path:
    """Fixture providing the src directory path."""
    return SRC_ROOT


@pytest.fixture(scope="session")
def doc_root() -> Path:
    """Fixture providing the documentation root path."""
    return DOC_ROOT


# Verify paths exist at import time
def _verify_paths():
    """Verify that all critical paths exist."""
    errors = []
    
    if not PROJECT_ROOT.exists():
        errors.append(f"PROJECT_ROOT does not exist: {PROJECT_ROOT}")
    if not TRADING_BOT_ROOT.exists():
        errors.append(f"TRADING_BOT_ROOT does not exist: {TRADING_BOT_ROOT}")
    if not SRC_ROOT.exists():
        errors.append(f"SRC_ROOT does not exist: {SRC_ROOT}")
    
    if errors:
        print("WARNING: Path verification failed:")
        for error in errors:
            print(f"  - {error}")
        print(f"  Current file: {_THIS_FILE}")
        print(f"  Calculated PROJECT_ROOT: {PROJECT_ROOT}")


_verify_paths()

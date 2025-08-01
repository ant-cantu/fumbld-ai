"""
NFL Fantasy Projections Library

A Python library for calculating NFL player fantasy projections using official data sources.
Supports Yahoo Fantasy Sports API integration and multiple scoring systems.

Core Classes:
- NFLProjectionsLibrary: Main library class for projections
- ProjectionResult: Data class for projection results
- PlayerStats: Data class for player statistics

Quick Start:
    from nfl_fantasy_projections import NFLProjectionsLibrary
    
    # Initialize library
    lib = NFLProjectionsLibrary()
    
    # Get sample projection
    result = lib.get_sample_projection("Josh Allen", "QB")
    print(f"{result.player_name}: {result.projected_points:.1f} points")
    
    # Get Yahoo projection (requires OAuth setup)
    result = lib.get_yahoo_projection("Josh Allen", "QB")
"""

from .nfl_projections_library import (
    NFLProjectionsLibrary,
    PlayerProjection,
    PlayerStats,
    get_sample_projection,
    get_yahoo_projection,
    get_multiple_projections,
    export_to_csv
)

from .config import (
    SCORING_SYSTEMS,
    NFL_TEAMS,
    POSITION_RELIABILITY
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    'NFLProjectionsLibrary',
    'PlayerProjection', 
    'PlayerStats',
    'get_sample_projection',
    'get_yahoo_projection',
    'get_multiple_projections',
    'export_to_csv',
    'SCORING_SYSTEMS',
    'NFL_TEAMS',
    'POSITION_RELIABILITY'
]

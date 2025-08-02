#!/usr/bin/env python3
"""
Test script for get_projections.py
Demonstrates how to run the projections generator
"""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def test_projections():
    """Test the projections generator"""
    try:
        from get_projections import ProjectionsGenerator
        
        print("🏈 Testing NFL Projections Generator...")
        
        # Initialize generator
        generator = ProjectionsGenerator(scoring_system="ppr")
        
        print(f"✅ Generator initialized for season {generator.current_season}")
        print(f"📁 Data path: {generator.data_path}")
        print(f"💾 Output file: {generator.output_filepath}")
        
        # Test extracting player names
        players = generator.extract_all_player_names()
        total = sum(len(pos_players) for pos_players in players.values())
        print(f"📋 Found {total} total players across all positions")
        
        # Show sample players by position
        for position, player_set in players.items():
            sample_players = list(player_set)[:3]  # Show first 3
            print(f"   {position}: {len(player_set)} players (sample: {sample_players})")
        
        print("\n🚀 To generate full projections, run:")
        print("   python get_projections.py")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the correct directory with access to nfl_stats/")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_projections()

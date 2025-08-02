#!/usr/bin/env python3
"""
Verify that injury filtering is working correctly
"""

import pandas as pd
from pathlib import Path
import requests

# Get current NFL state
response = requests.get("https://api.sleeper.app/v1/state/nfl")
nfl_data = response.json()
current_week = nfl_data['week']
current_season = nfl_data['season']

print(f"Current NFL State: Season {current_season}, Week {current_week}")

# Check injury data
data_path = Path(__file__).parent / "nfl_stats" / "data"
injury_file = data_path / "df_injury_2024.csv"

if injury_file.exists():
    df_injury = pd.read_csv(injury_file)
    print(f"Total injury records in file: {len(df_injury)}")
    
    # Filter to current week
    current_injuries = df_injury[
        (df_injury.get('season', 0) == current_season) &
        (df_injury.get('week', 0) == current_week)
    ]
    
    print(f"Current week injury records: {len(current_injuries)}")
    
    if len(current_injuries) > 0:
        print("Sample current week injuries:")
        print(current_injuries[['full_name', 'position', 'report_status', 'week', 'season']].head())
    else:
        print("No injury data found for current NFL week - all players defaulting to 'Healthy'")
        
        # Show some sample injury data for reference
        print("\nSample injury data available:")
        print(df_injury[['full_name', 'position', 'report_status', 'week', 'season']].head())
        print(f"Available weeks: {sorted(df_injury['week'].unique())}")
        print(f"Available seasons: {sorted(df_injury['season'].unique())}")
else:
    print("No injury file found")

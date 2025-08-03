"""
NFL Fantasy Points Projections Library - CSV Data Only
Pure CSV-based fantasy projections with machine learning

This library provides NFL player fantasy projections using only CSV data
from the nfl_stats folder, with ML models that learn and improve over time.

Author: Your NFL Projections System
Version: 2.0.0 - CSV Only
"""

# Debug printing control
DEBUG_PRINTS = False  # Set to False to disable all print statements

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import time
import json
import pickle
import os, requests
from pathlib import Path

# -------------------------
# Get NFL State
# -------------------------
response = requests.get("https://api.sleeper.app/v1/state/nfl")

# print(response.json())
df = pd.DataFrame([response.json()])

week = df['week'].iloc[0]
season = df['season'].iloc[0]
season_type = df['season_type'].iloc[0]
prev_season = df['previous_season'].iloc[0]

# ML imports with graceful fallback
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    if DEBUG_PRINTS:
        print("⚠️  scikit-learn not installed. ML features disabled.")
        print("   To enable ML: pip install scikit-learn")


def debug_print(message: str):
    """Print debug messages only if DEBUG_PRINTS is True"""
    if DEBUG_PRINTS:
        print(message)


@dataclass
class PlayerProjection:
    """Data class representing a player's fantasy projection"""
    player_name: str
    position: str
    team: str
    projected_points: float
    confidence: float
    week: int
    season: int
    scoring_breakdown: Dict[str, float]
    data_source: str
    last_updated: str


@dataclass
class PlayerStats:
    """Data class representing a player's comprehensive statistics"""
    player_name: str
    position: str
    team: str
    games_played: int
    # Offensive stats
    passing_yards: float = 0.0
    passing_tds: float = 0.0
    interceptions: float = 0.0
    rushing_yards: float = 0.0
    rushing_tds: float = 0.0
    receiving_yards: float = 0.0
    receiving_tds: float = 0.0
    receptions: float = 0.0
    fumbles: float = 0.0
    two_point_conversions: float = 0.0
    # Defense stats
    def_sacks: float = 0.0
    def_interceptions: float = 0.0
    def_fumbles_recovered: float = 0.0
    def_tds: float = 0.0
    def_safeties: float = 0.0
    def_blocked_kicks: float = 0.0
    def_points_allowed: float = 0.0
    # Kicker stats
    fg_made: float = 0.0
    fg_attempts: float = 0.0
    fg_avg_distance: float = 0.0
    fg_long: float = 0.0
    xp_made: float = 0.0


class CSVProjectionsLibrary:
    """
    CSV-only NFL Fantasy Points Projections Library
    
    This library calculates fantasy football projections using only CSV data
    with machine learning models that learn and improve over time.
    """
    
    def __init__(self, scoring_system: str = "ppr", data_path: str = None):
        """
        Initialize the CSV projections library
        
        Args:
            scoring_system (str): Fantasy scoring system - "ppr", "half_ppr", "standard", or "superflex"
            data_path (str): Path to the nfl_stats directory (optional)
        """
        self.current_season = int(season)
        self.current_week = int(week)
        self.scoring_system = scoring_system
        
        # Set data path
        if data_path:
            self.data_path = Path(data_path)
        else:
            # Default to the data folder within nfl_stats directory
            current_dir = Path(__file__).parent
            self.data_path = current_dir / "data"
        
        debug_print(f"📊 CSV Data path: {self.data_path}")
        
        # Fantasy scoring systems
        self.scoring_systems = {
            "standard": {
                'passing_yards': 0.04,    # 1 point per 25 yards
                'passing_tds': 4,
                'interceptions': -2,
                'rushing_yards': 0.1,     # 1 point per 10 yards
                'rushing_tds': 6,
                'receiving_yards': 0.1,   # 1 point per 10 yards
                'receiving_tds': 6,
                'receptions': 0,          # No PPR
                'fumbles': -2,
                'two_point_conversions': 2,
                # Defense scoring
                'def_sacks': 1,
                'def_interceptions': 2,
                'def_fumbles_recovered': 2,
                'def_tds': 6,
                'def_safeties': 2,
                'def_blocked_kicks': 2,
                'def_points_allowed_0': 10,      # 0 points allowed
                'def_points_allowed_1_6': 7,    # 1-6 points allowed
                'def_points_allowed_7_13': 4,   # 7-13 points allowed
                'def_points_allowed_14_20': 1,  # 14-20 points allowed
                'def_points_allowed_21_27': 0,  # 21-27 points allowed
                'def_points_allowed_28_34': -1, # 28-34 points allowed
                'def_points_allowed_35_plus': -4, # 35+ points allowed
                # Kicker scoring
                'fg_made': 3,             # 3 points per field goal
                'fg_40_49': 1,           # Bonus for 40-49 yard FG
                'fg_50_plus': 2,         # Bonus for 50+ yard FG
                'xp_made': 1,            # 1 point per extra point
                'fg_missed': -1          # Penalty for missed FG
            },
            "ppr": {
                'passing_yards': 0.04,
                'passing_tds': 4,
                'interceptions': -2,
                'rushing_yards': 0.1,
                'rushing_tds': 6,
                'receiving_yards': 0.1,
                'receiving_tds': 6,
                'receptions': 1,          # Full PPR
                'fumbles': -2,
                'two_point_conversions': 2,
                # Defense scoring (same as standard)
                'def_sacks': 1,
                'def_interceptions': 2,
                'def_fumbles_recovered': 2,
                'def_tds': 6,
                'def_safeties': 2,
                'def_blocked_kicks': 2,
                'def_points_allowed_0': 10,
                'def_points_allowed_1_6': 7,
                'def_points_allowed_7_13': 4,
                'def_points_allowed_14_20': 1,
                'def_points_allowed_21_27': 0,
                'def_points_allowed_28_34': -1,
                'def_points_allowed_35_plus': -4,
                # Kicker scoring (same as standard)
                'fg_made': 3,
                'fg_40_49': 1,
                'fg_50_plus': 2,
                'xp_made': 1,
                'fg_missed': -1
            },
            "half_ppr": {
                'passing_yards': 0.04,
                'passing_tds': 4,
                'interceptions': -2,
                'rushing_yards': 0.1,
                'rushing_tds': 6,
                'receiving_yards': 0.1,
                'receiving_tds': 6,
                'receptions': 0.5,        # Half PPR
                'fumbles': -2,
                'two_point_conversions': 2,
                # Defense scoring (same as standard)
                'def_sacks': 1,
                'def_interceptions': 2,
                'def_fumbles_recovered': 2,
                'def_tds': 6,
                'def_safeties': 2,
                'def_blocked_kicks': 2,
                'def_points_allowed_0': 10,
                'def_points_allowed_1_6': 7,
                'def_points_allowed_7_13': 4,
                'def_points_allowed_14_20': 1,
                'def_points_allowed_21_27': 0,
                'def_points_allowed_28_34': -1,
                'def_points_allowed_35_plus': -4,
                # Kicker scoring (same as standard)
                'fg_made': 3,
                'fg_40_49': 1,
                'fg_50_plus': 2,
                'xp_made': 1,
                'fg_missed': -1
            },
            "superflex": {
                'passing_yards': 0.04,
                'passing_tds': 6,        # Superflex often has higher QB scoring
                'interceptions': -2,
                'rushing_yards': 0.1,
                'rushing_tds': 6,
                'receiving_yards': 0.1,
                'receiving_tds': 6,
                'receptions': 1,          # Usually PPR in superflex
                'fumbles': -2,
                'two_point_conversions': 2,
                # Defense scoring (same as standard)
                'def_sacks': 1,
                'def_interceptions': 2,
                'def_fumbles_recovered': 2,
                'def_tds': 6,
                'def_safeties': 2,
                'def_blocked_kicks': 2,
                'def_points_allowed_0': 10,
                'def_points_allowed_1_6': 7,
                'def_points_allowed_7_13': 4,
                'def_points_allowed_14_20': 1,
                'def_points_allowed_21_27': 0,
                'def_points_allowed_28_34': -1,
                'def_points_allowed_35_plus': -4,
                # Kicker scoring (same as standard)
                'fg_made': 3,
                'fg_40_49': 1,
                'fg_50_plus': 2,
                'xp_made': 1,
                'fg_missed': -1
            }
        }
        
        # Initialize ML models
        self.ml_models = {}
        self.ml_scalers = {}
        self.model_cache_path = self.data_path / "ml_models"
        self.model_cache_path.mkdir(exist_ok=True)
        
        # Load existing models if available
        self._load_ml_models()
    
    def _calculate_nfl_week(self) -> int:
        """Calculate current NFL week based on the date"""
        # NFL season typically starts first Thursday after Labor Day
        # This is a simplified calculation - you might want to make it more precise
        current_date = datetime.now()
        
        # Approximate NFL season start (usually early September)
        season_start = datetime(current_date.year, 9, 1)
        
        # If we're before the season, return week 1
        if current_date < season_start:
            return 1
        
        # Calculate weeks since season start
        weeks_since_start = (current_date - season_start).days // 7
        
        # NFL regular season is weeks 1-18, then playoffs
        if weeks_since_start <= 18:
            return max(1, weeks_since_start + 1)
        else:
            return 18  # Cap at regular season end
    
    def _load_csv_data(self) -> Dict[str, pd.DataFrame]:
        """Load all CSV files from the nfl_stats directory"""
        data = {}
        
        try:
            # Load weekly player stats from all available years
            weekly_files = list(self.data_path.glob("df_weekly_*.csv"))
            if weekly_files:
                weekly_dfs = []
                for file in weekly_files:
                    df = pd.read_csv(file)
                    # Extract year from filename (e.g., df_weekly_2024.csv -> 2024)
                    year = file.stem.split('_')[-1]
                    df['data_year'] = int(year) if year.isdigit() else self.current_season
                    weekly_dfs.append(df)
                
                data['weekly'] = pd.concat(weekly_dfs, ignore_index=True)
                debug_print(f"📈 Loaded weekly stats from {len(weekly_files)} files: {len(data['weekly'])} total records")
            
            # Load defense stats from all available years
            dst_files = list(self.data_path.glob("dst_stats_*.csv"))
            if dst_files:
                dst_dfs = []
                for file in dst_files:
                    df = pd.read_csv(file)
                    year = file.stem.split('_')[-1]
                    df['data_year'] = int(year) if year.isdigit() else self.current_season
                    dst_dfs.append(df)
                
                data['defense'] = pd.concat(dst_dfs, ignore_index=True)
                debug_print(f"🛡️ Loaded defense stats from {len(dst_files)} files: {len(data['defense'])} total records")
            
            # Load kicker stats from all available years
            kicker_files = list(self.data_path.glob("kicker_stats_*.csv"))
            if kicker_files:
                kicker_dfs = []
                for file in kicker_files:
                    df = pd.read_csv(file)
                    year = file.stem.split('_')[-1]
                    df['data_year'] = int(year) if year.isdigit() else self.current_season
                    kicker_dfs.append(df)
                
                data['kickers'] = pd.concat(kicker_dfs, ignore_index=True)
                debug_print(f"🦵 Loaded kicker stats from {len(kicker_files)} files: {len(data['kickers'])} total records")
            
            # Load injury data from all available years
            injury_files = list(self.data_path.glob("df_injury_*.csv"))
            if injury_files:
                injury_dfs = []
                for file in injury_files:
                    df = pd.read_csv(file)
                    year = file.stem.split('_')[-1]
                    # Use 'season' column if it exists, otherwise add data_year from filename
                    if 'season' in df.columns:
                        df['data_year'] = df['season']
                    else:
                        df['data_year'] = int(year) if year.isdigit() else self.current_season
                    injury_dfs.append(df)
                
                data['injuries'] = pd.concat(injury_dfs, ignore_index=True)
                debug_print(f"🏥 Loaded injury data from {len(injury_files)} files: {len(data['injuries'])} total records")
        
        except Exception as e:
            debug_print(f"❌ Error loading CSV data: {e}")
            
        return data
    
    def _calculate_fantasy_points(self, stats: Dict[str, float], position: str) -> Tuple[float, Dict[str, float]]:
        """
        Calculate fantasy points from stats using the selected scoring system
        
        Args:
            stats (Dict): Player statistics
            position (str): Player position
            
        Returns:
            Tuple[float, Dict]: Total points and breakdown by category
        """
        scoring = self.scoring_systems[self.scoring_system]
        points = 0.0
        breakdown = {}
        
        if position in ['QB', 'RB', 'WR', 'TE', 'FLEX']:
            # Offensive player scoring
            for stat, value in stats.items():
                if stat in scoring and value > 0:
                    stat_points = value * scoring[stat]
                    points += stat_points
                    breakdown[stat] = stat_points
        
        elif position in ['DEF', 'DST', 'D/ST']:
            # Defense scoring
            for stat, value in stats.items():
                if stat.startswith('def_') and stat in scoring and value > 0:
                    # Skip def_tds as it appears to be points allowed in the CSV data
                    if stat == 'def_tds':
                        continue
                    stat_points = value * scoring[stat]
                    points += stat_points
                    breakdown[stat] = stat_points
            
            # Points allowed scoring (special case) - use def_points_allowed if available
            if 'def_points_allowed' in stats:
                points_allowed = stats['def_points_allowed']
                if points_allowed == 0:
                    breakdown['def_points_allowed'] = scoring['def_points_allowed_0']
                elif points_allowed <= 6:
                    breakdown['def_points_allowed'] = scoring['def_points_allowed_1_6']
                elif points_allowed <= 13:
                    breakdown['def_points_allowed'] = scoring['def_points_allowed_7_13']
                elif points_allowed <= 20:
                    breakdown['def_points_allowed'] = scoring['def_points_allowed_14_20']
                elif points_allowed <= 27:
                    breakdown['def_points_allowed'] = scoring['def_points_allowed_21_27']
                elif points_allowed <= 34:
                    breakdown['def_points_allowed'] = scoring['def_points_allowed_28_34']
                else:
                    breakdown['def_points_allowed'] = scoring['def_points_allowed_35_plus']
                
                points += breakdown['def_points_allowed']
        
        elif position == 'K':
            # Kicker scoring
            if 'fg_made' in stats:
                fg_points = stats['fg_made'] * scoring['fg_made']
                points += fg_points
                breakdown['fg_made'] = fg_points
                
                # Distance bonuses
                if 'fg_avg_distance' in stats and stats['fg_made'] > 0:
                    avg_dist = stats['fg_avg_distance']
                    if avg_dist >= 50:
                        bonus = stats['fg_made'] * scoring['fg_50_plus']
                        points += bonus
                        breakdown['fg_50_plus'] = bonus
                    elif avg_dist >= 40:
                        bonus = stats['fg_made'] * scoring['fg_40_49']
                        points += bonus
                        breakdown['fg_40_49'] = bonus
            
            if 'xp_made' in stats:
                xp_points = stats['xp_made'] * scoring['xp_made']
                points += xp_points
                breakdown['xp_made'] = xp_points
            
            if 'fg_attempts' in stats and 'fg_made' in stats:
                missed = stats['fg_attempts'] - stats['fg_made']
                if missed > 0:
                    miss_penalty = missed * scoring['fg_missed']
                    points += miss_penalty
                    breakdown['fg_missed'] = miss_penalty
        
        return points, breakdown
    
    def _check_injury_status(self, player_name: str, data: Dict[str, pd.DataFrame]) -> bool:
        """
        Check if player is marked as 'out' in current week's injury report
        
        Args:
            player_name (str): Name of the player
            data (Dict): Loaded CSV data including injuries
            
        Returns:
            bool: True if player is out due to injury, False otherwise
        """
        if 'injuries' not in data:
            return False
        
        injury_df = data['injuries']
        
        # Filter to current season and week only
        current_injuries = injury_df[
            (injury_df['data_year'] == self.current_season) &
            (injury_df.get('week', 0) == self.current_week)
        ]
        
        debug_print(f"🔍 Checking injuries for season {self.current_season}, week {self.current_week}")
        debug_print(f"🔍 Found {len(current_injuries)} current week injuries")
        
        if current_injuries.empty:
            return False
        
        # Look for player in injury report (try both full_name and player_display_name columns)
        name_columns = ['full_name', 'player_display_name']
        player_injuries = pd.DataFrame()
        
        for col in name_columns:
            if col in current_injuries.columns:
                matches = current_injuries[
                    current_injuries[col].str.lower() == player_name.lower()
                ]
                debug_print(f"🔍 Checking {col} for {player_name}: {len(matches)} matches")
                if not matches.empty:
                    player_injuries = matches
                    debug_print(f"🔍 Found player in injury report: {matches.iloc[0][col]}")
                    break
        
        if player_injuries.empty:
            return False
        
        # Check if marked as 'out' (try both report_status and report_secondary_injury)
        status_columns = ['report_status', 'report_secondary_injury']
        
        for col in status_columns:
            if col in player_injuries.columns:
                debug_print(f"🔍 Checking {col}: {player_injuries[col].tolist()}")
                is_out = player_injuries[col].str.lower() == 'out'
                if is_out.any():
                    debug_print(f"🏥 {player_name} is OUT due to injury in week {self.current_week}")
                    return True
        
        return False

    def get_player_stats_from_csv(self, player_name: str, position: str = None) -> Optional[PlayerStats]:
        """
        Get player statistics from CSV data
        
        Args:
            player_name (str): Name of the player
            position (str): Position filter (optional)
            
        Returns:
            PlayerStats or None if player not found
        """
        data = self._load_csv_data()
        
        if not data:
            debug_print("❌ No CSV data available")
            return None
        
        # Search in weekly stats first
        if 'weekly' in data:
            df = data['weekly']
            
            # Filter by player name (case insensitive)
            player_df = df[df['player_display_name'].str.lower() == player_name.lower()]
            
            if position:
                player_df = player_df[player_df['position'] == position.upper()]
            
            if not player_df.empty:
                # Aggregate stats across all weeks
                agg_stats = {
                    'player_name': player_name,
                    'position': player_df['position'].iloc[0],
                    'team': 'Multiple' if player_df['season'].nunique() > 1 else 'N/A',
                    'games_played': len(player_df),
                    'passing_yards': player_df['passing_yards'].sum(),
                    'passing_tds': player_df['passing_tds'].sum(),
                    'interceptions': player_df['interceptions'].sum(),
                    'rushing_yards': player_df['rushing_yards'].sum(),
                    'rushing_tds': player_df['rushing_tds'].sum(),
                    'receiving_yards': player_df['receiving_yards'].sum(),
                    'receiving_tds': player_df['receiving_tds'].sum(),
                    'receptions': player_df['receptions'].sum(),
                    'fumbles': player_df['rushing_fumbles_lost'].sum() + player_df['receiving_fumbles_lost'].sum(),
                    'two_point_conversions': (player_df['passing_2pt_conversions'].sum() + 
                                            player_df['rushing_2pt_conversions'].sum() + 
                                            player_df['receiving_2pt_conversions'].sum())
                }
                
                return PlayerStats(**agg_stats)
        
        # Search in defense stats
        if 'defense' in data and (not position or position.upper() in ['DEF', 'DST', 'D/ST']):
            df = data['defense']
            
            # For defense, handle both team abbreviations and city names
            search_name = player_name.lower()
            
            # Remove "DEF", "DST", "D/ST" suffixes if present
            for suffix in [' def', ' dst', ' d/st']:
                if search_name.endswith(suffix):
                    search_name = search_name[:-len(suffix)].strip()
            
            # NFL city to team abbreviation mapping
            city_to_team = {
                'arizona': 'ARI', 'atlanta': 'ATL', 'baltimore': 'BAL', 'buffalo': 'BUF',
                'carolina': 'CAR', 'chicago': 'CHI', 'cincinnati': 'CIN', 'cleveland': 'CLE',
                'dallas': 'DAL', 'denver': 'DEN', 'detroit': 'DET', 'green bay': 'GB',
                'houston': 'HOU', 'indianapolis': 'IND', 'jacksonville': 'JAX', 'kansas city': 'KC',
                'las vegas': 'LV', 'los angeles chargers': 'LAC', 'los angeles rams': 'LA',
                'miami': 'MIA', 'minnesota': 'MIN', 'new england': 'NE', 'new orleans': 'NO',
                'new york giants': 'NYG', 'new york jets': 'NYJ', 'philadelphia': 'PHI',
                'pittsburgh': 'PIT', 'san francisco': 'SF', 'seattle': 'SEA', 'tampa bay': 'TB',
                'tennessee': 'TEN', 'washington': 'WAS'
            }
            
            # Try direct team abbreviation match first
            team_df = df[df['team'].str.lower() == search_name]
            
            # If no match, try city name lookup
            if team_df.empty and search_name in city_to_team:
                team_abbr = city_to_team[search_name]
                team_df = df[df['team'].str.upper() == team_abbr]
                debug_print(f"🏈 Mapped city '{search_name}' to team '{team_abbr}'")
            
            if not team_df.empty:
                team_name = team_df['team'].iloc[0].upper()
                agg_stats = {
                    'player_name': f"{team_name} DEF",
                    'position': 'DEF',
                    'team': team_name,
                    'games_played': len(team_df),
                    'def_sacks': team_df['sacks'].sum(),
                    'def_interceptions': team_df['interceptions'].sum(),
                    'def_fumbles_recovered': team_df['fumbles'].sum(),
                    'def_tds': team_df['def_tds'].sum(),  # Note: This appears to be points allowed in the data
                    'def_safeties': team_df['safeties'].sum(),
                    'def_blocked_kicks': team_df['blocked_kicks'].sum(),
                    'def_points_allowed': team_df['def_tds'].mean()  # Use as points allowed per game
                }
                
                return PlayerStats(**agg_stats)
        
        # Search in kicker stats
        if 'kickers' in data and (not position or position.upper() == 'K'):
            df = data['kickers']
            
            # Try exact name match first
            kicker_df = df[df['kicker'].str.lower() == player_name.lower()]
            
            # If no exact match, try partial match (e.g., "Justin Tucker" -> "J.Tucker")
            if kicker_df.empty:
                # Try matching last name
                last_name = player_name.split()[-1].lower() if ' ' in player_name else player_name.lower()
                kicker_df = df[df['kicker'].str.lower().str.contains(last_name, na=False)]
                
                # If multiple matches, try to find best match
                if len(kicker_df) > 1:
                    # Try to match first initial + last name
                    if ' ' in player_name:
                        first_initial = player_name.split()[0][0].lower()
                        best_match = kicker_df[kicker_df['kicker'].str.lower().str.startswith(first_initial)]
                        if not best_match.empty:
                            kicker_df = best_match
                        else:
                            kicker_df = kicker_df.iloc[:1]  # Take first match
            
            if not kicker_df.empty:
                actual_name = kicker_df['kicker'].iloc[0]
                debug_print(f"🦵 Found kicker: '{player_name}' -> '{actual_name}'")
                
                agg_stats = {
                    'player_name': actual_name,
                    'position': 'K',
                    'team': kicker_df['team'].iloc[-1] if not kicker_df['team'].empty else 'N/A',
                    'games_played': len(kicker_df),
                    'fg_made': kicker_df['fg_made'].sum(),
                    'fg_attempts': kicker_df['fg_attempts'].sum(),
                    'fg_avg_distance': kicker_df['fg_avg_dist'].mean(),
                    'fg_long': kicker_df['fg_long'].max(),
                    'xp_made': kicker_df['xp_made'].sum()
                }
                
                return PlayerStats(**agg_stats)
        
        debug_print(f"❌ Player not found: {player_name}")
        return None
    
    def _prepare_ml_features(self, stats: PlayerStats) -> np.array:
        """
        Prepare features for ML model training
        
        Args:
            stats (PlayerStats): Player statistics
            
        Returns:
            numpy array of features
        """
        position = stats.position.upper()
        
        if position in ['QB', 'RB', 'WR', 'TE']:
            # Offensive player features
            features = [
                stats.games_played,
                stats.passing_yards / max(stats.games_played, 1),  # Per game averages
                stats.passing_tds / max(stats.games_played, 1),
                stats.interceptions / max(stats.games_played, 1),
                stats.rushing_yards / max(stats.games_played, 1),
                stats.rushing_tds / max(stats.games_played, 1),
                stats.receiving_yards / max(stats.games_played, 1),
                stats.receiving_tds / max(stats.games_played, 1),
                stats.receptions / max(stats.games_played, 1),
                stats.fumbles / max(stats.games_played, 1),
                stats.two_point_conversions / max(stats.games_played, 1),
                1 if position == 'QB' else 0,  # Position indicators
                1 if position == 'RB' else 0,
                1 if position == 'WR' else 0,
                1 if position == 'TE' else 0
            ]
        
        elif position in ['DEF', 'DST', 'D/ST']:
            # Defense features
            features = [
                stats.games_played,
                stats.def_sacks / max(stats.games_played, 1),
                stats.def_interceptions / max(stats.games_played, 1),
                stats.def_fumbles_recovered / max(stats.games_played, 1),
                stats.def_tds / max(stats.games_played, 1),
                stats.def_safeties / max(stats.games_played, 1),
                stats.def_blocked_kicks / max(stats.games_played, 1),
                stats.def_points_allowed / max(stats.games_played, 1)
            ]
        
        elif position == 'K':
            # Kicker features
            features = [
                stats.games_played,
                stats.fg_made / max(stats.games_played, 1),
                stats.fg_attempts / max(stats.games_played, 1),
                stats.fg_made / max(stats.fg_attempts, 1),  # FG accuracy
                stats.fg_avg_distance,
                stats.fg_long,
                stats.xp_made / max(stats.games_played, 1)
            ]
        
        else:
            # Unknown position - basic features
            features = [stats.games_played, 0, 0, 0, 0]
        
        return np.array(features)
    
    def _calculate_enhanced_confidence(self, stats: PlayerStats, position: str, use_ml: bool = False, 
                                     ml_prediction: float = None, statistical_prediction: float = None) -> float:
        """
        Calculate enhanced confidence score based on multiple factors
        
        Args:
            stats (PlayerStats): Player statistics
            position (str): Player position
            use_ml (bool): Whether ML was used
            ml_prediction (float): ML prediction if available
            statistical_prediction (float): Statistical prediction
            
        Returns:
            float: Confidence score between 0 and 1
        """
        position = position.upper()
        
        # Base confidence from games played (more games = higher confidence)
        games_factor = min(1.0, stats.games_played / 16.0)  # Full season = max confidence from games
        
        # Position-specific confidence adjustments
        position_confidence = {
            'QB': 0.15,    # QBs are more predictable
            'RB': 0.10,    # RBs have moderate predictability
            'WR': 0.08,    # WRs less predictable due to target share
            'TE': 0.08,    # TEs similar to WRs
            'K': 0.12,     # Kickers fairly predictable
            'DEF': 0.10    # Defenses moderately predictable
        }.get(position, 0.05)
        
        # Data quality assessment
        data_quality = 0.0
        
        if position in ['QB', 'RB', 'WR', 'TE']:
            # Assess offensive player data quality
            total_stats = (stats.passing_yards + stats.rushing_yards + stats.receiving_yards)
            if total_stats > 0:
                data_quality += 0.10
            
            if stats.passing_tds + stats.rushing_tds + stats.receiving_tds > 0:
                data_quality += 0.05
                
            if stats.receptions > 0 and position in ['RB', 'WR', 'TE']:
                data_quality += 0.05
                
        elif position == 'K':
            # Assess kicker data quality
            if stats.fg_attempts > 0:
                data_quality += 0.10
                accuracy = stats.fg_made / stats.fg_attempts
                if accuracy > 0.8:  # High accuracy = more confidence
                    data_quality += 0.05
                elif accuracy < 0.6:  # Low accuracy = less confidence
                    data_quality -= 0.03
            
            if stats.xp_made > 0:
                data_quality += 0.05
                
        elif position in ['DEF', 'DST']:
            # Assess defense data quality
            if stats.def_sacks + stats.def_interceptions + stats.def_fumbles_recovered > 0:
                data_quality += 0.10
            
            if stats.def_tds > 0:
                data_quality += 0.05
        
        # ML model confidence boost
        ml_confidence = 0.0
        if use_ml and ML_AVAILABLE:
            ml_confidence = 0.15  # Base ML boost
            
            # If we have both ML and statistical predictions, check agreement
            if ml_prediction is not None and statistical_prediction is not None and statistical_prediction > 0:
                agreement_ratio = min(ml_prediction, statistical_prediction) / max(ml_prediction, statistical_prediction)
                if agreement_ratio > 0.8:  # High agreement = more confidence
                    ml_confidence += 0.10
                elif agreement_ratio < 0.5:  # Low agreement = less confidence
                    ml_confidence -= 0.05
        
        # Season progression bonus (later in season = more data = higher confidence)
        # Assuming we're partway through the season, give a small bonus
        season_progress = min(0.05, stats.games_played / 18.0 * 0.05)
        
        # Combine all factors
        total_confidence = (
            0.4 * games_factor +           # 40% weight on games played
            position_confidence +          # Position-specific base
            data_quality +                 # Data quality assessment
            ml_confidence +                # ML model boost
            season_progress                # Season progression
        )
        
        # Apply position-specific caps and floors
        if position == 'QB':
            total_confidence = max(0.70, min(0.98, total_confidence))  # QBs: 70-98%
        elif position in ['RB', 'WR']:
            total_confidence = max(0.65, min(0.95, total_confidence))  # RB/WR: 65-95%
        elif position == 'TE':
            total_confidence = max(0.60, min(0.92, total_confidence))  # TE: 60-92%
        elif position == 'K':
            total_confidence = max(0.75, min(0.96, total_confidence))  # K: 75-96% (most predictable)
        elif position in ['DEF', 'DST']:
            total_confidence = max(0.55, min(0.90, total_confidence))  # DEF: 55-90%
        else:
            total_confidence = max(0.50, min(0.85, total_confidence))  # Others: 50-85%
        
        return total_confidence
    
    def _train_ml_model(self, position: str, force_retrain: bool = False):
        """
        Train ML model for a specific position
        
        Args:
            position (str): Position to train model for
            force_retrain (bool): Force retraining even if model exists
        """
        if not ML_AVAILABLE:
            debug_print("❌ ML not available - skipping model training")
            return
        
        model_file = self.model_cache_path / f"{position.lower()}_model.pkl"
        scaler_file = self.model_cache_path / f"{position.lower()}_scaler.pkl"
        
        # Skip if model exists and not forcing retrain
        if model_file.exists() and not force_retrain:
            debug_print(f"✅ ML model for {position} already exists")
            return
        
        debug_print(f"🤖 Training ML model for {position}...")
        
        # Load training data
        data = self._load_csv_data()
        if not data:
            debug_print("❌ No CSV data for training")
            return
        
        features = []
        targets = []
        
        # Collect training data based on position
        if position.upper() in ['QB', 'RB', 'WR', 'TE'] and 'weekly' in data:
            df = data['weekly']
            position_df = df[df['position'] == position.upper()]
            
            # Prioritize recent years for training (weight more recent data)
            for _, row in position_df.iterrows():
                # Create stats object
                stats = PlayerStats(
                    player_name=row['player_display_name'],
                    position=row['position'],
                    team='N/A',
                    games_played=1,
                    passing_yards=row.get('passing_yards', 0),
                    passing_tds=row.get('passing_tds', 0),
                    interceptions=row.get('interceptions', 0),
                    rushing_yards=row.get('rushing_yards', 0),
                    rushing_tds=row.get('rushing_tds', 0),
                    receiving_yards=row.get('receiving_yards', 0),
                    receiving_tds=row.get('receiving_tds', 0),
                    receptions=row.get('receptions', 0),
                    fumbles=(row.get('rushing_fumbles_lost', 0) + row.get('receiving_fumbles_lost', 0)),
                    two_point_conversions=(row.get('passing_2pt_conversions', 0) + 
                                         row.get('rushing_2pt_conversions', 0) + 
                                         row.get('receiving_2pt_conversions', 0))
                )
                
                feature_vector = self._prepare_ml_features(stats)
                features.append(feature_vector)
                
                # Use the fantasy points from CSV as target
                if self.scoring_system == 'ppr':
                    target = row.get('fantasy_points_ppr', row.get('fantasy_points', 0))
                else:
                    target = row.get('fantasy_points', 0)
                
                # Weight recent years more heavily (2024+ gets full weight, earlier years get reduced weight)
                data_year = row.get('data_year', self.current_season)
                if data_year >= 2024:
                    weight = 1.0
                elif data_year >= 2023:
                    weight = 0.8
                elif data_year >= 2022:
                    weight = 0.6
                else:
                    weight = 0.4
                
                # Add multiple copies for weighting (simple approach)
                for _ in range(int(weight * 10) // 2):
                    targets.append(target)
                    if len(targets) > len(features):
                        features.append(feature_vector)
        
        elif position.upper() in ['DEF', 'DST'] and 'defense' in data:
            df = data['defense']
            
            for _, row in df.iterrows():
                stats = PlayerStats(
                    player_name=f"{row['team']} DEF",
                    position='DEF',
                    team=row['team'],
                    games_played=1,
                    def_sacks=row.get('sacks', 0),
                    def_interceptions=row.get('interceptions', 0),
                    def_fumbles_recovered=row.get('fumbles', 0),
                    def_tds=0,  # Set to 0 since def_tds in CSV is actually points allowed
                    def_safeties=row.get('safeties', 0),
                    def_blocked_kicks=row.get('blocked_kicks', 0),
                    def_points_allowed=row.get('def_tds', 0)  # Use def_tds column as points allowed
                )
                
                feature_vector = self._prepare_ml_features(stats)
                features.append(feature_vector)
                
                # Calculate defense points manually (excluding def_tds)
                stat_dict = {
                    'def_sacks': row.get('sacks', 0),
                    'def_interceptions': row.get('interceptions', 0),
                    'def_fumbles_recovered': row.get('fumbles', 0),
                    'def_tds': 0,  # Set to 0
                    'def_safeties': row.get('safeties', 0),
                    'def_blocked_kicks': row.get('blocked_kicks', 0),
                    'def_points_allowed': row.get('def_tds', 0)  # Points allowed
                }
                points, _ = self._calculate_fantasy_points(stat_dict, 'DEF')
                targets.append(points)
        
        elif position.upper() == 'K' and 'kickers' in data:
            df = data['kickers']
            
            for _, row in df.iterrows():
                stats = PlayerStats(
                    player_name=row['kicker'],
                    position='K',
                    team=row['team'],
                    games_played=1,
                    fg_made=row.get('fg_made', 0),
                    fg_attempts=row.get('fg_attempts', 0),
                    fg_avg_distance=row.get('fg_avg_dist', 0),
                    fg_long=row.get('fg_long', 0),
                    xp_made=row.get('xp_made', 0)
                )
                
                feature_vector = self._prepare_ml_features(stats)
                features.append(feature_vector)
                
                # Calculate kicker points manually
                stat_dict = {
                    'fg_made': row.get('fg_made', 0),
                    'fg_attempts': row.get('fg_attempts', 0),
                    'fg_avg_distance': row.get('fg_avg_dist', 0),
                    'xp_made': row.get('xp_made', 0)
                }
                points, _ = self._calculate_fantasy_points(stat_dict, 'K')
                targets.append(points)
        
        if len(features) < 10:  # Need minimum data for training
            debug_print(f"❌ Insufficient data for {position} model training ({len(features)} samples)")
            return
        
        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(targets)
        
        # Remove any NaN or infinite values
        valid_mask = np.isfinite(X).all(axis=1) & np.isfinite(y)
        X = X[valid_mask]
        y = y[valid_mask]
        
        if len(X) < 10:
            debug_print(f"❌ Insufficient valid data for {position} model training")
            return
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train ensemble of models
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boost': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear': LinearRegression()
        }
        
        best_model = None
        best_score = float('-inf')
        
        for name, model in models.items():
            try:
                # Cross-validation score
                scores = cross_val_score(model, X_scaled, y, cv=min(5, len(X)//2), 
                                       scoring='neg_mean_absolute_error')
                avg_score = scores.mean()
                
                debug_print(f"📊 {name} CV score for {position}: {-avg_score:.2f}")
                
                if avg_score > best_score:
                    best_score = avg_score
                    best_model = model
            
            except Exception as e:
                debug_print(f"❌ Error training {name} for {position}: {e}")
        
        if best_model is not None:
            # Train best model on full dataset
            best_model.fit(X_scaled, y)
            
            # Save model and scaler
            with open(model_file, 'wb') as f:
                pickle.dump(best_model, f)
            
            with open(scaler_file, 'wb') as f:
                pickle.dump(scaler, f)
            
            # Store in memory
            self.ml_models[position] = best_model
            self.ml_scalers[position] = scaler
            
            debug_print(f"✅ Trained and saved ML model for {position} (score: {-best_score:.2f})")
        else:
            debug_print(f"❌ Failed to train ML model for {position}")
    
    def _load_ml_models(self):
        """Load existing ML models from disk"""
        if not ML_AVAILABLE:
            return
        
        positions = ['QB', 'RB', 'WR', 'TE', 'DEF', 'K']
        
        for position in positions:
            model_file = self.model_cache_path / f"{position.lower()}_model.pkl"
            scaler_file = self.model_cache_path / f"{position.lower()}_scaler.pkl"
            
            if model_file.exists() and scaler_file.exists():
                try:
                    with open(model_file, 'rb') as f:
                        self.ml_models[position] = pickle.load(f)
                    
                    with open(scaler_file, 'rb') as f:
                        self.ml_scalers[position] = pickle.load(f)
                    
                    debug_print(f"✅ Loaded ML model for {position}")
                
                except Exception as e:
                    debug_print(f"❌ Error loading ML model for {position}: {e}")
    
    def get_projection(self, player_name: str, position: str = None, use_ml: bool = True) -> Optional[PlayerProjection]:
        """
        Get fantasy projection for a player using CSV data
        
        Args:
            player_name (str): Name of the player
            position (str): Position (optional - will be detected if not provided)
            use_ml (bool): Whether to use ML for projection
            
        Returns:
            PlayerProjection or None if player not found
        """
        # Get player stats from CSV
        stats = self.get_player_stats_from_csv(player_name, position)
        
        if not stats:
            return None
        
        # Check injury status first - if player is out, return 0 projection
        data = self._load_csv_data()
        if self._check_injury_status(player_name, data):
            return PlayerProjection(
                player_name=stats.player_name,
                position=stats.position.upper(),
                team=stats.team,
                projected_points=0.0,
                confidence=1.0,  # 100% confident they'll score 0 if out
                week=self.current_week,
                season=self.current_season,
                scoring_breakdown={"injury": 0.0},
                data_source="CSV - INJURED OUT",
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        
        position = stats.position.upper()
        
        # Prepare stats dictionary for calculation
        stat_dict = asdict(stats)
        
        # Calculate base fantasy points
        base_points, breakdown = self._calculate_fantasy_points(stat_dict, position)
        
        # If no games played, can't make meaningful projection
        if stats.games_played == 0:
            projected_points = 0.0
            confidence = 0.0
        else:
            # Calculate per-game average
            per_game_points = base_points / stats.games_played
            
            # Use ML for projection if available and requested
            if use_ml and ML_AVAILABLE and position in self.ml_models:
                try:
                    model = self.ml_models[position]
                    scaler = self.ml_scalers[position]
                    
                    # Prepare features
                    features = self._prepare_ml_features(stats).reshape(1, -1)
                    features_scaled = scaler.transform(features)
                    
                    # Get ML prediction
                    ml_prediction = model.predict(features_scaled)[0]
                    
                    # Blend ML prediction with statistical average
                    # Weight more towards ML if we have more games (more confidence)
                    ml_weight = min(0.8, stats.games_played / 10.0)
                    projected_points = (ml_weight * ml_prediction + 
                                      (1 - ml_weight) * per_game_points)
                    
                    # Enhanced confidence calculation for ML predictions
                    confidence = self._calculate_enhanced_confidence(stats, position, use_ml=True, ml_prediction=ml_prediction, statistical_prediction=per_game_points)
                    
                    debug_print(f"🤖 ML projection for {player_name}: {ml_prediction:.2f} (weight: {ml_weight:.2f})")
                
                except Exception as e:
                    debug_print(f"❌ ML prediction failed for {player_name}: {e}")
                    projected_points = per_game_points
                    confidence = self._calculate_enhanced_confidence(stats, position, use_ml=False)
            
            else:
                # Use statistical projection
                projected_points = per_game_points
                confidence = self._calculate_enhanced_confidence(stats, position, use_ml=False)
        
        # Create projection object
        projection = PlayerProjection(
            player_name=stats.player_name,
            position=position,
            team=stats.team,
            projected_points=projected_points,
            confidence=confidence,
            week=self.current_week,
            season=self.current_season,
            scoring_breakdown=breakdown,
            data_source="CSV",
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        debug_print(f"✅ Projection for {player_name} ({position}): {projected_points:.2f} pts (confidence: {confidence:.1%})")
        
        return projection
    
    def get_multiple_projections(self, player_names: List[str], use_ml: bool = True) -> Dict[str, PlayerProjection]:
        """
        Get projections for multiple players
        
        Args:
            player_names (List[str]): List of player names
            use_ml (bool): Whether to use ML for projections
            
        Returns:
            Dictionary mapping player names to their projections
        """
        projections = {}
        
        for player_name in player_names:
            projection = self.get_projection(player_name, use_ml=use_ml)
            if projection:
                projections[player_name] = projection
            else:
                debug_print(f"❌ No projection available for {player_name}")
        
        return projections
    
    def train_all_models(self, force_retrain: bool = False):
        """
        Train ML models for all positions
        
        Args:
            force_retrain (bool): Force retraining even if models exist
        """
        if not ML_AVAILABLE:
            debug_print("❌ ML not available - cannot train models")
            return
        
        positions = ['QB', 'RB', 'WR', 'TE', 'DEF', 'K']
        
        debug_print("🤖 Starting ML model training for all positions...")
        
        for position in positions:
            self._train_ml_model(position, force_retrain)
        
        debug_print("✅ Completed ML model training")
    
    def update_with_new_data(self, daily_update: bool = True):
        """
        Update ML models with new data (simulates daily learning)
        
        Args:
            daily_update (bool): Whether this is a daily incremental update
        """
        if not ML_AVAILABLE:
            debug_print("❌ ML not available - cannot update models")
            return
        
        debug_print("📚 Updating models with new data...")
        
        # For daily updates, retrain models to incorporate new data
        if daily_update:
            self.train_all_models(force_retrain=True)
        
        debug_print("✅ Model update completed")
    
    def export_projections_to_csv(self, projections: Dict[str, PlayerProjection], 
                                filename: str = None) -> str:
        """
        Export projections to CSV file
        
        Args:
            projections (Dict): Dictionary of projections
            filename (str): Output filename (optional)
            
        Returns:
            str: Path to created CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"projections_{timestamp}.csv"
        
        # Convert projections to DataFrame
        rows = []
        for player_name, projection in projections.items():
            row = {
                'player_name': projection.player_name,
                'position': projection.position,
                'team': projection.team,
                'projected_points': projection.projected_points,
                'confidence': projection.confidence,
                'week': projection.week,
                'season': projection.season,
                'data_source': projection.data_source,
                'last_updated': projection.last_updated
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Save to CSV
        output_path = self.data_path / filename
        df.to_csv(output_path, index=False)
        
        debug_print(f"📊 Exported {len(projections)} projections to {output_path}")
        
        return str(output_path)


# Convenience functions for easy usage
def get_csv_projection(player_name: str, scoring_system: str = "ppr", use_ml: bool = True) -> Optional[PlayerProjection]:
    """
    Quick function to get a single player projection
    
    Args:
        player_name (str): Name of the player
        scoring_system (str): Scoring system to use
        use_ml (bool): Whether to use ML
        
    Returns:
        PlayerProjection or None
    """
    lib = CSVProjectionsLibrary(scoring_system=scoring_system)
    return lib.get_projection(player_name, use_ml=use_ml)


def bulk_csv_projections(player_names: List[str], scoring_system: str = "ppr", use_ml: bool = True) -> Dict[str, PlayerProjection]:
    """
    Get projections for multiple players
    
    Args:
        player_names (List[str]): List of player names
        scoring_system (str): Scoring system to use
        use_ml (bool): Whether to use ML
        
    Returns:
        Dictionary of projections
    """
    lib = CSVProjectionsLibrary(scoring_system=scoring_system)
    return lib.get_multiple_projections(player_names, use_ml=use_ml)


def train_all_csv_models(data_path: str = None, force_retrain: bool = False):
    """
    Train all ML models using CSV data
    
    Args:
        data_path (str): Path to CSV data directory
        force_retrain (bool): Force retraining
    """
    lib = CSVProjectionsLibrary(data_path=data_path)
    lib.train_all_models(force_retrain=force_retrain)


def export_csv_projections(projections: Dict[str, PlayerProjection], filename: str = None) -> str:
    """
    Export projections to CSV
    
    Args:
        projections (Dict): Projections to export
        filename (str): Output filename
        
    Returns:
        str: Path to exported file
    """
    lib = CSVProjectionsLibrary()
    return lib.export_projections_to_csv(projections, filename)

#!/usr/bin/env python3
"""
NFL Player Projections Generator
Generates comprehensive player projections using ML models from CSV data

This script:
1. Extracts all player names from CSV data files
2. Runs ML projections for each player
3. Collects injury status and season statistics
4. Creates/appends to df_projected_points_[year].csv with comprehensive data

Author: NFL Projections System
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime
from typing import Dict, List, Set, Optional
import logging, requests

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

# Add the nfl_stats directory to the path so we can import the library
current_dir = Path(__file__).parent
nfl_stats_dir = current_dir / "nfl_stats"
sys.path.append(str(nfl_stats_dir))

try:
    from nfl_projections_library import CSVProjectionsLibrary, PlayerProjection
    print("✅ Successfully imported nfl_projections_library")
except ImportError as e:
    print(f"❌ Error importing nfl_projections_library: {e}")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('projections_generation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProjectionsGenerator:
    """
    Generates comprehensive player projections from CSV data
    """
    
    def __init__(self, scoring_system: str = "ppr"):
        """
        Initialize the projections generator
        
        Args:
            scoring_system (str): Fantasy scoring system to use
        """
        self.scoring_system = scoring_system
        self.data_path = nfl_stats_dir / "data"
        self.output_path = current_dir
        
        # Get current NFL season and week from API
        self.current_nfl_season = int(season)
        self.current_nfl_week = int(week)
        
        # Initialize the projections library
        self.proj_lib = CSVProjectionsLibrary(scoring_system=scoring_system, data_path=str(self.data_path))
        
        # Find the most recent data files available
        self.available_years = self._find_available_data_years()
        self.projection_year = self._determine_projection_year()
        
        # Output filename
        self.output_filename = f"df_projected_points_{self.projection_year}.csv"
        self.output_filepath = self.output_path / self.output_filename
        
        logger.info(f"NFL State: Season {self.current_nfl_season}, Week {self.current_nfl_week}")
        logger.info(f"Available data years: {sorted(self.available_years)}")
        logger.info(f"Using {self.projection_year} for projections")
        logger.info(f"Output file: {self.output_filepath}")
    
    def _get_team_city_map(self) -> Dict[str, str]:
        """Get team abbreviation to full city name mapping"""
        return {
            'ARI': 'Arizona',
            'ATL': 'Atlanta', 
            'BAL': 'Baltimore',
            'BUF': 'Buffalo',
            'CAR': 'Carolina',
            'CHI': 'Chicago',
            'CIN': 'Cincinnati',
            'CLE': 'Cleveland',
            'DAL': 'Dallas',
            'DEN': 'Denver',
            'DET': 'Detroit',
            'GB': 'Green Bay',
            'HOU': 'Houston',
            'IND': 'Indianapolis',
            'JAX': 'Jacksonville',
            'KC': 'Kansas City',
            'LV': 'Las Vegas',
            'LAC': 'Los Angeles',
            'LAR': 'Los Angeles',
            'MIA': 'Miami',
            'MIN': 'Minnesota',
            'NE': 'New England',
            'NO': 'New Orleans',
            'NYG': 'New York',
            'NYJ': 'New York',
            'PHI': 'Philadelphia',
            'PIT': 'Pittsburgh',
            'SF': 'San Francisco',
            'SEA': 'Seattle',
            'TB': 'Tampa Bay',
            'TEN': 'Tennessee',
            'WAS': 'Washington'
        }
    
    def _get_team_abbr_from_full_name(self, full_name: str) -> str:
        """Convert full team name back to abbreviation for library calls"""
        team_city_map = self._get_team_city_map()
        # Create reverse mapping
        reverse_map = {v: k for k, v in team_city_map.items()}
        return reverse_map.get(full_name, full_name)
    
    def _find_available_data_years(self) -> Set[int]:
        """Find all available data years in the data directory"""
        years = set()
        
        # Check for weekly files
        for file in self.data_path.glob("df_weekly_*.csv"):
            try:
                year = int(file.stem.split('_')[-1])
                years.add(year)
            except ValueError:
                continue
                
        # Check for defense files
        for file in self.data_path.glob("dst_stats_*.csv"):
            try:
                year = int(file.stem.split('_')[-1])
                years.add(year)
            except ValueError:
                continue
                
        # Check for kicker files
        for file in self.data_path.glob("kicker_stats_*.csv"):
            try:
                year = int(file.stem.split('_')[-1])
                years.add(year)
            except ValueError:
                continue
        
        return years
    
    def _determine_projection_year(self) -> int:
        """Determine which year to use for projections"""
        if not self.available_years:
            logger.warning("No data files found!")
            return self.current_nfl_season
            
        # Use current NFL season if available, otherwise use the most recent year
        if self.current_nfl_season in self.available_years:
            return self.current_nfl_season
        else:
            most_recent = max(self.available_years)
            logger.info(f"No {self.current_nfl_season} data found, using {most_recent} data")
            return most_recent
    
    def extract_all_player_names(self) -> Dict[str, Set[str]]:
        """
        Extract all unique player names from ALL available CSV files, organized by position
        
        Returns:
            Dict[str, Set[str]]: Dictionary mapping positions to sets of player names
        """
        players_by_position = {
            'QB': set(),
            'RB': set(), 
            'WR': set(),
            'TE': set(),
            'K': set(),
            'DEF': set()
        }
        
        logger.info("Extracting player names from ALL available CSV files...")
        
        # Extract from ALL weekly stats files (offensive players)
        weekly_files = list(self.data_path.glob("df_weekly_*.csv"))
        if weekly_files:
            total_weekly_records = 0
            for weekly_file in weekly_files:
                try:
                    df_weekly = pd.read_csv(weekly_file)
                    total_weekly_records += len(df_weekly)
                    
                    for _, row in df_weekly.iterrows():
                        player_name = row.get('player_display_name', '').strip()
                        position = row.get('position', '').strip().upper()
                        
                        if player_name and position in players_by_position:
                            players_by_position[position].add(player_name)
                except Exception as e:
                    logger.warning(f"Error reading {weekly_file}: {e}")
            
            logger.info(f"Loaded {total_weekly_records} records from {len(weekly_files)} weekly stats files")
        else:
            logger.warning("No weekly stats files found")
        
        # Extract from ALL defense stats files
        dst_files = list(self.data_path.glob("dst_stats_*.csv"))
        if dst_files:
            total_dst_records = 0
            team_city_map = self._get_team_city_map()
            
            for dst_file in dst_files:
                try:
                    df_dst = pd.read_csv(dst_file)
                    total_dst_records += len(df_dst)
                    
                    for _, row in df_dst.iterrows():
                        team_abbr = row.get('team', '').strip().upper()
                        if team_abbr and team_abbr in team_city_map:
                            full_team_name = team_city_map[team_abbr]
                            players_by_position['DEF'].add(full_team_name)
                        elif team_abbr:  # Fallback for unknown abbreviations
                            players_by_position['DEF'].add(f"{team_abbr} Defense")
                except Exception as e:
                    logger.warning(f"Error reading {dst_file}: {e}")
            
            logger.info(f"Loaded {total_dst_records} records from {len(dst_files)} defense stats files")
        else:
            logger.warning("No defense stats files found")
        
        # Extract from ALL kicker stats files
        kicker_files = list(self.data_path.glob("kicker_stats_*.csv"))
        if kicker_files:
            total_kicker_records = 0
            for kicker_file in kicker_files:
                try:
                    df_kicker = pd.read_csv(kicker_file)
                    total_kicker_records += len(df_kicker)
                    
                    # Check if we have the 'kicker' column (new format) or other column names
                    kicker_column = None
                    if 'kicker' in df_kicker.columns:
                        kicker_column = 'kicker'
                    elif 'player_name' in df_kicker.columns:
                        kicker_column = 'player_name'
                    elif 'kicker_name' in df_kicker.columns:
                        kicker_column = 'kicker_name'
                    
                    if kicker_column:
                        for _, row in df_kicker.iterrows():
                            kicker_name = row.get(kicker_column, '')
                            # Handle NaN values and ensure it's a string
                            if pd.notna(kicker_name) and str(kicker_name).strip():
                                players_by_position['K'].add(str(kicker_name).strip())
                    else:
                        logger.warning(f"No recognized kicker name column found in {kicker_file}. Available columns: {list(df_kicker.columns)}")
                        
                except Exception as e:
                    logger.warning(f"Error reading {kicker_file}: {e}")
            
            logger.info(f"Loaded {total_kicker_records} records from {len(kicker_files)} kicker stats files")
        else:
            logger.warning("No kicker stats files found")
        
        # Log summary
        total_players = sum(len(players) for players in players_by_position.values())
        logger.info(f"Extracted {total_players} unique players:")
        for position, players in players_by_position.items():
            logger.info(f"   {position}: {len(players)} players")
        
        return players_by_position
    
    def get_injury_status(self, player_name: str) -> str:
        """
        Get injury status for a player from injury data for CURRENT NFL WEEK only
        
        Args:
            player_name (str): Name of the player
            
        Returns:
            str: Injury status (e.g., 'Healthy', 'Out', 'Doubtful', etc.)
        """
        # Look for ALL injury files
        injury_files = list(self.data_path.glob("df_injury_*.csv"))
        
        if not injury_files:
            logger.debug(f"No injury files found for {player_name}")
            return "Healthy"
        
        try:
            # Combine all injury data
            all_injury_data = []
            for injury_file in injury_files:
                try:
                    df_injury = pd.read_csv(injury_file)
                    all_injury_data.append(df_injury)
                except Exception as e:
                    logger.warning(f"Error reading {injury_file}: {e}")
            
            if not all_injury_data:
                return "Healthy"
            
            # Combine all injury dataframes
            combined_injury_df = pd.concat(all_injury_data, ignore_index=True)
            
            # Filter to current NFL season and current NFL week ONLY
            current_injuries = combined_injury_df[
                (combined_injury_df.get('season', 0) == self.current_nfl_season) &
                (combined_injury_df.get('week', 0) == self.current_nfl_week)
            ]
            
            logger.debug(f"Checking injuries for NFL Season {self.current_nfl_season}, Week {self.current_nfl_week}")
            logger.debug(f"Found {len(current_injuries)} current week injury records")
            
            if current_injuries.empty:
                logger.debug(f"No injury data for current week - {player_name} is Healthy")
                return "Healthy"
            
            # Look for player in current week injury report
            name_columns = ['full_name', 'player_display_name']
            
            for col in name_columns:
                if col in current_injuries.columns:
                    player_injury = current_injuries[
                        current_injuries[col].str.lower() == player_name.lower()
                    ]
                    
                    if not player_injury.empty:
                        # Check report status - prioritize report_status over practice_status
                        status_columns = ['report_status', 'practice_status']
                        
                        for status_col in status_columns:
                            if status_col in player_injury.columns:
                                status = player_injury[status_col].iloc[0]
                                if pd.notna(status) and status.strip() and status.strip().lower() != 'nan':
                                    injury_status = status.strip().title()
                                    logger.debug(f"{player_name} injury status: {injury_status}")
                                    return injury_status
            
            # If player not found in current week injury report, they are healthy
            logger.debug(f"{player_name} not in current week injury report - Healthy")
            return "Healthy"
            
        except Exception as e:
            logger.warning(f"Error checking injury status for {player_name}: {e}")
            return "Unknown"
    
    def get_season_stats(self, player_name: str, position: str) -> Dict[str, float]:
        """
        Get season totals for a player (rounded to 2 decimal places)
        
        Args:
            player_name (str): Name of the player
            position (str): Player position
            
        Returns:
            Dict[str, float]: Season statistics rounded to 2 decimal places
        """
        stats = {}
        
        try:
            # Get player stats using the library
            player_stats = self.proj_lib.get_player_stats_from_csv(player_name, position)
            
            if player_stats:
                if position in ['QB', 'RB', 'WR', 'TE']:
                    stats = {
                        'games_played': round(player_stats.games_played, 2),
                        'passing_yards': round(player_stats.passing_yards, 2),
                        'passing_tds': round(player_stats.passing_tds, 2),
                        'interceptions': round(player_stats.interceptions, 2),
                        'rushing_yards': round(player_stats.rushing_yards, 2),
                        'rushing_tds': round(player_stats.rushing_tds, 2),
                        'receiving_yards': round(player_stats.receiving_yards, 2),
                        'receiving_tds': round(player_stats.receiving_tds, 2),
                        'receptions': round(player_stats.receptions, 2),
                        'fumbles': round(player_stats.fumbles, 2),
                        'two_point_conversions': round(player_stats.two_point_conversions, 2)
                    }
                elif position in ['DEF', 'DST']:
                    stats = {
                        'games_played': round(player_stats.games_played, 2),
                        'def_sacks': round(player_stats.def_sacks, 2),
                        'def_interceptions': round(player_stats.def_interceptions, 2),
                        'def_fumbles_recovered': round(player_stats.def_fumbles_recovered, 2),
                        'def_tds': round(player_stats.def_tds, 2),
                        'def_safeties': round(player_stats.def_safeties, 2),
                        'def_blocked_kicks': round(player_stats.def_blocked_kicks, 2),
                        'def_points_allowed': round(player_stats.def_points_allowed, 2)
                    }
                elif position == 'K':
                    stats = {
                        'games_played': round(player_stats.games_played, 2),
                        'fg_made': round(player_stats.fg_made, 2),
                        'fg_attempts': round(player_stats.fg_attempts, 2),
                        'fg_avg_distance': round(player_stats.fg_avg_distance, 2),
                        'fg_long': round(player_stats.fg_long, 2),
                        'xp_made': round(player_stats.xp_made, 2)
                    }
        
        except Exception as e:
            logger.warning(f"Error getting season stats for {player_name}: {e}")
        
        return stats
    
    def load_existing_projections(self) -> pd.DataFrame:
        """
        Load existing projections file if it exists
        
        Returns:
            pd.DataFrame: Existing projections or empty DataFrame
        """
        if self.output_filepath.exists():
            try:
                df = pd.read_csv(self.output_filepath)
                logger.info(f"Loaded {len(df)} existing projections")
                return df
            except Exception as e:
                logger.warning(f"Error loading existing file: {e}")
                return pd.DataFrame()
        else:
            logger.info("Creating new projections file")
            return pd.DataFrame()
    
    def player_exists_in_df(self, df: pd.DataFrame, player_name: str, week: int, season: int) -> bool:
        """
        Check if player projection already exists for this week/season
        
        Args:
            df (pd.DataFrame): Existing projections DataFrame
            player_name (str): Player name
            week (int): Week number
            season (int): Season year
            
        Returns:
            bool: True if player already exists for this week/season
        """
        if df.empty:
            return False
        
        existing = df[
            (df['player_name'].str.lower() == player_name.lower()) &
            (df['week'] == week) &
            (df['season'] == season)
        ]
        
        return not existing.empty
    
    def generate_all_projections(self, use_ml: bool = True, force_update: bool = False):
        """
        Generate projections for all players and save to CSV
        
        Args:
            use_ml (bool): Whether to use ML models for projections
            force_update (bool): Force update existing records
        """
        logger.info(f"Starting projection generation for season {self.projection_year}")
        
        # Train ML models if needed
        if use_ml:
            logger.info("Training ML models...")
            self.proj_lib.train_all_models()
        
        # Extract all player names
        players_by_position = self.extract_all_player_names()
        
        # Load existing projections
        existing_df = self.load_existing_projections()
        
        # Prepare new projections list
        new_projections = []
        skipped_count = 0
        error_count = 0
        
        # Process each position
        for position, player_names in players_by_position.items():
            logger.info(f"Processing {len(player_names)} {position} players...")
            
            for player_name in player_names:
                try:
                    # Skip if already exists and not forcing update
                    if not force_update and self.player_exists_in_df(existing_df, player_name, self.current_nfl_week, self.current_nfl_season):
                        skipped_count += 1
                        continue
                    
                    # For defense teams, convert full name back to abbreviation for library call
                    projection_name = player_name
                    if position == 'DEF':
                        team_abbr = self._get_team_abbr_from_full_name(player_name)
                        if team_abbr != player_name:  # If we found a mapping
                            projection_name = f"{team_abbr} DEF"
                    
                    # Get ML projection
                    projection = self.proj_lib.get_projection(projection_name, position, use_ml=use_ml)
                    
                    if projection:
                        # Get injury status
                        injury_status = self.get_injury_status(player_name)
                        
                        # Get season stats  
                        season_stats = self.get_season_stats(projection_name, position)
                        
                        # Create projection record with rounded values
                        record = {
                            'player_name': player_name,  # Use the full team name for defense
                            'position': projection.position,
                            'team': projection.team,
                            'projected_points': round(projection.projected_points, 2),
                            'confidence': round(projection.confidence, 2),
                            'injury_status': injury_status,
                            'week': self.current_nfl_week,
                            'season': self.current_nfl_season,
                            'scoring_system': self.scoring_system,
                            'data_source': projection.data_source,
                            'last_updated': projection.last_updated
                        }
                        
                        # Add season stats
                        record.update(season_stats)
                        
                        new_projections.append(record)
                        
                        if len(new_projections) % 50 == 0:
                            logger.info(f"   Processed {len(new_projections)} players...")
                    
                    else:
                        logger.warning(f"No projection available for {player_name}")
                        error_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing {player_name}: {e}")
                    error_count += 1
        
        # Convert to DataFrame
        if new_projections:
            new_df = pd.DataFrame(new_projections)
            
            # Combine with existing data
            if not existing_df.empty:
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                # Remove duplicates (keep last occurrence)
                combined_df = combined_df.drop_duplicates(
                    subset=['player_name', 'week', 'season'], 
                    keep='last'
                )
            else:
                combined_df = new_df
            
            # Sort by projected points descending
            combined_df = combined_df.sort_values('projected_points', ascending=False)
            
            # Save to CSV
            combined_df.to_csv(self.output_filepath, index=False)
            
            logger.info(f"Successfully generated projections:")
            logger.info(f"   New projections: {len(new_projections)}")
            logger.info(f"   Skipped existing: {skipped_count}")
            logger.info(f"   Errors: {error_count}")
            logger.info(f"   Total in file: {len(combined_df)}")
            logger.info(f"   Saved to: {self.output_filepath}")
            
            # Show top 10 projections
            logger.info("\nTop 10 Projected Players:")
            top_10 = combined_df.head(10)[['player_name', 'position', 'projected_points', 'confidence', 'injury_status']]
            for _, row in top_10.iterrows():
                logger.info(f"   {row['player_name']} ({row['position']}): {row['projected_points']:.2f} pts ({row['confidence']:.1%} conf) - {row['injury_status']}")
        
        else:
            logger.warning("No new projections generated")


def main():
    """
    Main function to run projections generation
    """
    logger.info("NFL Player Projections Generator Starting...")
    
    try:
        # Initialize generator
        generator = ProjectionsGenerator(scoring_system="ppr")
        
        # Generate projections
        generator.generate_all_projections(use_ml=True, force_update=False)
        
        logger.info("Projection generation completed successfully!")
        
    except Exception as e:
        logger.error(f"Fatal error in projection generation: {e}")
        raise


if __name__ == "__main__":
    main()

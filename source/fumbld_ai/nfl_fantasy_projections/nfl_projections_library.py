"""
NFL Fantasy Points Projections Library
Using Yahoo! Sports API with OAuth authentication

This library provides functions to calculate NFL player fantasy projections
using both live Yahoo Sports data and sample data for testing.

Author: Your NFL Projections System
Version: 1.0.0
"""

# Debug printing control
DEBUG_PRINTS = True  # Set to False to disable all print statements

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import time
import json
import pickle
import os

# Optional import for Yahoo Fantasy API - only needed for live data
try:
    import yahoo_fantasy_api as yfa
    YAHOO_API_AVAILABLE = True
except ImportError:
    YAHOO_API_AVAILABLE = False
    if DEBUG_PRINTS:
        print("⚠️  yahoo_fantasy_api not installed. Sample data mode only.")
        print("   To use Yahoo API: pip install yahoo_fantasy_api")

# Optional imports for ML - graceful fallback if not available
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
    """
    Data class representing a player's fantasy projection
    """
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
    """
    Data class representing a player's season statistics
    """
    player_name: str
    player_id: str
    position: str
    team: str
    games_played: int
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
    def_yards_allowed: float = 0.0


class NFLProjectionsLibrary:
    """
    Main class for NFL Fantasy Points Projections
    
    This library calculates fantasy football projections using Yahoo Sports API
    and provides fallback sample data for testing.
    """
    
    def __init__(self, scoring_system: str = "ppr"):
        """
        Initialize the projections library
        
        Args:
            scoring_system (str): Fantasy scoring system - "ppr", "half_ppr", "standard", or "superflex"
        """
        self.current_season = datetime.now().year
        self.current_week = 1# self._calculate_nfl_week()
        
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
                'def_points_allowed_35_plus': -4 # 35+ points allowed
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
                # Defense scoring
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
                'def_points_allowed_35_plus': -4
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
                # Defense scoring
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
                'def_points_allowed_35_plus': -4
            },
            "superflex": {
                'passing_yards': 0.04,
                'passing_tds': 6,        # Higher QB scoring
                'interceptions': -2,
                'rushing_yards': 0.1,
                'rushing_tds': 6,
                'receiving_yards': 0.1,
                'receiving_tds': 6,
                'receptions': 1,
                'fumbles': -2,
                'two_point_conversions': 2,
                # Defense scoring
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
                'def_points_allowed_35_plus': -4
            }
        }
        
        self.scoring = self.scoring_systems.get(scoring_system, self.scoring_systems["ppr"])
        self.scoring_system = scoring_system
        self._yahoo_nfl = None
        self._game_id = None
        self._oauth = None
        self._league_ids = []
        
        # ML Model attributes
        self._ml_models = {}
        self._scaler = None
        self._feature_columns = [
            'passing_yards_per_game', 'passing_tds_per_game', 'interceptions_per_game',
            'rushing_yards_per_game', 'rushing_tds_per_game',
            'receiving_yards_per_game', 'receiving_tds_per_game', 'receptions_per_game',
            'fumbles_per_game', 'two_point_conversions_per_game',
            'games_played', 'position_encoded'
        ]
        
        # Initialize ML models if available
        if ML_AVAILABLE:
            self._initialize_ml_models()
        
        # Yahoo Fantasy API stat ID mappings (from actual API documentation)
        self._stat_categories = {
            '4': 'Passing Yards',
            '5': 'Passing Touchdowns', 
            '6': 'Interceptions',
            '9': 'Rushing Yards',
            '10': 'Rushing Touchdowns',
            '11': 'Receptions',
            '12': 'Reception Yards',
            '13': 'Reception Touchdowns',
            '15': 'Return Touchdowns',
            '16': '2-Point Conversions',
            '18': 'Fumbles Lost',
            '57': 'Offensive Fumble Return TD',
            '19': 'Field Goals 0-19 Yards',
            '20': 'Field Goals 20-29 Yards',
            '21': 'Field Goals 30-39 Yards',
            '22': 'Field Goals 40-49 Yards',
            '23': 'Field Goals 50+ Yards',
            '24': 'Field Goals Missed 0-19 Yards',
            '25': 'Field Goals Missed 20-29 Yards',
            '29': 'Point After Attempt Made',
            '30': 'Point After Attempt Missed',
            '31': 'Points Allowed',
            '32': 'Sack',
            '33': 'Interception',
            '34': 'Fumble Recovery',
            '35': 'Touchdown',
            '36': 'Safety',
            '37': 'Block Kick',
            '50': 'Points Allowed 0 points',
            '51': 'Points Allowed 1-6 points',
            '52': 'Points Allowed 7-13 points',
            '53': 'Points Allowed 14-20 points',
            '54': 'Points Allowed 21-27 points',
            '55': 'Points Allowed 28-34 points',
            '56': 'Points Allowed 35+ points'
        }
        
    def _calculate_nfl_week(self) -> int:
        """Calculate current NFL week based on date"""
        current_date = datetime.now()
        
        # NFL season typically starts first Thursday after Labor Day (early September)
        if current_date.month >= 9:
            season_start = datetime(current_date.year, 9, 7)
        elif current_date.month <= 2:
            season_start = datetime(current_date.year - 1, 9, 7)
        else:
            return 1  # Off-season
        
        days_passed = (current_date - season_start).days
        week = max(1, min(18, (days_passed // 7) + 1))
        return week
    
    def _initialize_ml_models(self) -> None:
        """Initialize machine learning models for projections"""
        if not ML_AVAILABLE:
            return
            
        try:
            self._ml_models = {
                'random_forest': RandomForestRegressor(
                    n_estimators=100, 
                    random_state=42, 
                    max_depth=10
                ),
                'gradient_boost': GradientBoostingRegressor(
                    n_estimators=100, 
                    random_state=42, 
                    max_depth=6
                ),
                'linear_regression': LinearRegression()
            }
            self._scaler = StandardScaler()
            debug_print("✅ ML models initialized successfully")
        except Exception as e:
            debug_print(f"⚠️  ML model initialization failed: {e}")
            self._ml_models = {}
    
    def _load_csv_training_data(self) -> pd.DataFrame:
        """Load training data from CSV file"""
        try:
            # CSV file is in source/ directory
            csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "stats_player_reg_2024.csv")
            
            if not os.path.exists(csv_path):
                debug_print(f"❌ CSV file not found at {csv_path}")
                return pd.DataFrame()
                
            df = pd.read_csv(csv_path)
            debug_print(f"✅ Loaded {len(df)} player records from CSV")
            return df
        except Exception as e:
            debug_print(f"❌ Error loading CSV data: {e}")
            return pd.DataFrame()
    
    def _calculate_fantasy_points_from_csv(self, row) -> float:
        """Calculate fantasy points from CSV row data"""
        try:
            # Use existing fantasy_points_ppr column if available
            if 'fantasy_points_ppr' in row and pd.notna(row['fantasy_points_ppr']):
                return float(row['fantasy_points_ppr'])
            
            # Calculate manually if not available
            points = 0.0
            
            # Passing stats
            points += row.get('passing_yards', 0) * self.scoring.get('passing_yards', 0)
            points += row.get('passing_tds', 0) * self.scoring.get('passing_tds', 0)
            points += row.get('passing_interceptions', 0) * self.scoring.get('interceptions', 0)
            
            # Rushing stats
            points += row.get('rushing_yards', 0) * self.scoring.get('rushing_yards', 0)
            points += row.get('rushing_tds', 0) * self.scoring.get('rushing_tds', 0)
            
            # Receiving stats
            points += row.get('receiving_yards', 0) * self.scoring.get('receiving_yards', 0)
            points += row.get('receiving_tds', 0) * self.scoring.get('receiving_tds', 0)
            points += row.get('receptions', 0) * self.scoring.get('receptions', 0)
            
            # Other stats
            points += row.get('rushing_fumbles_lost', 0) * self.scoring.get('fumbles', 0)
            points += row.get('receiving_fumbles_lost', 0) * self.scoring.get('fumbles', 0)
            points += row.get('passing_2pt_conversions', 0) * self.scoring.get('two_point_conversions', 0)
            points += row.get('rushing_2pt_conversions', 0) * self.scoring.get('two_point_conversions', 0)
            points += row.get('receiving_2pt_conversions', 0) * self.scoring.get('two_point_conversions', 0)
            
            return points
        except Exception as e:
            debug_print(f"⚠️  Error calculating points for player: {e}")
            return 0.0

    def _create_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Create training data from CSV file for ML models"""
        if not ML_AVAILABLE:
            return np.array([]), np.array([])
            
        # Load CSV data
        df = self._load_csv_training_data()
        if df.empty:
            debug_print("❌ No CSV data available, using fallback sample data")
            return self._create_fallback_training_data()
        
        # Filter for relevant positions and players with sufficient games
        relevant_positions = ['QB', 'RB', 'WR', 'TE']
        df_filtered = df[
            (df['position'].isin(relevant_positions)) & 
            (df['games'] >= 8) &  # At least 8 games played
            (pd.notna(df['fantasy_points_ppr']))  # Has fantasy points data
        ].copy()
        
        if len(df_filtered) < 50:
            debug_print(f"⚠️  Only {len(df_filtered)} players meet criteria, using fallback data")
            return self._create_fallback_training_data()
        
        debug_print(f"📊 Using {len(df_filtered)} players for training")
        
        features = []
        targets = []
        
        position_encoding = {"QB": 1, "RB": 2, "WR": 3, "TE": 4, "K": 5, "DEF": 6}
        
        for _, row in df_filtered.iterrows():
            try:
                games = max(row.get('games', 1), 1)
                
                # Create feature vector
                feature_row = [
                    row.get('passing_yards', 0) / games,      # passing_yards_per_game
                    row.get('passing_tds', 0) / games,        # passing_tds_per_game
                    row.get('passing_interceptions', 0) / games,  # interceptions_per_game
                    row.get('rushing_yards', 0) / games,      # rushing_yards_per_game
                    row.get('rushing_tds', 0) / games,        # rushing_tds_per_game
                    row.get('receiving_yards', 0) / games,    # receiving_yards_per_game
                    row.get('receiving_tds', 0) / games,      # receiving_tds_per_game
                    row.get('receptions', 0) / games,         # receptions_per_game
                    (row.get('rushing_fumbles_lost', 0) + row.get('receiving_fumbles_lost', 0)) / games,  # fumbles_per_game
                    (row.get('passing_2pt_conversions', 0) + row.get('rushing_2pt_conversions', 0) + row.get('receiving_2pt_conversions', 0)) / games,  # two_point_conversions_per_game
                    games,  # games_played
                    position_encoding.get(row.get('position', 'OTHER'), 0)  # position_encoded
                ]
                
                # Calculate fantasy points per game
                total_points = self._calculate_fantasy_points_from_csv(row)
                points_per_game = total_points / games
                
                features.append(feature_row)
                targets.append(points_per_game)
                
            except Exception as e:
                debug_print(f"⚠️  Skipping player due to error: {e}")
                continue
        
        debug_print(f"✅ Created training data: {len(features)} samples")
        return np.array(features), np.array(targets)
    
    def _create_fallback_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Fallback training data using sample players"""
        training_players = [
            # QBs
            {"name": "Josh Allen", "position": "QB", "passing_yards": 4306, "passing_tds": 29, "interceptions": 14, "rushing_yards": 524, "rushing_tds": 8, "receiving_yards": 0, "receiving_tds": 0, "receptions": 0, "fumbles": 3, "two_point_conversions": 0, "games_played": 17, "actual_points": 392.24},
            {"name": "Lamar Jackson", "position": "QB", "passing_yards": 3678, "passing_tds": 24, "interceptions": 7, "rushing_yards": 821, "rushing_tds": 5, "receiving_yards": 0, "receiving_tds": 0, "receptions": 0, "fumbles": 4, "two_point_conversions": 1, "games_played": 16, "actual_points": 309.12},
            {"name": "Patrick Mahomes", "position": "QB", "passing_yards": 4183, "passing_tds": 27, "interceptions": 14, "rushing_yards": 358, "rushing_tds": 4, "receiving_yards": 0, "receiving_tds": 0, "receptions": 0, "fumbles": 2, "two_point_conversions": 0, "games_played": 16, "actual_points": 335.32},
            # RBs
            {"name": "Christian McCaffrey", "position": "RB", "passing_yards": 0, "passing_tds": 0, "interceptions": 0, "rushing_yards": 1459, "rushing_tds": 14, "receiving_yards": 564, "receiving_tds": 2, "receptions": 67, "fumbles": 2, "two_point_conversions": 0, "games_played": 16, "actual_points": 355.3},
            {"name": "Austin Ekeler", "position": "RB", "passing_yards": 0, "passing_tds": 0, "interceptions": 0, "rushing_yards": 915, "rushing_tds": 12, "receiving_yards": 722, "receiving_tds": 8, "receptions": 107, "fumbles": 1, "two_point_conversions": 0, "games_played": 17, "actual_points": 353.7},
            # WRs  
            {"name": "Cooper Kupp", "position": "WR", "passing_yards": 0, "passing_tds": 0, "interceptions": 0, "rushing_yards": 0, "rushing_tds": 0, "receiving_yards": 1947, "receiving_tds": 16, "receptions": 145, "fumbles": 1, "two_point_conversions": 0, "games_played": 16, "actual_points": 433.7},
            {"name": "Stefon Diggs", "position": "WR", "passing_yards": 0, "passing_tds": 0, "interceptions": 0, "rushing_yards": 0, "rushing_tds": 0, "receiving_yards": 1183, "receiving_tds": 8, "receptions": 107, "fumbles": 1, "two_point_conversions": 0, "games_played": 17, "actual_points": 273.3},
            # TEs
            {"name": "Travis Kelce", "position": "TE", "passing_yards": 0, "passing_tds": 0, "interceptions": 0, "rushing_yards": 0, "rushing_tds": 0, "receiving_yards": 984, "receiving_tds": 5, "receptions": 93, "fumbles": 0, "two_point_conversions": 1, "games_played": 17, "actual_points": 191.4},
        ]
        
        features = []
        targets = []
        position_encoding = {"QB": 1, "RB": 2, "WR": 3, "TE": 4, "K": 5, "DEF": 6}
        
        for player in training_players:
            games = max(player['games_played'], 1)
            feature_row = [
                player['passing_yards'] / games,
                player['passing_tds'] / games,
                player['interceptions'] / games,
                player['rushing_yards'] / games,
                player['rushing_tds'] / games,
                player['receiving_yards'] / games,
                player['receiving_tds'] / games,
                player['receptions'] / games,
                player['fumbles'] / games,
                player['two_point_conversions'] / games,
                player['games_played'],
                position_encoding.get(player['position'], 0)
            ]
            
            features.append(feature_row)
            targets.append(player['actual_points'] / games)
            
        return np.array(features), np.array(targets)
        features = []
        targets = []
        
        position_encoding = {"QB": 1, "RB": 2, "WR": 3, "TE": 4, "K": 5, "DEF": 6}
        
        for player in training_players:
            # Calculate per-game stats
            games = max(player['games_played'], 1)
            feature_row = [
                player['passing_yards'] / games,      # passing_yards_per_game
                player['passing_tds'] / games,        # passing_tds_per_game
                player['interceptions'] / games,      # interceptions_per_game
                player['rushing_yards'] / games,      # rushing_yards_per_game
                player['rushing_tds'] / games,        # rushing_tds_per_game
                player['receiving_yards'] / games,    # receiving_yards_per_game
                player['receiving_tds'] / games,      # receiving_tds_per_game
                player['receptions'] / games,         # receptions_per_game
                player['fumbles'] / games,            # fumbles_per_game
                player['two_point_conversions'] / games,  # two_point_conversions_per_game
                player['games_played'],               # games_played
                position_encoding.get(player['position'], 0)  # position_encoded
            ]
            
            features.append(feature_row)
            targets.append(player['actual_points'] / games)  # Points per game
            
        return np.array(features), np.array(targets)
    
    def train_ml_models(self) -> bool:
        """Train machine learning models using sample data"""
        if not ML_AVAILABLE:
            debug_print("❌ ML libraries not available")
            return False
            
        if not self._ml_models:
            debug_print("❌ ML models not initialized")
            return False
            
        try:
            debug_print("🤖 Training ML models...")
            
            # Get training data
            X, y = self._create_training_data()
            
            if len(X) == 0:
                debug_print("❌ No training data available")
                return False
                
            # Split data for validation
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self._scaler.fit_transform(X_train)
            X_test_scaled = self._scaler.transform(X_test)
            
            # Train each model
            model_scores = {}
            for name, model in self._ml_models.items():
                debug_print(f"   🔄 Training {name}...")
                
                # Train model
                if name == 'linear_regression':
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Calculate accuracy metrics
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                
                model_scores[name] = {'mae': mae, 'mse': mse}
                debug_print(f"   ✅ {name}: MAE={mae:.2f}, MSE={mse:.2f}")
            
            debug_print("✅ ML models trained successfully")
            return True
            
        except Exception as e:
            debug_print(f"❌ ML training failed: {e}")
            return False
    
    def calculate_ml_projection(self, player_stats: PlayerStats, games_to_project: int = 1) -> Optional[PlayerProjection]:
        """Calculate projection using machine learning models"""
        if not ML_AVAILABLE or not self._ml_models:
            return None
            
        try:
            # Prepare features
            games = max(player_stats.games_played, 1)
            position_encoding = {"QB": 1, "RB": 2, "WR": 3, "TE": 4, "K": 5, "DEF": 6}
            
            features = np.array([[
                player_stats.passing_yards / games,
                player_stats.passing_tds / games,
                player_stats.interceptions / games,
                player_stats.rushing_yards / games,
                player_stats.rushing_tds / games,
                player_stats.receiving_yards / games,
                player_stats.receiving_tds / games,
                player_stats.receptions / games,
                player_stats.fumbles / games,
                player_stats.two_point_conversions / games,
                player_stats.games_played,
                position_encoding.get(player_stats.position, 0)
            ]])
            
            # Get predictions from all models
            predictions = {}
            for name, model in self._ml_models.items():
                if name == 'linear_regression':
                    if self._scaler is not None:
                        features_scaled = self._scaler.transform(features)
                        pred = model.predict(features_scaled)[0]
                    else:
                        pred = model.predict(features)[0]
                else:
                    pred = model.predict(features)[0]
                    
                predictions[name] = pred * games_to_project
            
            # Ensemble prediction (weighted average)
            weights = {'random_forest': 0.4, 'gradient_boost': 0.4, 'linear_regression': 0.2}
            ensemble_prediction = sum(predictions[name] * weights.get(name, 0.33) for name in predictions.keys())
            
            # Calculate confidence based on model agreement
            pred_values = list(predictions.values())
            std_dev = np.std(pred_values)
            confidence = max(0.5, min(1.0, 1.0 - (std_dev / np.mean(pred_values))))
            
            # Create scoring breakdown (approximated from traditional method)
            traditional_projection = self.calculate_projection_from_stats(player_stats, games_to_project)
            
            return PlayerProjection(
                player_name=player_stats.player_name,
                position=player_stats.position,
                team=player_stats.team,
                projected_points=round(ensemble_prediction, 2),
                confidence=round(confidence, 2),
                week=self.current_week,
                season=self.current_season,
                scoring_breakdown=traditional_projection.scoring_breakdown if traditional_projection else {},
                data_source="ML Models (RF+GB+LR)",
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
        except Exception as e:
            print(f"❌ ML projection failed: {e}")
            return None
    
    def train_ml_models(self) -> bool:
        """Train machine learning models using CSV data"""
        if not ML_AVAILABLE:
            debug_print("❌ ML libraries not available")
            return False
            
        if not self._ml_models:
            debug_print("❌ ML models not initialized")
            return False
            
        try:
            debug_print("🤖 Training ML models...")
            
            # Get training data from CSV
            X, y = self._create_training_data()
            
            if len(X) == 0:
                debug_print("❌ No training data available")
                return False
                
            debug_print(f"📊 Training with {len(X)} samples")
            
            # Split data for validation
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self._scaler.fit_transform(X_train)
            X_test_scaled = self._scaler.transform(X_test)
            
            # Train each model
            model_scores = {}
            for name, model in self._ml_models.items():
                debug_print(f"   🔄 Training {name}...")
                
                # Train model
                if name == 'linear_regression':
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Calculate accuracy metrics
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                
                model_scores[name] = {'mae': mae, 'mse': mse}
                debug_print(f"   ✅ {name}: MAE={mae:.2f}, MSE={mse:.2f}")
            
            debug_print("✅ ML models trained successfully")
            return True
            
        except Exception as e:
            debug_print(f"❌ ML training failed: {e}")
            return False
    
    def calculate_ml_projection(self, player_stats: PlayerStats, games_to_project: int = 1) -> Optional[PlayerProjection]:
        """Calculate projection using machine learning models"""
        if not ML_AVAILABLE or not self._ml_models:
            return None
            
        try:
            # Prepare features based on position
            games = max(player_stats.games_played, 1)
            position_encoding = {"QB": 1, "RB": 2, "WR": 3, "TE": 4, "K": 5, "DEF": 6}
            
            if player_stats.position == "DEF":
                # For defense, use defense-specific features
                features = np.array([[
                    0,  # passing_yards_per_game (not applicable)
                    0,  # passing_tds_per_game (not applicable)
                    0,  # interceptions_per_game (not applicable)
                    0,  # rushing_yards_per_game (not applicable)
                    0,  # rushing_tds_per_game (not applicable)
                    0,  # receiving_yards_per_game (not applicable)
                    0,  # receiving_tds_per_game (not applicable)
                    0,  # receptions_per_game (not applicable)
                    0,  # fumbles_per_game (not applicable)
                    0,  # two_point_conversions_per_game (not applicable)
                    player_stats.games_played,
                    position_encoding.get(player_stats.position, 6)
                ]])
                
                # For DEF, use traditional calculation since we don't have training data yet
                return self.calculate_projection_from_stats(player_stats, games_to_project)
            else:
                # For offensive players, use standard features
                features = np.array([[
                    player_stats.passing_yards / games,
                    player_stats.passing_tds / games,
                    player_stats.interceptions / games,
                    player_stats.rushing_yards / games,
                    player_stats.rushing_tds / games,
                    player_stats.receiving_yards / games,
                    player_stats.receiving_tds / games,
                    player_stats.receptions / games,
                    player_stats.fumbles / games,
                    player_stats.two_point_conversions / games,
                    player_stats.games_played,
                    position_encoding.get(player_stats.position, 0)
                ]])
            
            # Get predictions from all models
            predictions = {}
            for name, model in self._ml_models.items():
                if name == 'linear_regression':
                    if self._scaler is not None:
                        features_scaled = self._scaler.transform(features)
                        pred = model.predict(features_scaled)[0]
                    else:
                        pred = model.predict(features)[0]
                else:
                    pred = model.predict(features)[0]
                    
                predictions[name] = pred * games_to_project
            
            # Ensemble prediction (weighted average)
            weights = {'random_forest': 0.4, 'gradient_boost': 0.4, 'linear_regression': 0.2}
            ensemble_prediction = sum(predictions[name] * weights.get(name, 0.33) for name in predictions.keys())
            
            # Calculate confidence based on model agreement
            pred_values = list(predictions.values())
            std_dev = np.std(pred_values)
            confidence = max(0.5, min(1.0, 1.0 - (std_dev / np.mean(pred_values))))
            
            # Create scoring breakdown (approximated from traditional method)
            traditional_projection = self.calculate_projection_from_stats(player_stats, games_to_project)
            
            return PlayerProjection(
                player_name=player_stats.player_name,
                position=player_stats.position,
                team=player_stats.team,
                projected_points=round(ensemble_prediction, 2),
                confidence=round(confidence, 2),
                week=self.current_week,
                season=self.current_season,
                scoring_breakdown=traditional_projection.scoring_breakdown if traditional_projection else {},
                data_source="ML Models (RF+GB+LR)",
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
        except Exception as e:
            print(f"❌ ML projection failed: {e}")
            return None

    def connect_yahoo_api(self, oauth) -> bool:
        """
        Connect to Yahoo Fantasy API using provided OAuth
        
        Args:
            oauth: Yahoo OAuth object (already authenticated)
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not YAHOO_API_AVAILABLE:
            debug_print("❌ yahoo_fantasy_api package not available")
            debug_print("   Install with: pip install yahoo_fantasy_api")
            return False
            
        try:
            # Get current NFL game
            gm = yfa.Game(oauth, 'nfl')
            
            # Get the game ID
            game_id = gm.game_id()
            
            # Try to get league IDs for this user
            league_ids = gm.league_ids(year=2024)
            
            # Store the game object - we'll need a league for most operations
            self._yahoo_nfl = gm
            self._game_id = game_id
            self._oauth = oauth
            self._league_ids = league_ids
            
            debug_print(f"✅ Successfully connected to Yahoo Fantasy NFL API (Game ID: {game_id})")
            if league_ids:
                debug_print(f"   Found {len(league_ids)} league(s): {league_ids}")
            else:
                debug_print("   ⚠️  No leagues found - some features may be limited")
            
            return True
        except Exception as e:
            debug_print(f"❌ Failed to connect to Yahoo API: {e}")
            self._yahoo_nfl = None
            return False
    
    def get_yahoo_player_stats(self, player_name: str) -> Optional[PlayerStats]:
        """
        Get player statistics from Yahoo Fantasy API
        
        Uses the correct Yahoo Fantasy API methods: Game -> League -> player_details() and player_stats()
        
        Args:
            player_name (str): Name of the NFL player or team (will auto-detect defenses)
            
        Returns:
            Optional[PlayerStats]: Player statistics or None if not found
        """
        if not YAHOO_API_AVAILABLE:
            debug_print("❌ yahoo_fantasy_api package not available")
            debug_print("   Use get_sample_projection() for testing instead")
            return None
            
        if not self._yahoo_nfl:
            debug_print("❌ Yahoo API not connected. Use connect_yahoo_api() first.")
            return None
        
        # Handle defense team name variations - Yahoo API expects just city names, not "city DEF"
        defense_mappings = {
            "San Francisco": "San Francisco",
            "SF": "San Francisco", 
            "49ers": "San Francisco",
            "Pittsburgh": "Pittsburgh",
            "PIT": "Pittsburgh",
            "Steelers": "Pittsburgh",
            "Baltimore": "Baltimore",
            "BAL": "Baltimore",
            "Ravens": "Baltimore",
            "Buffalo": "Buffalo",
            "BUF": "Buffalo",
            "Bills": "Buffalo",
            "Kansas City": "Kansas City",
            "KC": "Kansas City",
            "Chiefs": "Kansas City"
        }
        
        # Check if this might be a defense search
        search_name = player_name
        if player_name in defense_mappings:
            search_name = defense_mappings[player_name]
            debug_print(f"🏈 Searching for defense: {search_name}")
        elif "DEF" in player_name.upper():
            # Remove "DEF" for Yahoo API search
            search_name = player_name.replace(" DEF", "").replace("DEF", "").strip()
            debug_print(f"🏈 Removed DEF for Yahoo search: {search_name}")
        elif any(team in player_name for team in defense_mappings.keys()):
            search_name = defense_mappings.get(player_name, player_name)
            debug_print(f"🏈 Auto-detected defense search: {search_name}")
        
        try:
            debug_print(f"🔍 Searching Yahoo for {search_name}...")
            
            # We need a league to search for players
            if not hasattr(self, '_league_ids') or not self._league_ids:
                debug_print("❌ No leagues found. Yahoo Fantasy API requires league access for player search.")
                debug_print("💡 You need to be in an active Yahoo Fantasy league to search players")
                debug_print("💡 Try using get_sample_projection() for testing instead")
                return None
            
            # Use the first available league
            league_id = self._league_ids[0]
            league = self._yahoo_nfl.to_league(league_id)
            self.current_week = 17 # league.current_week()
            debug_print(f"CURRENT WEEK: {self.current_week}") #####################################
            
            debug_print(f"   🔄 Using league {league_id} to search for players...")
            
            # Use player_details() to search for the player by name
            try:
                player_results = league.player_details(search_name)
                
                if not player_results:
                    debug_print(f"❌ No players found matching '{search_name}'")
                    debug_print("💡 Try using the exact player name as it appears in Yahoo Fantasy")
                    debug_print("💡 Or use get_sample_projection() for testing")
                    return None
                
                # Find the best match
                target_player = None
                for player in player_results:
                    full_name = player.get('name', {}).get('full', '')
                    if search_name.lower() in full_name.lower():
                        target_player = player
                        break
                
                if not target_player:
                    target_player = player_results[0]  # Use first result if no exact match
                
                player_id = int(target_player.get('player_id', 0))
                full_name = target_player.get('name', {}).get('full', search_name)
                
                debug_print(f"   ✅ Found {full_name} (ID: {player_id})")
                
                # Get player stats using player_stats() method
                debug_print(f"   🔄 Getting stats for {full_name}...")
                stats_data = league.player_stats([player_id], 'season')
                
                if not stats_data or len(stats_data) == 0:
                    debug_print(f"❌ No stats available for {full_name}")
                    return None
                
                # Parse Yahoo stats into our PlayerStats format
                return self._parse_yahoo_stats(target_player, stats_data[0])
                
            except Exception as e:
                debug_print(f"   ⚠️  Player search failed: {e}")
                debug_print("💡 Try using get_sample_projection() for testing")
                return None
            
        except Exception as e:
            debug_print(f"❌ Error with Yahoo API for {search_name}: {e}")
            debug_print(f"💡 Yahoo Fantasy API requires active league participation")
            debug_print(f"💡 Consider using sample data: get_sample_projection('{player_name}')")
            return None
    
    def _parse_yahoo_stats(self, player_info: Dict, stats_data: Dict) -> PlayerStats:
        """
        Parse Yahoo Fantasy API stats into PlayerStats object
        
        Args:
            player_info (Dict): Player information from Yahoo (from player_details)
            stats_data (Dict): Player statistics from Yahoo (from player_stats)
            
        Returns:
            PlayerStats: Parsed player statistics
        """
        # Extract basic player information
        name_obj = player_info.get('name', {})
        if isinstance(name_obj, dict):
            player_name = name_obj.get('full', 'Unknown')
        else:
            player_name = str(name_obj)
            
        player_id = str(player_info.get('player_id', ''))
        
        # Get position and team info
        position = 'UNKNOWN'
        team = 'UNKNOWN'
        
        # Extract position from eligible_positions
        eligible_positions = player_info.get('eligible_positions', [])
        if eligible_positions:
            if isinstance(eligible_positions, list) and len(eligible_positions) > 0:
                first_pos = eligible_positions[0]
                if isinstance(first_pos, dict):
                    position = first_pos.get('position', 'UNKNOWN')
                else:
                    position = str(first_pos)
            elif isinstance(eligible_positions, dict):
                position = eligible_positions.get('position', 'UNKNOWN')
        
        # Get team abbreviation
        team = player_info.get('editorial_team_abbr', 'UNKNOWN')
        
        # Initialize stats object
        stats = PlayerStats(
            player_name=player_name,
            player_id=player_id,
            position=position,
            team=team,
            games_played=self.current_week - 1 if self.current_week > 1 else 1
        )
        
        # Parse stats from the player_stats() response
        # The format is different from what was assumed before
        debug_print(f"   🔍 Parsing stats for {player_name}...")
        
        # Yahoo Fantasy API returns stats as direct key-value pairs in the stats_data dict
        # Common NFL stat abbreviations in Yahoo Fantasy (updated based on actual API response):
        yahoo_stat_mapping = {
            # Offensive stats
            'Pass Yds': 'passing_yards',       # Passing Yards
            'Pass TD': 'passing_tds',          # Passing Touchdowns
            'Rush Yds': 'rushing_yards',      # Rushing Yards
            'Rush TD': 'rushing_tds',         # Rushing Touchdowns
            'Rec': 'receptions',              # Receptions
            'Rec Yds': 'receiving_yards',     # Receiving Yards
            'Rec TD': 'receiving_tds',        # Receiving Touchdowns
            'Fum Lost': 'fumbles',            # Fumbles Lost
            '2PT': 'two_point_conversions',   # 2-Point Conversions
            # Defense stats (corrected based on actual API response)
            'Sack': 'def_sacks',              # Sacks
            'Fum Rec': 'def_fumbles_recovered',  # Fumble Recoveries
            'TD': 'def_tds',                  # Defensive Touchdowns
            'Safety': 'def_safeties',         # Safeties
            'Blk Kick': 'def_blocked_kicks',  # Blocked Kicks
            'Pts Allow': 'def_points_allowed',  # Points Allowed
            # Points allowed brackets (match exact API response)
            'Pts Allow 0': 'def_points_allowed_0',
            'Pts Allow 1-6': 'def_points_allowed_1_6',
            'Pts Allow 7-13': 'def_points_allowed_7_13',
            'Pts Allow 14-20': 'def_points_allowed_14_20',
            'Pts Allow 21-27': 'def_points_allowed_21_27',
            'Pts Allow 28-34': 'def_points_allowed_28_34',
            'Pts Allow 35+': 'def_points_allowed_35_plus'
        }
        
        # Handle "Int" stat which means different things for offense vs defense
        if 'Int' in stats_data:
            try:
                int_value = float(stats_data['Int'])
                if position == 'DEF':
                    stats.def_interceptions = int_value
                    debug_print(f"   📊 Int: {int_value} (defense)")
                else:
                    stats.interceptions = int_value
                    debug_print(f"   📊 Int: {int_value} (offense)")
            except (ValueError, TypeError):
                debug_print(f"   ⚠️  Invalid value for Int: {stats_data['Int']}")
        
        # Parse the stats from the response
        for yahoo_stat, our_field in yahoo_stat_mapping.items():
            if yahoo_stat in stats_data:
                try:
                    value = float(stats_data[yahoo_stat])
                    setattr(stats, our_field, value)
                    if value > 0:  # Only show non-zero stats
                        debug_print(f"   📊 {yahoo_stat}: {value}")
                except (ValueError, TypeError):
                    debug_print(f"   ⚠️  Invalid value for {yahoo_stat}: {stats_data[yahoo_stat]}")
        
        # Also check for any other numeric stats that might be relevant
        for key, value in stats_data.items():
            if key not in yahoo_stat_mapping and key != 'Int' and isinstance(value, (int, float)) and value > 0:
                debug_print(f"   📋 {key}: {value} (not mapped to projections)")
        
        return stats
    
    def calculate_projection_from_stats(self, player_stats: PlayerStats, 
                                      games_to_project: int = 1) -> PlayerProjection:
        """
        Calculate fantasy projection from player statistics
        
        Args:
            player_stats (PlayerStats): Player's season statistics
            games_to_project (int): Number of games to project (default: 1)
            
        Returns:
            PlayerProjection: Calculated fantasy projection
        """
        if player_stats.games_played == 0:
            return PlayerProjection(
                player_name=player_stats.player_name,
                position=player_stats.position,
                team=player_stats.team,
                projected_points=0.0,
                confidence=0.0,
                week=self.current_week,
                season=self.current_season,
                scoring_breakdown={},
                data_source="Yahoo Fantasy API",
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        
        # Calculate per-game averages
        games = max(player_stats.games_played, 1)
        
        if player_stats.position == "DEF":
            # For defense, calculate different stats
            per_game_stats = {
                'def_sacks': player_stats.def_sacks / games,
                'def_interceptions': player_stats.def_interceptions / games,
                'def_fumbles_recovered': player_stats.def_fumbles_recovered / games,
                'def_tds': player_stats.def_tds / games,
                'def_safeties': player_stats.def_safeties / games,
                'def_blocked_kicks': player_stats.def_blocked_kicks / games,
            }
            
            # Use actual points allowed bracket data from Yahoo API if available
            # These represent the number of games in each bracket, so we need to convert to per-game probabilities
            total_bracket_games = (player_stats.def_points_allowed_0 + 
                                 player_stats.def_points_allowed_1_6 + 
                                 player_stats.def_points_allowed_7_13 + 
                                 player_stats.def_points_allowed_14_20 + 
                                 player_stats.def_points_allowed_21_27 + 
                                 player_stats.def_points_allowed_28_34 + 
                                 player_stats.def_points_allowed_35_plus)
            
            if total_bracket_games > 0:
                # Use actual bracket data (convert to per-game probabilities)
                per_game_stats['def_points_allowed_0'] = player_stats.def_points_allowed_0 / total_bracket_games
                per_game_stats['def_points_allowed_1_6'] = player_stats.def_points_allowed_1_6 / total_bracket_games
                per_game_stats['def_points_allowed_7_13'] = player_stats.def_points_allowed_7_13 / total_bracket_games
                per_game_stats['def_points_allowed_14_20'] = player_stats.def_points_allowed_14_20 / total_bracket_games
                per_game_stats['def_points_allowed_21_27'] = player_stats.def_points_allowed_21_27 / total_bracket_games
                per_game_stats['def_points_allowed_28_34'] = player_stats.def_points_allowed_28_34 / total_bracket_games
                per_game_stats['def_points_allowed_35_plus'] = player_stats.def_points_allowed_35_plus / total_bracket_games
            else:
                # Fallback: estimate based on total points allowed
                points_allowed_per_game = player_stats.def_points_allowed / games if player_stats.def_points_allowed > 0 else 21  # Default to league average
                
                # Determine points allowed bracket (this is a simplified estimation)
                if points_allowed_per_game == 0:
                    per_game_stats['def_points_allowed_0'] = 1
                elif points_allowed_per_game <= 6:
                    per_game_stats['def_points_allowed_1_6'] = 1
                elif points_allowed_per_game <= 13:
                    per_game_stats['def_points_allowed_7_13'] = 1
                elif points_allowed_per_game <= 20:
                    per_game_stats['def_points_allowed_14_20'] = 1
                elif points_allowed_per_game <= 27:
                    per_game_stats['def_points_allowed_21_27'] = 1
                elif points_allowed_per_game <= 34:
                    per_game_stats['def_points_allowed_28_34'] = 1
                else:
                    per_game_stats['def_points_allowed_35_plus'] = 1
        else:
            # For offensive players
            per_game_stats = {
                'passing_yards': player_stats.passing_yards / games,
                'passing_tds': player_stats.passing_tds / games,
                'interceptions': player_stats.interceptions / games,
                'rushing_yards': player_stats.rushing_yards / games,
                'rushing_tds': player_stats.rushing_tds / games,
                'receiving_yards': player_stats.receiving_yards / games,
                'receiving_tds': player_stats.receiving_tds / games,
                'receptions': player_stats.receptions / games,
                'fumbles': player_stats.fumbles / games,
                'two_point_conversions': player_stats.two_point_conversions / games
            }
        
        # Apply position-based adjustments
        adjusted_stats = self._apply_position_adjustments(per_game_stats, player_stats.position)
        
        # Calculate fantasy points
        scoring_breakdown = {}
        total_points = 0.0
        
        for stat_name, per_game_value in adjusted_stats.items():
            if stat_name in self.scoring and per_game_value > 0:
                # points_per_game = per_game_value * self.scoring[stat_name]
                # projected_points = points_per_game * games_to_project
                # scoring_breakdown[stat_name] = round(projected_points, 2)
                # total_points += projected_points
                points_per_game = per_game_value * self.scoring[stat_name]
                projected_points = points_per_game * games_to_project
                scoring_breakdown[stat_name] = round(projected_points, 2)
                total_points += projected_points
        
        # Calculate confidence score
        confidence = self._calculate_confidence(player_stats)
        
        return PlayerProjection(
            player_name=player_stats.player_name,
            position=player_stats.position,
            team=player_stats.team,
            projected_points=round(total_points, 2),
            confidence=confidence,
            week=self.current_week,
            season=self.current_season,
            scoring_breakdown=scoring_breakdown,
            data_source="Yahoo Fantasy API",
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _apply_position_adjustments(self, stats: Dict[str, float], position: str) -> Dict[str, float]:
        """
        Apply position-specific adjustments for projections
        
        Args:
            stats (Dict[str, float]): Per-game statistics
            position (str): Player position
            
        Returns:
            Dict[str, float]: Adjusted statistics
        """
        adjusted_stats = stats.copy()
        
        # Position-specific multipliers based on trends and matchups
        if position == "QB":
            # QBs may have slight variance in performance
            pass
        elif position == "RB":
            # RBs might have more consistent rushing production
            adjusted_stats['rushing_yards'] *= 1.0
            adjusted_stats['rushing_tds'] *= 1.0
        elif position in ["WR", "TE"]:
            # WRs and TEs might have target-dependent variance
            adjusted_stats['receiving_yards'] *= 1.0
            adjusted_stats['receptions'] *= 1.0
        elif position == "DEF":
            # Defense adjustments based on strength of schedule, etc.
            # For now, keep as-is but could add matchup-based adjustments
            pass
        
        return adjusted_stats
    
    def _calculate_confidence(self, player_stats: PlayerStats) -> float:
        """
        Calculate confidence score for projections (0.0 to 1.0)
        
        Args:
            player_stats (PlayerStats): Player statistics
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        # Base confidence on games played (more games = higher confidence)
        games_confidence = min(player_stats.games_played / 16, 1.0)
        
        # Position reliability factors
        position_confidence = {
            "QB": 0.85,
            "RB": 0.80,
            "WR": 0.75,
            "TE": 0.70,
            "K": 0.60,
            "DEF": 0.65
        }.get(player_stats.position, 0.70)
        
        # Overall confidence is weighted average
        confidence = (games_confidence * 0.6) + (position_confidence * 0.4)
        return round(confidence, 2)
    
    def get_yahoo_projection(self, oauth, player_name: str, use_ml: bool = True) -> Optional[PlayerProjection]:
        """
        Get fantasy projection for a player using Yahoo Fantasy API
        
        This method attempts to connect to Yahoo Fantasy API and retrieve player data.
        Yahoo API has limitations for general player search - it works best with
        league-specific access, but this method tries available endpoints.
        
        Args:
            oauth: Yahoo OAuth object (already authenticated)
            player_name (str): Name of the NFL player
            use_ml (bool): Whether to use ML models for projection (default: True)
            
        Returns:
            Optional[PlayerProjection]: Player projection or None if not found.
                                      Falls back to sample data if Yahoo API fails.
        """
        if not YAHOO_API_AVAILABLE:
            debug_print("❌ yahoo_fantasy_api package not available")
            debug_print("💡 Using sample data instead...")
            return self.get_sample_projection(player_name, use_ml=use_ml)
            
        # Connect to Yahoo API if not already connected
        if not self._yahoo_nfl:
            if not self.connect_yahoo_api(oauth):
                debug_print("💡 Falling back to sample data...")
                return self.get_sample_projection(player_name, use_ml=use_ml)
        
        # Get player stats from Yahoo
        player_stats = self.get_yahoo_player_stats(player_name)
        
        if not player_stats:
            debug_print("💡 Yahoo API search failed, trying sample data...")
            return self.get_sample_projection(player_name, use_ml=use_ml)
        
        # Calculate projection using ML if available and requested
        if use_ml and ML_AVAILABLE and self._ml_models:
            # Train models if not already trained
            if not hasattr(self, '_models_trained'):
                self.train_ml_models()
                self._models_trained = True
                
            ml_projection = self.calculate_ml_projection(player_stats)
            if ml_projection:
                debug_print(f"🤖 ML Projection: {ml_projection.projected_points} points")
                
                # Also calculate traditional projection for comparison
                traditional_projection = self.calculate_projection_from_stats(player_stats)
                debug_print(f"📊 Traditional Projection: {traditional_projection.projected_points} points")
                
                return ml_projection
        
        # Fall back to traditional projection
        projection = self.calculate_projection_from_stats(player_stats)
        return projection
    
    def get_sample_projection(self, player_name: str, use_ml: bool = True) -> Optional[PlayerProjection]:
        """
        Get fantasy projection using sample data (for testing)
        
        Args:
            player_name (str): Name of the NFL player
            use_ml (bool): Whether to use ML models for projection (default: True)
            
        Returns:
            Optional[PlayerProjection]: Player projection using sample data
        """
        # Sample player data for testing
        sample_players = {
            "Josh Allen": PlayerStats(
                player_name="Josh Allen",
                player_id="sample_001",
                position="QB",
                team="BUF",
                games_played=17,
                passing_yards=4306,
                passing_tds=29,
                interceptions=14,
                rushing_yards=524,
                rushing_tds=8,
                fumbles=3,
                two_point_conversions=0
            ),
            "Lamar Jackson": PlayerStats(
                player_name="Lamar Jackson", 
                player_id="sample_002",
                position="QB",
                team="BAL",
                games_played=16,
                passing_yards=3678,
                passing_tds=24,
                interceptions=7,
                rushing_yards=821,
                rushing_tds=5,
                fumbles=4,
                two_point_conversions=1
            ),
            "Christian McCaffrey": PlayerStats(
                player_name="Christian McCaffrey",
                player_id="sample_003",
                position="RB",
                team="SF",
                games_played=16,
                rushing_yards=1459,
                rushing_tds=14,
                receiving_yards=564,
                receiving_tds=2,
                receptions=67,
                fumbles=2,
                two_point_conversions=0
            ),
            "Cooper Kupp": PlayerStats(
                player_name="Cooper Kupp",
                player_id="sample_004",
                position="WR",
                team="LAR",
                games_played=16,
                receiving_yards=1947,
                receiving_tds=16,
                receptions=145,
                fumbles=1,
                two_point_conversions=0
            ),
            "Travis Kelce": PlayerStats(
                player_name="Travis Kelce",
                player_id="sample_005",
                position="TE",
                team="KC",
                games_played=17,
                receiving_yards=984,
                receiving_tds=5,
                receptions=93,
                fumbles=0,
                two_point_conversions=1
            ),
            "Stefon Diggs": PlayerStats(
                player_name="Stefon Diggs",
                player_id="sample_006",
                position="WR",
                team="HOU",
                games_played=17,
                receiving_yards=1183,
                receiving_tds=8,
                receptions=107,
                fumbles=1,
                two_point_conversions=0
            ),
            "San Francisco DEF": PlayerStats(
                player_name="San Francisco DEF",
                player_id="sample_007",
                position="DEF",
                team="SF",
                games_played=17,
                def_sacks=48.0,
                def_interceptions=17.0,
                def_fumbles_recovered=8.0,
                def_tds=3.0,
                def_safeties=1.0,
                def_blocked_kicks=2.0,
                def_points_allowed=18.5 * 17  # 18.5 points per game average
            ),
            "Pittsburgh DEF": PlayerStats(
                player_name="Pittsburgh DEF", 
                player_id="sample_008",
                position="DEF",
                team="PIT",
                games_played=17,
                def_sacks=38.0,
                def_interceptions=14.0,
                def_fumbles_recovered=6.0,
                def_tds=2.0,
                def_safeties=0.0,
                def_blocked_kicks=1.0,
                def_points_allowed=19.8 * 17  # 19.8 points per game average
            )
        }
        
        # Try exact match first
        player_stats = sample_players.get(player_name)
        
        # If no exact match and player_name doesn't contain "DEF", try adding "DEF"
        if not player_stats and "DEF" not in player_name.upper():
            defense_name = f"{player_name} DEF"
            player_stats = sample_players.get(defense_name)
            if player_stats:
                debug_print(f"🏈 Found defense: {defense_name}")
        
        # Also try common team name variations for defenses
        if not player_stats:
            # Try searching by team abbreviation and city names for defenses
            team_mappings = {
                "SF": "San Francisco DEF",
                "49ers": "San Francisco DEF", 
                "San Francisco": "San Francisco DEF",
                "PIT": "Pittsburgh DEF",
                "Steelers": "Pittsburgh DEF",
                "Pittsburgh": "Pittsburgh DEF",
                # Add more team mappings as needed
                "BAL": "Baltimore DEF",
                "Ravens": "Baltimore DEF",
                "Baltimore": "Baltimore DEF",
                "BUF": "Buffalo DEF", 
                "Bills": "Buffalo DEF",
                "Buffalo": "Buffalo DEF",
                "KC": "Kansas City DEF",
                "Chiefs": "Kansas City DEF",
                "Kansas City": "Kansas City DEF",
                "LAR": "Los Angeles DEF",
                "Rams": "Los Angeles DEF",
                "Los Angeles": "Los Angeles DEF"
            }
            
            mapped_name = team_mappings.get(player_name)
            if mapped_name:
                player_stats = sample_players.get(mapped_name)
                if player_stats:
                    debug_print(f"🏈 Found defense via mapping: {mapped_name}")
        
        if not player_stats:
            debug_print(f"❌ No sample data available for {player_name}")
            debug_print(f"💡 For defenses, try: 'San Francisco', 'Pittsburgh', 'SF', 'PIT'")
            debug_print(f"💡 For players, try: 'Josh Allen', 'Christian McCaffrey', etc.")
            return None
        
        # Calculate projection using ML if available and requested
        if use_ml and ML_AVAILABLE and self._ml_models:
            # Train models if not already trained
            if not hasattr(self, '_models_trained'):
                self.train_ml_models()
                self._models_trained = True
                
            ml_projection = self.calculate_ml_projection(player_stats)
            if ml_projection:
                ml_projection.data_source = "ML Models + Sample Data"
                debug_print(f"🤖 ML Projection: {ml_projection.projected_points} points")
                
                # Also calculate traditional projection for comparison
                traditional_projection = self.calculate_projection_from_stats(player_stats)
                traditional_projection.data_source = "Sample Data"
                debug_print(f"📊 Traditional Projection: {traditional_projection.projected_points} points")
                
                return ml_projection
        
        # Calculate projection using sample data (traditional method)
        projection = self.calculate_projection_from_stats(player_stats)
        projection.data_source = "Sample Data"
        
        return projection
    
    def bulk_projections(self, oauth, player_names: List[str], 
                        use_sample_data: bool = False) -> Dict[str, PlayerProjection]:
        """
        Get projections for multiple players
        
        Args:
            oauth: Yahoo OAuth object (already authenticated)
            player_names (List[str]): List of player names
            use_sample_data (bool): If True, use sample data instead of Yahoo API
            
        Returns:
            Dict[str, PlayerProjection]: Dictionary of player projections
        """
        projections = {}
        
        debug_print(f"🏈 Getting projections for {len(player_names)} players...")
        
        for i, player_name in enumerate(player_names, 1):
            debug_print(f"\n📊 Processing {i}/{len(player_names)}: {player_name}")
            
            if use_sample_data:
                projection = self.get_sample_projection(player_name)
            else:
                projection = self.get_yahoo_projection(oauth, player_name)
            
            if projection:
                projections[player_name] = projection
                debug_print(f"✅ {projection.projected_points} points projected")
            else:
                debug_print(f"❌ Failed to get projection")
            
            # Rate limiting for API calls
            if not use_sample_data:
                time.sleep(0.5)
        
        return projections
    
    def export_projections_to_csv(self, projections: Dict[str, PlayerProjection], 
                                 filename: str = None) -> str:
        """
        Export projections to CSV file
        
        Args:
            projections (Dict[str, PlayerProjection]): Player projections
            filename (str): Optional custom filename
            
        Returns:
            str: Path to exported CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nfl_projections_{timestamp}.csv"
        
        # Convert projections to DataFrame
        data = []
        for projection in projections.values():
            row = {
                'Player': projection.player_name,
                'Position': projection.position,
                'Team': projection.team,
                'Projected_Points': projection.projected_points,
                'Confidence': projection.confidence,
                'Week': projection.week,
                'Season': projection.season,
                'Data_Source': projection.data_source,
                'Last_Updated': projection.last_updated
            }
            
            # Add scoring breakdown
            for stat, points in projection.scoring_breakdown.items():
                row[f'{stat}_points'] = points
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Sort by projected points descending
        df = df.sort_values('Projected_Points', ascending=False)
        
        # Save to CSV
        filepath = f"c:\\Users\\acantu\\Desktop\\Projected Points\\{filename}"
        df.to_csv(filepath, index=False)
        
        debug_print(f"📄 Projections exported to: {filepath}")
        return filepath
    
    def get_projection_summary(self, projections: Dict[str, PlayerProjection]) -> Dict[str, any]:
        """
        Get summary statistics for a set of projections
        
        Args:
            projections (Dict[str, PlayerProjection]): Player projections
            
        Returns:
            Dict[str, any]: Summary statistics
        """
        if not projections:
            return {}
        
        points = [p.projected_points for p in projections.values()]
        confidence_scores = [p.confidence for p in projections.values()]
        
        # Get top scorer
        top_projection = max(projections.values(), key=lambda x: x.projected_points)
        
        # Group by position
        by_position = {}
        for projection in projections.values():
            pos = projection.position
            if pos not in by_position:
                by_position[pos] = []
            by_position[pos].append(projection.projected_points)
        
        summary = {
            'total_players': len(projections),
            'average_points': round(np.mean(points), 2),
            'median_points': round(np.median(points), 2),
            'max_points': round(max(points), 2),
            'min_points': round(min(points), 2),
            'average_confidence': round(np.mean(confidence_scores), 2),
            'top_scorer': {
                'name': top_projection.player_name,
                'position': top_projection.position,
                'points': top_projection.projected_points
            },
            'by_position': {pos: {
                'count': len(pts),
                'avg_points': round(np.mean(pts), 2)
            } for pos, pts in by_position.items()}
        }
        
        return summary


# Convenience functions for easy importing
def get_yahoo_projection(oauth, player_name: str, scoring_system: str = "ppr", use_ml: bool = True) -> Optional[PlayerProjection]:
    """
    Get a single player projection using Yahoo Fantasy API
    
    This function attempts to connect to Yahoo Fantasy API and retrieve player data.
    Yahoo API has limitations for general player search, but this function tries
    available endpoints and falls back to sample data if needed.
    
    Args:
        oauth: Yahoo OAuth object (already authenticated)
        player_name (str): Name of the NFL player
        scoring_system (str): Fantasy scoring system ("ppr", "half_ppr", "standard", "superflex")
        use_ml (bool): Whether to use ML models for projection (default: True)
        
    Returns:
        Optional[PlayerProjection]: Player projection from Yahoo API or sample data fallback
    """
    library = NFLProjectionsLibrary(scoring_system=scoring_system)
    return library.get_yahoo_projection(oauth, player_name, use_ml=use_ml)


def get_sample_projection(player_name: str, scoring_system: str = "ppr", use_ml: bool = True) -> Optional[PlayerProjection]:
    """
    Get a single player projection using sample data
    
    Args:
        player_name (str): Name of the NFL player
        scoring_system (str): Fantasy scoring system ("ppr", "half_ppr", "standard", "superflex")
        use_ml (bool): Whether to use ML models for projection (default: True)
        
    Returns:
        Optional[PlayerProjection]: Player projection using sample data
    """
    library = NFLProjectionsLibrary(scoring_system=scoring_system)
    return library.get_sample_projection(player_name, use_ml=use_ml)


def get_multiple_projections(oauth, player_names: List[str], scoring_system: str = "ppr", 
                           use_sample_data: bool = False) -> Dict[str, PlayerProjection]:
    """
    Get projections for multiple players
    
    Args:
        oauth: Yahoo OAuth object (already authenticated)
        player_names (List[str]): List of player names
        scoring_system (str): Fantasy scoring system ("ppr", "half_ppr", "standard", "superflex")
        use_sample_data (bool): If True, use sample data instead of Yahoo API
        
    Returns:
        Dict[str, PlayerProjection]: Dictionary of player projections
    """
    library = NFLProjectionsLibrary(scoring_system=scoring_system)
    return library.bulk_projections(oauth, player_names, use_sample_data)


def export_to_csv(projections: Dict[str, PlayerProjection], filename: str = None) -> str:
    """
    Export projections to CSV file
    
    Args:
        projections (Dict[str, PlayerProjection]): Player projections
        filename (str): Optional custom filename
        
    Returns:
        str: Path to exported CSV file
    """
    library = NFLProjectionsLibrary()
    return library.export_projections_to_csv(projections, filename)

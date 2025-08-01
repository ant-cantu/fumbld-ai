"""
Configuration file for NFL Player Projections
Customize scoring systems and other settings here
"""

# Fantasy Football Scoring Systems
SCORING_SYSTEMS = {
    "standard": {
        'passing_yards': 0.04,  # 1 point per 25 yards
        'passing_tds': 4,
        'interceptions': -2,
        'rushing_yards': 0.1,   # 1 point per 10 yards
        'rushing_tds': 6,
        'receiving_yards': 0.1, # 1 point per 10 yards
        'receiving_tds': 6,
        'receptions': 0,        # No PPR
        'fumbles': -2
    },
    
    "ppr": {
        'passing_yards': 0.04,  # 1 point per 25 yards
        'passing_tds': 4,
        'interceptions': -2,
        'rushing_yards': 0.1,   # 1 point per 10 yards
        'rushing_tds': 6,
        'receiving_yards': 0.1, # 1 point per 10 yards
        'receiving_tds': 6,
        'receptions': 1,        # Full PPR
        'fumbles': -2
    },
    
    "half_ppr": {
        'passing_yards': 0.04,  # 1 point per 25 yards
        'passing_tds': 4,
        'interceptions': -2,
        'rushing_yards': 0.1,   # 1 point per 10 yards
        'rushing_tds': 6,
        'receiving_yards': 0.1, # 1 point per 10 yards
        'receiving_tds': 6,
        'receptions': 0.5,      # Half PPR
        'fumbles': -2
    },
    
    "superflex": {
        'passing_yards': 0.04,  # 1 point per 25 yards
        'passing_tds': 6,       # Higher QB scoring
        'interceptions': -2,
        'rushing_yards': 0.1,   # 1 point per 10 yards
        'rushing_tds': 6,
        'receiving_yards': 0.1, # 1 point per 10 yards
        'receiving_tds': 6,
        'receptions': 1,        # Full PPR
        'fumbles': -2
    }
}

# API Configuration
API_CONFIG = {
    "espn_base_url": "http://sports.espn.com/nfl",
    "nfl_api_base": "https://api.nfl.com",
    "request_timeout": 10,
    "rate_limit_delay": 0.5,  # seconds between requests
    "cache_timeout": 3600     # 1 hour in seconds
}

# Team Abbreviations
NFL_TEAMS = {
    "ARI": "Arizona Cardinals",
    "ATL": "Atlanta Falcons", 
    "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills",
    "CAR": "Carolina Panthers",
    "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals",
    "CLE": "Cleveland Browns",
    "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos",
    "DET": "Detroit Lions",
    "GB": "Green Bay Packers",
    "HOU": "Houston Texans",
    "IND": "Indianapolis Colts",
    "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs",
    "LV": "Las Vegas Raiders",
    "LAC": "Los Angeles Chargers",
    "LAR": "Los Angeles Rams",
    "MIA": "Miami Dolphins",
    "MIN": "Minnesota Vikings",
    "NE": "New England Patriots",
    "NO": "New Orleans Saints",
    "NYG": "New York Giants",
    "NYJ": "New York Jets",
    "PHI": "Philadelphia Eagles",
    "PIT": "Pittsburgh Steelers",
    "SF": "San Francisco 49ers",
    "SEA": "Seattle Seahawks",
    "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans",
    "WAS": "Washington Commanders"
}

# Position Rankings (for confidence calculations)
POSITION_RELIABILITY = {
    "QB": 0.85,
    "RB": 0.80,
    "WR": 0.75,
    "TE": 0.70,
    "K": 0.60,
    "DST": 0.65
}

# Injury Impact Adjustments
INJURY_ADJUSTMENTS = {
    "questionable": 0.90,
    "doubtful": 0.30,
    "out": 0.0,
    "ir": 0.0,
    "healthy": 1.0
}

# Weather Impact (for outdoor games)
WEATHER_ADJUSTMENTS = {
    "clear": 1.0,
    "light_rain": 0.95,
    "heavy_rain": 0.85,
    "snow": 0.80,
    "high_wind": 0.90,
    "extreme_cold": 0.85
}

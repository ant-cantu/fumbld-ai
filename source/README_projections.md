# NFL Player Projections Generator

This script (`get_projections.py`) generates comprehensive NFL player projections using machine learning models trained on CSV data. It creates a detailed projections file that includes player statistics, injury status, and ML-generated fantasy point projections.

## Features

- **Comprehensive Player Coverage**: Extracts all players from CSV data files
- **ML-Powered Projections**: Uses trained machine learning models for accurate predictions
- **Injury Status Integration**: Includes current injury reports in projections
- **Season Statistics**: Provides complete season totals for each player
- **Smart Data Management**: Appends new data without overriding existing records
- **Duplicate Prevention**: Ignores matching data to prevent duplicates

## Output File Structure

The script creates `df_projected_points_[YEAR].csv` with the following columns:

### Core Information
- `player_name`: Full player name
- `position`: Player position (QB, RB, WR, TE, K, DEF)
- `team`: Current team
- `projected_points`: ML-generated fantasy point projection
- `confidence`: Confidence level of the projection (0-1)
- `injury_status`: Current injury status (Healthy, Out, Doubtful, etc.)

### Metadata
- `week`: Current NFL week
- `season`: Current NFL season year
- `scoring_system`: Fantasy scoring system used (e.g., "ppr")
- `data_source`: Source of the projection data
- `last_updated`: Timestamp of when projection was generated

### Offensive Player Stats (QB, RB, WR, TE)
- `games_played`: Games played this season
- `passing_yards`: Total passing yards
- `passing_tds`: Total passing touchdowns
- `interceptions`: Total interceptions thrown
- `rushing_yards`: Total rushing yards
- `rushing_tds`: Total rushing touchdowns
- `receiving_yards`: Total receiving yards
- `receiving_tds`: Total receiving touchdowns
- `receptions`: Total receptions
- `fumbles`: Total fumbles lost
- `two_point_conversions`: Total 2-point conversions

### Defense Stats (DEF)
- `games_played`: Games played this season
- `def_sacks`: Total sacks
- `def_interceptions`: Total interceptions
- `def_fumbles_recovered`: Total fumbles recovered
- `def_tds`: Total defensive touchdowns
- `def_safeties`: Total safeties
- `def_blocked_kicks`: Total blocked kicks
- `def_points_allowed`: Average points allowed per game

### Kicker Stats (K)
- `games_played`: Games played this season
- `fg_made`: Total field goals made
- `fg_attempts`: Total field goal attempts
- `fg_avg_distance`: Average field goal distance
- `fg_long`: Longest field goal made
- `xp_made`: Total extra points made

## Usage

### Basic Usage
```bash
cd /source/
python get_projections.py
```

### Programmatic Usage
```python
from get_projections import ProjectionsGenerator

# Initialize generator
generator = ProjectionsGenerator(scoring_system="ppr")

# Generate projections
generator.generate_all_projections(use_ml=True, force_update=False)
```

### Configuration Options

#### Scoring Systems
- `"ppr"`: Full Point Per Reception
- `"half_ppr"`: Half Point Per Reception  
- `"standard"`: Standard scoring (no PPR)
- `"superflex"`: Superflex league scoring

#### Generation Options
- `use_ml=True`: Use machine learning models (recommended)
- `use_ml=False`: Use statistical averages only
- `force_update=True`: Override existing projections
- `force_update=False`: Skip existing projections (default)

## Data Flow

1. **Data Extraction**: Reads player names from:
   - `df_weekly_[YEAR].csv` (offensive players)
   - `dst_stats_[YEAR].csv` (defense/special teams)
   - `kicker_stats_[YEAR].csv` (kickers)

2. **ML Processing**: For each player:
   - Runs through trained ML models
   - Calculates projection confidence
   - Handles injured players (sets to 0 points)

3. **Data Enrichment**: Adds:
   - Current injury status from `df_injury_[YEAR].csv`
   - Season statistics totals
   - Fantasy point projections

4. **Output Management**:
   - Creates new file if none exists
   - Appends to existing file
   - Prevents duplicate entries
   - Sorts by projected points (highest first)

## File Management

### Input Files Required
```
source/nfl_stats/data/
├── df_weekly_[YEAR].csv      # Weekly player stats
├── dst_stats_[YEAR].csv      # Defense/ST stats
├── kicker_stats_[YEAR].csv   # Kicker stats
├── df_injury_[YEAR].csv      # Injury reports
└── ml_models/                # Trained ML models
    ├── qb_model.pkl
    ├── rb_model.pkl
    ├── wr_model.pkl
    ├── te_model.pkl
    ├── def_model.pkl
    └── k_model.pkl
```

### Output File
```
source/
└── df_projected_points_[YEAR].csv  # Generated projections
```

## Example Output

```csv
player_name,position,team,projected_points,confidence,injury_status,week,season,games_played,rushing_yards,receiving_yards,...
Josh Allen,QB,BUF,24.5,0.92,Healthy,15,2024,14,524,12,...
Christian McCaffrey,RB,SF,22.1,0.88,Out,15,2024,13,1234,89,...
Cooper Kupp,WR,LAR,18.7,0.85,Doubtful,15,2024,12,45,1147,...
```

## Logging

The script provides detailed logging including:
- Number of players processed per position
- ML model training status
- Existing vs new projections
- Top projected players
- Error handling for missing data

Log files are saved as `projections_generation.log`.

## Error Handling

- **Missing CSV Files**: Warns but continues with available data
- **Player Not Found**: Logs warning and continues
- **ML Model Errors**: Falls back to statistical projections
- **Injury Data Missing**: Defaults to "Unknown" status
- **Duplicate Prevention**: Automatically handles existing records

## Dependencies

- pandas
- numpy
- pathlib
- logging
- nfl_projections_library (local module)

## Notes

- The script automatically detects the current NFL season and week
- ML models are trained automatically if not present
- Injury status is based on current week only
- Projections are sorted by highest projected points
- The script can be run multiple times safely (no data loss)
- Confidence scores range from 0.5 to 0.98 depending on position and data quality

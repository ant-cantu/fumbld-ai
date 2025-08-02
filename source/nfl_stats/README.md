# CSV Fantasy Projections Library

A pure CSV-based NFL fantasy football projections library with machine learning capabilities. This library uses only CSV data (no external APIs) and includes ML models that learn and improve over time.

## Features

- **Pure CSV Data Source**: Uses only your local CSV files from the `nfl_stats` folder
- **Full Position Support**: QB, RB, WR, TE, DEF/DST, and Kickers
- **Multiple Scoring Systems**: PPR, Half-PPR, Standard, and Superflex
- **Machine Learning**: ML models that learn from historical data and improve over time
- **Easy Defense Search**: Enter defenses by city name (e.g., "San Francisco" instead of "San Francisco DEF")
- **Daily Learning**: Models can be retrained with new data for continuous improvement

## Installation

Ensure you have the required dependencies:

```bash
pip install pandas numpy scikit-learn
```

## Quick Start

### Basic Usage

```python
from fumbld_ai.nfl_fantasy_projections.csv_projections_library import get_csv_projection, bulk_csv_projections

# Get a single player projection
projection = get_csv_projection("Aaron Rodgers", scoring_system="ppr", use_ml=True)
if projection:
    print(f"{projection.player_name}: {projection.projected_points:.2f} points")

# Get multiple projections
players = ["Aaron Rodgers", "Derrick Henry", "San Francisco", "Justin Tucker"]
projections = bulk_csv_projections(players, scoring_system="ppr", use_ml=True)

for name, proj in projections.items():
    print(f"{proj.player_name} ({proj.position}): {proj.projected_points:.2f} pts")
```

### Advanced Usage

```python
from fumbld_ai.nfl_fantasy_projections.csv_projections_library import CSVProjectionsLibrary

# Initialize library with custom settings
lib = CSVProjectionsLibrary(scoring_system="half_ppr")

# Get detailed player stats
stats = lib.get_player_stats_from_csv("Aaron Rodgers")
if stats:
    print(f"Games played: {stats.games_played}")
    print(f"Passing yards: {stats.passing_yards}")
    print(f"Passing TDs: {stats.passing_tds}")

# Train ML models
lib.train_all_models(force_retrain=True)

# Get projection with ML
projection = lib.get_projection("Aaron Rodgers", use_ml=True)
```

## Supported Positions

### Offensive Players
- **QB** (Quarterbacks): Passing yards, TDs, interceptions, rushing stats
- **RB** (Running Backs): Rushing yards, TDs, receptions, receiving yards
- **WR** (Wide Receivers): Receptions, receiving yards, TDs, rushing stats
- **TE** (Tight Ends): Receptions, receiving yards, TDs

### Defense/Special Teams
- **DEF/DST**: Sacks, interceptions, fumble recoveries, TDs, safeties, blocked kicks

**Defense Input Options:**
- Team abbreviation: `"ARI"`, `"SF"`, `"NE"`
- City name: `"Arizona"`, `"San Francisco"`, `"New England"`
- With DEF suffix: `"San Francisco DEF"`, `"Arizona DEF"`

### Kickers
- **K**: Field goals made/attempted, distance bonuses, extra points

## Scoring Systems

### PPR (Points Per Reception)
- Passing: 1 pt per 25 yards, 4 pts per TD, -2 per INT
- Rushing: 1 pt per 10 yards, 6 pts per TD
- Receiving: 1 pt per 10 yards, 6 pts per TD, **1 pt per reception**
- Defense: Varies by stat (sacks, INTs, TDs, points allowed)
- Kickers: 3 pts per FG, 1 pt per XP, distance bonuses

### Half-PPR
- Same as PPR but **0.5 pts per reception**

### Standard
- Same as PPR but **0 pts per reception**

### Superflex
- Same as PPR but **6 pts per passing TD** (higher QB scoring)

## Data Requirements

Your `nfl_stats` folder should contain:

```
nfl_stats/
├── df_weekly_2024.csv      # Weekly player stats
├── dst_stats_2024.csv      # Defense/special teams stats
└── kicker_stats_2024.csv   # Kicker stats
```

### CSV Format Examples

**df_weekly_2024.csv:**
```csv
player_display_name,position,season,week,passing_yards,passing_tds,interceptions,rushing_yards,rushing_tds,receiving_yards,receiving_tds,receptions,fantasy_points,fantasy_points_ppr
Aaron Rodgers,QB,2024,1,167.0,1,1.0,-1.0,0,0.0,0,0,8.58,8.58
```

**dst_stats_2024.csv:**
```csv
team,week,sacks,interceptions,fumbles,safeties,def_tds,blocked_kicks
ARI,1,2.0,0.0,1,0.0,4,0
```

**kicker_stats_2024.csv:**
```csv
kicker,team,week,fg_made,fg_avg_dist,fg_long,fg_attempts,xp_made
Justin Tucker,BAL,1,2,38.4,58.0,5,3
```

## Machine Learning Features

### Training Models

```python
from fumbld_ai.nfl_fantasy_projections.csv_projections_library import train_all_csv_models

# Train all position models
train_all_csv_models(force_retrain=True)
```

### Daily Updates (Simulated Learning)

```python
lib = CSVProjectionsLibrary()

# Update models with new data (daily learning)
lib.update_with_new_data(daily_update=True)
```

### ML Model Details

- **Positions**: Separate models for QB, RB, WR, TE, DEF, K
- **Algorithms**: Ensemble of RandomForest, GradientBoosting, and LinearRegression
- **Features**: Per-game averages, position indicators, historical performance
- **Storage**: Models saved to `nfl_stats/ml_models/` directory

## API Reference

### Core Functions

#### `get_csv_projection(player_name, scoring_system="ppr", use_ml=True)`
Get a single player projection.

**Parameters:**
- `player_name` (str): Player name or city name for defenses
- `scoring_system` (str): "ppr", "half_ppr", "standard", or "superflex"
- `use_ml` (bool): Whether to use ML for projection

**Returns:** `PlayerProjection` object or `None`

#### `bulk_csv_projections(player_names, scoring_system="ppr", use_ml=True)`
Get projections for multiple players.

**Parameters:**
- `player_names` (List[str]): List of player names
- `scoring_system` (str): Scoring system
- `use_ml` (bool): Whether to use ML

**Returns:** `Dict[str, PlayerProjection]`

### CSVProjectionsLibrary Class

#### `__init__(scoring_system="ppr", data_path=None)`
Initialize the library.

#### `get_projection(player_name, position=None, use_ml=True)`
Get projection for a single player.

#### `get_multiple_projections(player_names, use_ml=True)`
Get projections for multiple players.

#### `train_all_models(force_retrain=False)`
Train ML models for all positions.

#### `export_projections_to_csv(projections, filename=None)`
Export projections to CSV file.

### Data Classes

#### `PlayerProjection`
```python
@dataclass
class PlayerProjection:
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
```

#### `PlayerStats`
```python
@dataclass
class PlayerStats:
    player_name: str
    position: str
    team: str
    games_played: int
    # ... all offensive, defensive, and kicker stats
```

## Example Usage Scenarios

### Fantasy Lineup Optimization

```python
# Get projections for your roster
roster = [
    "Josh Allen",           # QB
    "Christian McCaffrey",  # RB
    "Davante Adams",       # WR
    "Travis Kelce",        # TE
    "San Francisco",       # DEF (city name)
    "Justin Tucker"        # K
]

projections = bulk_csv_projections(roster, scoring_system="ppr", use_ml=True)

# Sort by projected points
sorted_projections = sorted(
    projections.values(), 
    key=lambda x: x.projected_points, 
    reverse=True
)

print("Your lineup projections:")
for proj in sorted_projections:
    print(f"{proj.player_name} ({proj.position}): {proj.projected_points:.1f} pts")
```

### Waiver Wire Analysis

```python
# Compare available players
available_rbs = ["Gus Edwards", "Ty Johnson", "Craig Reynolds"]
rb_projections = bulk_csv_projections(available_rbs, use_ml=True)

best_pickup = max(rb_projections.values(), key=lambda x: x.projected_points)
print(f"Best RB pickup: {best_pickup.player_name} ({best_pickup.projected_points:.1f} pts)")
```

### Export for External Analysis

```python
# Get projections and export to CSV
all_qbs = ["Josh Allen", "Lamar Jackson", "Aaron Rodgers", "Tom Brady"]
qb_projections = bulk_csv_projections(all_qbs, scoring_system="superflex")

# Export to CSV
csv_path = lib.export_projections_to_csv(qb_projections, "qb_rankings.csv")
print(f"Exported QB rankings to: {csv_path}")
```

## Debugging

Enable debug prints to see detailed processing:

```python
import fumbld_ai.nfl_fantasy_projections.csv_projections_library as csv_lib
csv_lib.DEBUG_PRINTS = True

# Now all operations will show debug output
projection = get_csv_projection("Aaron Rodgers")
```

## City Name to Team Mapping

The library supports these city names for defenses:

| City Name | Team Code | Full Name |
|-----------|-----------|-----------|
| Arizona | ARI | Arizona Cardinals |
| Atlanta | ATL | Atlanta Falcons |
| Baltimore | BAL | Baltimore Ravens |
| Buffalo | BUF | Buffalo Bills |
| Carolina | CAR | Carolina Panthers |
| Chicago | CHI | Chicago Bears |
| Cincinnati | CIN | Cincinnati Bengals |
| Cleveland | CLE | Cleveland Browns |
| Dallas | DAL | Dallas Cowboys |
| Denver | DEN | Denver Broncos |
| Detroit | DET | Detroit Lions |
| Green Bay | GB | Green Bay Packers |
| Houston | HOU | Houston Texans |
| Indianapolis | IND | Indianapolis Colts |
| Jacksonville | JAX | Jacksonville Jaguars |
| Kansas City | KC | Kansas City Chiefs |
| Las Vegas | LV | Las Vegas Raiders |
| Los Angeles Chargers | LAC | Los Angeles Chargers |
| Los Angeles Rams | LA | Los Angeles Rams |
| Miami | MIA | Miami Dolphins |
| Minnesota | MIN | Minnesota Vikings |
| New England | NE | New England Patriots |
| New Orleans | NO | New Orleans Saints |
| New York Giants | NYG | New York Giants |
| New York Jets | NYJ | New York Jets |
| Philadelphia | PHI | Philadelphia Eagles |
| Pittsburgh | PIT | Pittsburgh Steelers |
| San Francisco | SF | San Francisco 49ers |
| Seattle | SEA | Seattle Seahawks |
| Tampa Bay | TB | Tampa Bay Buccaneers |
| Tennessee | TEN | Tennessee Titans |
| Washington | WAS | Washington Commanders |

## Troubleshooting

### Common Issues

1. **"Player not found"**: Check spelling, try city name for defenses
2. **"ML not available"**: Install scikit-learn: `pip install scikit-learn`
3. **"No CSV data"**: Ensure CSV files are in the correct `nfl_stats` folder
4. **Low confidence scores**: Player needs more games played for higher confidence

### Error Messages

- `❌ No CSV data available`: Check file paths and CSV format
- `❌ Insufficient data for model training`: Need more player records
- `🤖 ML prediction failed`: Fallback to statistical projection used

## Performance Notes

- **First Run**: May take time to train ML models
- **Subsequent Runs**: Models are cached and load quickly
- **Memory Usage**: Models are stored in memory after loading
- **Disk Usage**: Models saved to `nfl_stats/ml_models/` directory

## License

This library is part of the Fumbld AI fantasy football projection system.

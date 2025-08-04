import nfl_data_py as nfl
import pandas as pd
import os, requests

nfl_stats_path = os.path.join(os.getcwd(), 'source', 'nfl_stats', 'data')

response = requests.get("https://api.sleeper.app/v1/state/nfl")

# print(response.json())
df = pd.DataFrame([response.json()])

week = df['week'].iloc[0]
season = int(df['season'].iloc[0])
season_type = df['season_type'].iloc[0]
prev_season = int(df['previous_season'].iloc[0])

if season_type == "pre":
    print(f"Current season is in pre-season - using previous season: {prev_season}")
    season = prev_season

# -------------------------
# GAME SCHEDULE
# -------------------------
df_schedule = nfl.import_schedules([season])
df_schedule.to_csv(rf'{nfl_stats_path}\\df_schedule_' + str(season) + ".csv", index=False)
print(f"✅ Exported df_schedule_{season}.csv")

# -------------------------
# INJURY REPORT
# -------------------------
df_depth_chart = nfl.import_injuries([season])
df_depth_chart.to_csv(rf'{nfl_stats_path}\\df_injury_' + str(season) + ".csv", index=False)
print(f"✅ Exported df_injury_{season}.csv")

# -------------------------
# WEEKLY PLAYER STATS
# -------------------------
projection_stats = [
    # Identification
    'player_display_name', 'position', 'season', 'week',

    # Passing stats
    'completions', 'attempts', 'passing_yards', 'passing_tds',
    'interceptions', 'passing_2pt_conversions',

    # Rushing stats
    'carries', 'rushing_yards', 'rushing_tds',
    'rushing_fumbles_lost', 'rushing_2pt_conversions',

    # Receiving stats
    'receptions', 'targets', 'receiving_yards', 'receiving_tds',
    'receiving_fumbles_lost', 'receiving_2pt_conversions',

    # Special teams
    'special_teams_tds',

    # Final fantasy scores (optional for projection comparison/validation)
    'fantasy_points', 'fantasy_points_ppr'
]

df_weekly = nfl.import_weekly_data(
    [season], 
    projection_stats,
    downcast=False
)
df_weekly.to_csv(rf'{nfl_stats_path}\\df_weekly_2024.csv', index=False)
print(f"✅ Exported df_weekly_{season}.csv")

# -------------------------
# KICKER STATS
# -------------------------
# Load play-by-play data for the season
pbp = nfl.import_pbp_data([season], downcast=False)

# Get roster data to map kicker IDs to full names
roster = nfl.__import_rosters(release='seasonal', years=[season])
kicker_roster = roster[roster['position'] == 'K'][['player_id', 'player_name', 'team']].drop_duplicates()

kicker_plays = pbp[
    pbp['kicker_player_name'].notna() & 
    pbp['play_type'].isin(['field_goal', 'extra_point'])
]

# Use kicker_player_id to get full names from roster
kicker_stats = kicker_plays.groupby(['kicker_player_id', 'posteam', 'week']).agg({
    'field_goal_result': lambda x: (x == 'made').sum(),
    'kick_distance': ['mean', 'max', 'count'],
    'extra_point_result': lambda x: (x == 'good').sum()
}).reset_index()

# Flatten columns
kicker_stats.columns = ['kicker_id', 'team', 'week', 'fg_made', 'fg_avg_dist', 'fg_long', 'fg_attempts', 'xp_made']

# Merge with roster to get full player names
kicker_stats = kicker_stats.merge(
    kicker_roster[['player_id', 'player_name']], 
    left_on='kicker_id', 
    right_on='player_id', 
    how='left'
).drop(['kicker_id', 'player_id'], axis=1)

# Reorder columns to put player name first
kicker_stats = kicker_stats[['player_name', 'team', 'week', 'fg_made', 'fg_avg_dist', 'fg_long', 'fg_attempts', 'xp_made']]
kicker_stats.rename(columns={'player_name': 'kicker'}, inplace=True)

# -------------------------
# DST STATS
# -------------------------
def is_def_td(row):
    return (
        row['touchdown'] == 1 and
        row['defteam'] != row['posteam'] and
        row['play_type'] not in ['kickoff', 'punt']
    )

pbp['def_tds'] = pbp.apply(is_def_td, axis=1)

# Fumble recoveries by defense
pbp['fumble_recoveries'] = (
    (pbp['fumble_recovery_1_team'] == pbp['defteam']).astype(int) +
    (pbp['fumble_recovery_2_team'] == pbp['defteam']).astype(int)
)

# Blocked kicks (FGs or PATs)
pbp['blocked_kick'] = pbp['blocked_player_name'].notna()

# Aggregate team DST stats
dst_stats = pbp.groupby(['defteam', 'week']).agg({
    'sack': 'sum',
    'interception': 'sum',
    'fumble_recoveries': 'sum',
    'safety': 'sum',
    'def_tds': 'sum',
    'blocked_kick': 'sum'
}).reset_index()

dst_stats.columns = ['team', 'week', 'sacks', 'interceptions', 'fumbles', 'safeties', 'def_tds', 'blocked_kicks']

# -------------------------
# Export to CSV
# -------------------------
kicker_stats.to_csv(f'{nfl_stats_path}\\kicker_stats_2024.csv', index=False)
dst_stats.to_csv(f'{nfl_stats_path}\\dst_stats_2024.csv', index=False)
print(f"✅ Exported kicker_stats_{season}.csv and dst_stats_{season}.csv")

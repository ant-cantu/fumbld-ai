import nfl_data_py as nfl
import pandas as pd
import os, requests

nfl_stats_path = os.path.join(os.getcwd(), 'source\\nfl_stats\\data')
season = 2024

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

kicker_plays = pbp[
    pbp['kicker_player_name'].notna() & 
    pbp['play_type'].isin(['field_goal', 'extra_point'])
]

kicker_stats = kicker_plays.groupby(['kicker_player_name', 'posteam', 'week']).agg({
    'field_goal_result': lambda x: (x == 'made').sum(),
    'kick_distance': ['mean', 'max', 'count'],
    'extra_point_result': lambda x: (x == 'good').sum()
}).reset_index()

# Flatten columns
kicker_stats.columns = ['kicker', 'team', 'week', 'fg_made', 'fg_avg_dist', 'fg_long', 'fg_attempts', 'xp_made']

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
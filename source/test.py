import pandas as pd
import os

projections = pd.read_csv(os.path.join(os.path.dirname(__file__), "df_projected_points_2024.csv"))

def get_player_projection(player_name):
    player_data = projections[projections['player_name'].str.contains(player_name, case=False, na=False)]
    if not player_data.empty:
        return player_data[['projected_points', 'confidence']].iloc[0]
    else:
        return None
    
def get_top_players_by_position(top_x=5):
    if projections.empty:
        return {}
    
    top_players = {}
    positions = projections['position'].unique()
    
    for position in positions:
        position_players = projections[projections['position'] == position]
        top_position_players = position_players.nlargest(top_x, 'projected_points')
        top_players[position] = top_position_players[['player_name', 'projected_points', 'confidence']]
    
    return top_players

projection = get_player_projection("Josh Allen")
pp = projection.iloc[0]
conf = projection.iloc[1]
print(f"pp: {pp} | conf: {conf}")

# cprint(get_top_players_by_position(10))
# Example usage:
# result = get_player_projection("Player Name")
# if result is not None:
#     print(f"Projected Points: {result['projected_points']}, Confidence: {result['confidence']}")

import nfl_data_py as nfl

pbp = nfl.import_pbp_data([2024], downcast=False)

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
pbp.to_csv(os.path.join(desktop_path, "nfl_pbp_2024.csv"), index=False)
print(f"Data saved to {os.path.join(desktop_path, 'nfl_pbp_2024.csv')}")


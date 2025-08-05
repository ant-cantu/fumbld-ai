import pandas as pd
import os, requests

# projections = pd.read_csv(os.path.join(os.path.dirname(__file__), "df_projected_points_2024.csv"))

# def get_player_projection(player_name):
#     player_data = projections[projections['player_name'].str.contains(player_name, case=False, na=False)]
#     if not player_data.empty:
#         return player_data[['projected_points', 'confidence']].iloc[0]
#     else:
#         return None
    
# def get_top_players_by_position(top_x=5):
#     if projections.empty:
#         return {}
    
#     top_players = {}
#     positions = projections['position'].unique()
    
#     for position in positions:
#         position_players = projections[projections['position'] == position]
#         top_position_players = position_players.nlargest(top_x, 'projected_points')
#         top_players[position] = top_position_players[['player_name', 'projected_points', 'confidence']]
    
#     return top_players

# projection = get_player_projection("Josh Allen")
# pp = projection.iloc[0]
# conf = projection.iloc[1]
# print(f"pp: {pp} | conf: {conf}")

# cprint(get_top_players_by_position(10))
# Example usage:
# result = get_player_projection("Player Name")
# if result is not None:
#     print(f"Projected Points: {result['projected_points']}, Confidence: {result['confidence']}")

# import nfl_data_py as nfl

# desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

# df_players = nfl.__import_rosters(release="seasonal", years=[2024])
# df_players.to_csv(rf'{desktop_path}\\df_players_2024.csv', index=False)
# print(f"✅ Exported df_players_2024.csv")

# name = "Josh Allen"
# player = pd.read_csv(os.path.join(os.path.dirname(__file__), "nfl_stats/data/df_players_2024.csv"))
# player_url = player[player['player_name'].str.contains(name, case=False, na=False)]
# if not player_url.empty:
#     print(player_url['headshot_url'].iloc[0])

def get_sleeper_league_setup(league_id):
    response = requests.get(f'https://api.sleeper.app/v1/league/{league_id}')

    if response.status_code == 200:
        data = response.json()
        if data == "null":
            raise Exception("'get_sleeper_league_setup()': League data does not exist.")
        
        if data['roster_positions']:
            league_setup = data['roster_positions']
        
        return league_setup


import requests
import pandas as pd
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
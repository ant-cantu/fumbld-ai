import requests, json
import os

response = requests.get('https://api.sleeper.app/v1/players/nfl')

try:
    if response.status_code == 200: 
        file_path = os.path.join(os.path.dirname(__file__), 'player_data.json')
        with open(file_path, 'w') as file:
            json.dump(response.json(), file, indent=4)
            print("Successfully downloaded and saved player data.")
    else:
        print({'error': response.status_code})
except Exception as e:
    print({'error': e})
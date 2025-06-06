# roster.py
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json, os
from flask import render_template

#current_script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the name of the subdirectory you're looking for
#subdirectory_name = "ignore"

# Construct the full path to the potential subdirectory
#potential_subdir_path = os.path.join(current_script_dir, subdirectory_name)

#file_path = os.path.join(potential_subdir_path, "oauth2.json")

#oauth = OAuth2(None, None, from_file=file_path)

#game = yfa.Game(oauth, 'nfl')

# print(game.league_ids(year=2024))



def roster():
    league = game.to_league('449.l.142565')

    team = league.to_team(league.team_key())

    roster = json.dumps(team.roster(week=12), indent=4)
    
    return render_template("roster.html", roster=roster)
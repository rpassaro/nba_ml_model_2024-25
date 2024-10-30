import argparse
from datetime import datetime, timedelta

import pandas as pd
import tensorflow as tf
import requests

from sbrscrape import Scoreboard
from src.Process_Data.update_dataset import update_nba_dataset, fetch_nba_data, get_data_single_game
from src.Predict.XGBoost_Runner import predict_single_game
from season_models_tests import szn_model_test

# Update dataset:
print("UPDATING DATASET")
update_nba_dataset()
print("DATASET UPDATED")

print("\nBACKTESTING MODELS")
szn_model_test()
print("MODELS TESTED\n")

# URLs for today's games and team stats
todays_games_url = 'https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2024/scores/00_todays_scores.json' #Check this after 2024
data_url = 'https://stats.nba.com/stats/leaguedashteamstats?' \
           'Conference=&DateFrom=&DateTo=&Division=&GameScope=&' \
           'GameSegment=&LastNGames=0&LeagueID=00&Location=&' \
           'MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&' \
           'PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&' \
           'PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&' \
           'Season=2023-24&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&' \
           'StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision='

# Headers to avoid being blocked by NBA.com
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
    'Referer': 'https://www.nba.com/',
    'Origin': 'https://www.nba.com',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Fetch today's games
def get_todays_games():
    response = requests.get(todays_games_url, headers=headers)
    if response.status_code == 200:
        todays_games = response.json()
        games_list = todays_games.get('gs', {}).get('g', [])  # Access the games list

        # Display home and away teams
        todays_games = []
        names = []
        for game in games_list:
            home_team = game['h']['tc'] + " " + game['h']['tn']
            away_team = game['v']['tc'] + " " + game['v']['tn']
            names.append([game['h']['tn'], game['v']['tn']])
            todays_games.append([home_team, away_team])
        
    else:
        print(f"Error fetching today's games: {response.status_code}")
        
    if len(todays_games) == 0:
        print("NO GAMES")
        return None
    
    return [todays_games, names]
  
def get_todays_picks():
    todays_games_data = get_todays_games()
    todays_games = todays_games_data[0]
    todays_names = todays_games_data[1]
    all_games_data = fetch_nba_data(datetime.today())['resultSets'][0].get('rowSet')
    sb = Scoreboard(date=datetime.today())
    name_index = 0
    for game in todays_games:
        single_game_data = get_data_single_game(game[0], game[1], sb, all_games_data, datetime.today().strftime("%m/%d/%Y"), 0, 0)
        keys_to_remove = {'Score', 'Home-Team-Win', 'OU-Cover', 'Date', 'TEAM_NAME', 'TEAM_NAME.1'}
        single_game_data = {k: v for k, v in single_game_data.items() if k not in keys_to_remove}

        single_game_df = pd.DataFrame(single_game_data, index=[0])
        prediction = predict_single_game(single_game_df)
        if prediction == None:
            continue #No agreement
        else:
            if prediction == 0:
                print(todays_names[name_index][0] + " vs " + todays_names[name_index][1] + ": UNDER " + str(single_game_data['OU']))
            else:
                print(todays_names[name_index][0] + " vs " + todays_names[name_index][1] + ": OVER " + str(single_game_data['OU']))
        name_index += 1

get_todays_picks()

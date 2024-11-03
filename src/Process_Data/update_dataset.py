import sqlite3
import pandas as pd
import requests
from datetime import datetime, timedelta
from sbrscrape import Scoreboard

# Headers for making API requests
games_header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/57.0.2987.133 Safari/537.36',
    'Dnt': '1',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en',
    'origin': 'http://stats.nba.com',
    'Referer': 'https://github.com'
}

data_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.nba.com/',
    'Connection': 'keep-alive'
}

# Database path
DATABASE_PATH = "C:/Users/Ryan/Desktop/NBA_AI_Model/Data/dataset.sqlite"

# NBA API URL for team stats (customize with parameters as needed)
NBA_API_URL = "https://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=10%2F01%2F2024&DateTo={month}%2F{day}%2F{year}&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2024-25&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision="

# Function to get the most recent date from the database
def get_most_recent_date():
    conn = sqlite3.connect(DATABASE_PATH)
    query = "SELECT MAX(Date) FROM nba_dataset"
    result = conn.execute(query).fetchone()[0]
    conn.close()
    return result

def fetch_nba_data(date):
    
    #GETS DATA FROM DAY BEFORE
    
    if isinstance(date, str):
        date = datetime.strptime(date, "%m/%d/%Y")
    date -= timedelta(days=1)
    month = date.month
    day = date.day
    year = date.year
    
    # Format the URL with the date
    url = NBA_API_URL.format(month=month, day=day, year=year)
    response = requests.get(url, headers=data_headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

def insert_data_into_db(data):
    # Connect to the original database
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Read existing data from the table
    try:
        existing_data = pd.read_sql_query("SELECT * FROM nba_dataset", conn)
    except Exception as e:
        print("Error reading from original database:", e)
        existing_data = pd.DataFrame()  # Use an empty DataFrame if table doesn't exist
    
    # Convert new data to DataFrame
    new_data = pd.DataFrame(data)
    
    # Append new data to the existing data
    updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    
    # Close the original database connection
    conn.close()
    
    # Connect to the new database file and save the updated data
    conn_new = sqlite3.connect(DATABASE_PATH)
    updated_data.to_sql('nba_dataset', conn_new, if_exists='replace', index=False)
    
    # Close the connection to the new database
    conn_new.close()
    
def fetch_games_on_date(date):
    # Format the URL with the specific date
    url = f"https://stats.nba.com/stats/scoreboardv2?GameDate={date}&LeagueID=00&DayOffset=0&SeasonType=Regular+Season"
    
    # Make the request
    response = requests.get(url, headers=data_headers)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching data: {response.status_code}")
        return None
    
def loop_through_dates(start_date_str):
    # Convert the start date from a string (format: 'YYYY-MM-DD') to a datetime object
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.today() - timedelta(days=1)  # Today's date

    # Loop from the start date to the end date
    current_date = start_date
    dates = []
    while current_date <= end_date:
        # Format the current date as needed (e.g., "MM/DD/YYYY" for the API)
        formatted_date = current_date.strftime("%m/%d/%Y")
        dates.append(formatted_date)

        # Perform any actions here, like calling a function with `formatted_date`
        # Example: fetch_game_ids_on_date(formatted_date)

        # Move to the next day
        current_date += timedelta(days=1)
    return dates
        
def get_data_single_game(home_team, away_team, sb, all_games_data, date, home_score, away_score):
    for game_odds in sb.games:
        if game_odds['home_team'] != home_team:
            continue
        ou_line = game_odds.get('total', {}).get('draftkings')
        break
    home_team_data = next((team_data for team_data in all_games_data if team_data[1] == home_team), None)
    away_team_data = next((team_data for team_data in all_games_data if team_data[1] == away_team), None)
    game_dict = {
        'TEAM_NAME': home_team,
        'GP': home_team_data[2] if home_team_data is not None else 0,
        'W': home_team_data[3] if home_team_data is not None else 0,
        'L': home_team_data[4] if home_team_data is not None else 0,
        'W_PCT': home_team_data[5] if home_team_data is not None else 0,
        'MIN': home_team_data[6] if home_team_data is not None else 0,
        'FGM': home_team_data[7] if home_team_data is not None else 0,
        'FGA': home_team_data[8] if home_team_data is not None else 0,
        'FG_PCT': home_team_data[9] if home_team_data is not None else 0,
        'FG3M': home_team_data[10] if home_team_data is not None else 0,
        'FG3A': home_team_data[11] if home_team_data is not None else 0,
        'FG3_PCT': home_team_data[12] if home_team_data is not None else 0,
        'FTM': home_team_data[13] if home_team_data is not None else 0,
        'FTA': home_team_data[14] if home_team_data is not None else 0,
        'FT_PCT': home_team_data[15] if home_team_data is not None else 0,
        'OREB': home_team_data[16] if home_team_data is not None else 0,
        'DREB': home_team_data[17] if home_team_data is not None else 0,
        'REB': home_team_data[18] if home_team_data is not None else 0,
        'AST': home_team_data[19] if home_team_data is not None else 0,
        'TOV': home_team_data[20] if home_team_data is not None else 0,
        'STL': home_team_data[21] if home_team_data is not None else 0,
        'BLK': home_team_data[22] if home_team_data is not None else 0,
        'BLKA': home_team_data[23] if home_team_data is not None else 0,
        'PF': home_team_data[24] if home_team_data is not None else 0,
        'PFD': home_team_data[25] if home_team_data is not None else 0,
        'PTS': home_team_data[26] if home_team_data is not None else 0,
        'PLUS_MINUS': home_team_data[27] if home_team_data is not None else 0,
        'GP_RANK': home_team_data[28] if home_team_data is not None else 0,
        'W_RANK': home_team_data[29] if home_team_data is not None else 0,
        'L_RANK': home_team_data[30] if home_team_data is not None else 0,
        'W_PCT_RANK': home_team_data[31] if home_team_data is not None else 0,
        'MIN_RANK': home_team_data[32] if home_team_data is not None else 0,
        'FGM_RANK': home_team_data[33] if home_team_data is not None else 0,
        'FGA_RANK': home_team_data[34] if home_team_data is not None else 0,
        'FG_PCT_RANK': home_team_data[35] if home_team_data is not None else 0,
        'FG3M_RANK': home_team_data[36] if home_team_data is not None else 0,
        'FG3A_RANK': home_team_data[37] if home_team_data is not None else 0,
        'FG3_PCT_RANK': home_team_data[38] if home_team_data is not None else 0,
        'FTM_RANK': home_team_data[39] if home_team_data is not None else 0,
        'FTA_RANK': home_team_data[40] if home_team_data is not None else 0,
        'FT_PCT_RANK': home_team_data[41] if home_team_data is not None else 0,
        'OREB_RANK': home_team_data[42] if home_team_data is not None else 0,
        'DREB_RANK': home_team_data[43] if home_team_data is not None else 0,
        'REB_RANK': home_team_data[44] if home_team_data is not None else 0,
        'AST_RANK': home_team_data[45] if home_team_data is not None else 0,
        'TOV_RANK': home_team_data[46] if home_team_data is not None else 0,
        'STL_RANK': home_team_data[47] if home_team_data is not None else 0,
        'BLK_RANK': home_team_data[48] if home_team_data is not None else 0,
        'BLKA_RANK': home_team_data[49] if home_team_data is not None else 0,
        'PF_RANK': home_team_data[50] if home_team_data is not None else 0,
        'PFD_RANK': home_team_data[51] if home_team_data is not None else 0,
        'PTS_RANK': home_team_data[52] if home_team_data is not None else 0,
        'PLUS_MINUS_RANK': home_team_data[53] if home_team_data is not None else 0,
        'Date': date,
        'TEAM_NAME.1': away_team,
        'GP.1': away_team_data[2] if away_team_data is not None else 0,
        'W.1': away_team_data[3] if away_team_data is not None else 0,
        'L.1': away_team_data[4] if away_team_data is not None else 0,
        'W_PCT.1': away_team_data[5] if away_team_data is not None else 0,
        'MIN.1': away_team_data[6] if away_team_data is not None else 0,
        'FGM.1': away_team_data[7] if away_team_data is not None else 0,
        'FGA.1': away_team_data[8] if away_team_data is not None else 0,
        'FG_PCT.1': away_team_data[9] if away_team_data is not None else 0,
        'FG3M.1': away_team_data[10] if away_team_data is not None else 0,
        'FG3A.1': away_team_data[11] if away_team_data is not None else 0,
        'FG3_PCT.1': away_team_data[12] if away_team_data is not None else 0,
        'FTM.1': away_team_data[13] if away_team_data is not None else 0,
        'FTA.1': away_team_data[14] if away_team_data is not None else 0,
        'FT_PCT.1': away_team_data[15] if away_team_data is not None else 0,
        'OREB.1': away_team_data[16] if away_team_data is not None else 0,
        'DREB.1': away_team_data[17] if away_team_data is not None else 0,
        'REB.1': away_team_data[18] if away_team_data is not None else 0,
        'AST.1': away_team_data[19] if away_team_data is not None else 0,
        'TOV.1': away_team_data[20] if away_team_data is not None else 0,
        'STL.1': away_team_data[21] if away_team_data is not None else 0,
        'BLK.1': away_team_data[22] if away_team_data is not None else 0,
        'BLKA.1': away_team_data[23] if away_team_data is not None else 0,
        'PF.1': away_team_data[24] if away_team_data is not None else 0,
        'PFD.1': away_team_data[25] if away_team_data is not None else 0,
        'PTS.1': away_team_data[26] if away_team_data is not None else 0,
        'PLUS_MINUS.1': away_team_data[27] if away_team_data is not None else 0,
        'GP_RANK.1': away_team_data[28] if away_team_data is not None else 0,
        'W_RANK.1': away_team_data[29] if away_team_data is not None else 0,
        'L_RANK.1': away_team_data[30] if away_team_data is not None else 0,
        'W_PCT_RANK.1': away_team_data[31] if away_team_data is not None else 0,
        'MIN_RANK.1': away_team_data[32] if away_team_data is not None else 0,
        'FGM_RANK.1': away_team_data[33] if away_team_data is not None else 0,
        'FGA_RANK.1': away_team_data[34] if away_team_data is not None else 0,
        'FG_PCT_RANK.1': away_team_data[35] if away_team_data is not None else 0,
        'FG3M_RANK.1': away_team_data[36] if away_team_data is not None else 0,
        'FG3A_RANK.1': away_team_data[37] if away_team_data is not None else 0,
        'FG3_PCT_RANK.1': away_team_data[38] if away_team_data is not None else 0,
        'FTM_RANK.1': away_team_data[39] if away_team_data is not None else 0,
        'FTA_RANK.1': away_team_data[40] if away_team_data is not None else 0,
        'FT_PCT_RANK.1': away_team_data[41] if away_team_data is not None else 0,
        'OREB_RANK.1': away_team_data[42] if away_team_data is not None else 0,
        'DREB_RANK.1': away_team_data[43] if away_team_data is not None else 0,
        'REB_RANK.1': away_team_data[44] if away_team_data is not None else 0,
        'AST_RANK.1': away_team_data[45] if away_team_data is not None else 0,
        'TOV_RANK.1': away_team_data[46] if away_team_data is not None else 0,
        'STL_RANK.1': away_team_data[47] if away_team_data is not None else 0,
        'BLK_RANK.1': away_team_data[48] if away_team_data is not None else 0,
        'BLKA_RANK.1': away_team_data[49] if away_team_data is not None else 0,
        'PF_RANK.1': away_team_data[50] if away_team_data is not None else 0,
        'PFD_RANK.1': away_team_data[51] if away_team_data is not None else 0,
        'PTS_RANK.1': away_team_data[52] if away_team_data is not None else 0,
        'PLUS_MINUS_RANK.1': away_team_data[53] if away_team_data is not None else 0,
        'Score': home_score + away_score,
        'Home-Team-Win': 1 if home_score > away_score else 0,
        'OU': ou_line,
        'OU-Cover': 1 if (home_score + away_score) > ou_line else 0,
    }
    return game_dict
        
# Main function to update the dataset
def update_nba_dataset():
    conn = sqlite3.connect(DATABASE_PATH)
    table_name = 'nba_dataset'
    master_data_df = pd.read_sql_query(f"SELECT * FROM {table_name}",conn)
    
    # Get the most recent date from the dataset
    most_recent_date = get_most_recent_date()
    if not most_recent_date:
        print("No previous data found.")
    print(most_recent_date)
    dates = loop_through_dates("2024-10-29")
    all_game_dicts = []
    for date in dates:
        if not master_data_df[(master_data_df['Date'] == date)].empty:
            continue
        
        else:
            #GET GAMES ON THIS DATE
            games_on_date = fetch_games_on_date(date)['resultSets'][1]['rowSet']
            if games_on_date:
                all_games_data = fetch_nba_data(date)['resultSets'][0].get('rowSet')
                sb = Scoreboard(date=date)
                for i in range(0, len(games_on_date), 2):
                    # Slice out two games at a time
                    game = games_on_date[i:i+2]
                    home_team, away_team = game[1][5] + " " + game[1][6], game[0][5] + " " + game[0][6]
                    home_score, away_score = game[1][22], game[0][22]
                    all_game_dicts.append(get_data_single_game(home_team, away_team, sb, all_games_data, date, home_score, away_score))
                
    insert_data_into_db(all_game_dicts)

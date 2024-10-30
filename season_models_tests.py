import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score
import os
from tqdm import tqdm
from send2trash import send2trash
import sqlite3

def szn_model_test():
    
    conn = sqlite3.connect("Data/dataset.sqlite")
    games_df = pd.read_sql("SELECT * FROM nba_dataset", conn)
    conn.close()

    # Separate features and target label
    label = games_df['OU-Cover']
    features = games_df.drop(columns=['TEAM_NAME', 'TEAM_NAME.1', 'index', 'Date', 'Date.1', 'Score', 'Home-Team-Win', 'OU-Cover'])

    model_directory = "C:/Users/Ryan/Desktop/NBA_AI_Model/Models"
    # List all model files in the directory
    model_files = [f for f in os.listdir(model_directory) if f.endswith('.json')]

    all_accuracies = []
    accuracies = {}
    accuracy_vals = []
    num_r = 0

    for model_file in tqdm(model_files, desc = "TESTING MODELS"):
        num_r += 1
        model_path = os.path.join(model_directory, model_file)

        xgb_uo = xgb.Booster()
        xgb_uo.load_model(model_path)
        uw = 0
        ul = 0
        ow = 0
        ol = 0

        for index, row in features.iterrows():
            if index < len(games_df) - 200:
                continue

            row_data = np.array(row).reshape(1, -1)
            dmatrix_data = xgb.DMatrix(row_data)
                
            # Predict and collect predictions
            prediction = xgb_uo.predict(dmatrix_data)
            ou_prediction = int(np.argmax(prediction))
            
            if ou_prediction == 0:
                if label[index] == 0:
                    uw += 1
                else:
                    ul += 1
            else:
                if label[index] == 1:
                    ow += 1
                else:
                    ol += 1
        games_total = ol + ow + uw + ul
        games_won = ow + uw

        accuracy = (games_won) / (games_total)
        
        if accuracy < .47:
            print(f"\nFOUND BAD FILE, REMOVING NOW\nACCURACY: {accuracy}, FILE: {model_path}\n")
            if os.path.exists(model_path):
                #os.remove(model_path)
                print(accuracy)
            continue
        
        all_accuracies.append(accuracy)
        
        min_accuracy = min(accuracy_vals) if len(accuracy_vals) > 0 else 0
        if len(accuracy_vals) < 2:
            accuracy_vals.append(accuracy)
            accuracies[model_file] = accuracy
        elif accuracy > min_accuracy:
            for temp_file in accuracies:
                if accuracies[temp_file] == min_accuracy:
                    accuracies.pop(temp_file)
                    break
            accuracies[model_file] = accuracy
            accuracy_vals.remove(min_accuracy)
            accuracy_vals.append(accuracy)
            
    print(accuracy_vals)
    print(accuracies)
    selected_models = list(accuracies.keys())
    model_index = 0

    # Define the path to the file you want to edit
    file_path = 'C:/Users/Ryan\Desktop/NBA_AI_Model/src/Predict/XGBoost_Runner.py'

    # Read the file content
    with open(file_path, 'r') as file:
        lines = file.readlines()


    # Replace the existing load_model lines
    with open(file_path, 'w') as file:
        for line in lines:
            if 'models = [' in line:
                new_load_model_line = f'models = ["C:/Users/Ryan/Desktop/NBA_AI_Model/Models/{selected_models[0]}", "C:/Users/Ryan/Desktop/NBA_AI_Model/Models/{selected_models[1]}"]\n'
                
                line = new_load_model_line
                
                model_index += 1
            file.write(line)
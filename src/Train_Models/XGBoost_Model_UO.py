import sqlite3

from datetime import datetime, date
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import statistics
import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="xgboost")


dataset = "nba_dataset"
con = sqlite3.connect("../../Data/dataset.sqlite")
data = pd.read_sql_query(f"select * from \"{dataset}\"", con)
data = data.iloc[5173:]
data = data[(data['GP'] > 10) & (data['GP.1'] > 10) & (data['GP'] < 75) & (data['GP.1'] < 75)]
con.close()

OU = data['OU-Cover']
total = data['OU']
dropped_data = ['TEAM_NAME', 'TEAM_NAME.1', 'index', 'Date', 'Score', 'Home-Team-Win', 'OU-Cover']
data.drop(dropped_data, axis=1, inplace=True)

# Add total to data and ensure all columns are numeric
data['OU'] = pd.to_numeric(total, errors='coerce')

data = data.to_numpy()
data = data.astype(float)
acc_results = []

for x in tqdm(range(10000)):
    if x % 50 == 0 and x != 0:
        time.sleep(250)
    print(" Normal params, 10 < gp < 75, normal dataset")
    x_train, x_test, y_train, y_test = train_test_split(data, OU, test_size=0.1)

    # Create DMatrix for XGBoost
    train = xgb.DMatrix(x_train, label=y_train)
    test = xgb.DMatrix(x_test)

    # Define the parameters for XGBoost
    param = {
        'max_depth': 20,
        'eta': 0.05,
        'objective': 'multi:softprob',
        'num_class': 3
    }
    epochs = 750

    # Train the model
    model = xgb.train(param, train, epochs)

    # Make predictions
    predictions = model.predict(test)
    y_pred = np.argmax(predictions, axis=1)

    # Total Accuracy
    total_acc = round(accuracy_score(y_test, y_pred) * 100, 3)
    acc_results.append(total_acc)
    if x % 10 == 0:
        print(statistics.mean(acc_results), x)
    # Printing and Saving Accuracies
    print(f"Total Accuracy: {total_acc}%")
        
    # only save results if they are the best so far
    if total_acc > 54:
        print("HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
        #MIGHT HAVE TO CHANGE FOLDER LOC
        model.save_model('../../Models/XGBoost_{}_UO,{},{}.json'.format(total_acc, x, datetime.today().strftime("%Y-%m-%d")))

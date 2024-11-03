import numpy as np
import xgboost as xgb
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="xgboost")
xgb_uo = xgb.Booster()

models = ["C:/Users/Ryan/Desktop/NBA_AI_Model/Models/XGBoost_54.569_UO,648,2024-10-29.json", "C:/Users/Ryan/Desktop/NBA_AI_Model/Models/XGBoost_54.83_UO,265,2024-10-31.json"]

def predict_single_game(game_data):
    ou_predictions_array = []
    for model in models:
        xgb_uo.load_model(model)
        
        dmatrix_data = xgb.DMatrix(game_data, None)
        
        # Predict and collect predictions
        ou_predictions_array.append(np.argmax(xgb_uo.predict(dmatrix_data)))
    if ou_predictions_array[0] == ou_predictions_array[1]:
        return ou_predictions_array[0]
    return None
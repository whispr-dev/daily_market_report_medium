import pandas as pd
import xgboost as xgb
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import joblib
import os

XGB_MODEL_FILE = "models/xgboost_edge.model"
SVM_MODEL_FILE = "models/svm_actionable.pkl"

def get_feature_vector(entry):
    return [
        1 if entry.get("reversal") == "bullish" else 0,
        1 if entry.get("squeeze") else 0,
        entry.get("rs_score", 0),
        1 if entry.get("confluence") else 0
    ]

def predict_confidence(entry):
    import joblib
    model = joblib.load(SVM_MODEL_FILE)
    vec = [get_feature_vector(entry)]
    prob = model.predict_proba(vec)[0][1]  # Probability of class=1
    return round(prob * 100, 1)

def train_models_from_edge_data(edge_data):
    os.makedirs("models", exist_ok=True)
    df = pd.DataFrame(edge_data)

    df["target_score"] = df["score"]
    df["target_class"] = df["score"].apply(lambda x: 1 if x >= 60 else 0)

    X = df.apply(get_feature_vector, axis=1).tolist()
    y_score = df["target_score"].tolist()
    y_class = df["target_class"].tolist()

    xgb_model = xgb.XGBRegressor(n_estimators=100, max_depth=3, objective="reg:squarederror")
    xgb_model.fit(X, y_score)
    xgb_model.save_model(XGB_MODEL_FILE)

    svm_model = make_pipeline(StandardScaler(), SVC(probability=True))
    svm_model.fit(X, y_class)
    joblib.dump(svm_model, SVM_MODEL_FILE)

    print("✅ ML models trained and saved.")

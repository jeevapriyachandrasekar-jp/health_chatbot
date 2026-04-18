import joblib
import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "diseasemodel.pkl")

model_data = joblib.load(model_path)

# Load model and vectorizer
model = model_data["model"]
vectorizer = model_data["vectorizer"]

def predict_with_model(text):
    X = vectorizer.transform([text])
    pred = model.predict(X)[0]
    probs = model.predict_proba(X)[0]
    confidence = max(probs)

    # Top 3 predictions
    top3_idx = probs.argsort()[-3:][::-1]
    top3 = [(model.classes_[i], probs[i]) for i in top3_idx]

    # ✅ Instead of discarding, always return something
    if confidence < 0.2:
        return {
            "predicted_disease": "Unknown / Not enough data",
            "confidence": confidence,
            "top3": top3
        }
    else:
        return {
            "predicted_disease": pred,
            "confidence": confidence,
            "top3": top3
        }

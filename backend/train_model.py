import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Example training data (replace with your dataset)
symptoms = [
    "fever cough headache",
    "sore throat runny nose",
    "stomach pain nausea vomiting",
    "chest pain shortness of breath",
    "joint pain fatigue"
]
labels = ["Flu", "Cold", "Food Poisoning", "Heart Disease", "Arthritis"]

# Vectorize text
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(symptoms)

# Train model
model = MultinomialNB()
model.fit(X, labels)

# Save BOTH model + vectorizer inside dict (no tuple confusion)
joblib.dump({"model": model, "vectorizer": vectorizer}, "diseasemodel.pkl")

print("✅ Model trained and saved as diseasemodel.pkl")

from sklearn.feature_extraction.text import TfidfVectorizer


def vectorize_text(text_list):
    vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=4000)
    X = vectorizer.fit_transform(text_list)
    return X, vectorizer
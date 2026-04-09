# ml_models.py — шаблон модуля
import json
import os

DICTIONARY_PATH = "dictionaries"
FALLBACK_DICT_PATH = "dictionaries/dictionaries"  # ru.json lives here

def load_dictionary(lang_code="az"):
    """
    Load per-language dictionary. Handles both top-level and nested dictionaries/ path.
    """
    candidates = [
        os.path.join(DICTIONARY_PATH, f"{lang_code}.json"),
        os.path.join(FALLBACK_DICT_PATH, f"{lang_code}.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(f"Dictionary for language '{lang_code}' not found at {candidates}")

def analyze_word(word, lang_code="az"):
    dictionary = load_dictionary(lang_code)
    entry = dictionary.get(word.lower(), None)
    if entry:
        return {
            "word": word,
            "POS": entry["POS"],
            "features": entry.get("Features", {})
        }
    else:
        return {
            "word": word,
            "POS": "UNK",
            "features": {}
        }
###
# ml_models.py — машинное обучение на морфологическом корпусе

import json
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from corpus_db import get_corpus

MODEL_PATH = "models/tag_predictor.pkl"

def prepare_dataset():
    corpus = get_corpus()
    X = []
    y = []
    for entry in corpus:
        for token in entry["tokens"]:
            word = token["word"]
            tags = token.get("tags", [])
            if tags:
                X.append(word)
                y.append("+".join(tags))
    return X, y

def train_tag_predictor():
    X, y = prepare_dataset()
    if not X:
        print("Корпус пуст. Невозможно обучить модель.")
        return None

    pipeline = Pipeline([
        ("vect", CountVectorizer(analyzer='char', ngram_range=(2, 4))),
        ("clf", LogisticRegression(max_iter=500))
    ])
    pipeline.fit(X, y)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        import pickle
        pickle.dump(pipeline, f)

    print(f"Модель сохранена в: {MODEL_PATH}")
    return pipeline

def predict_tags(word):
    import pickle
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Модель не обучена. Сначала вызовите train_tag_predictor().")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    predicted = model.predict([word])[0]
    return predicted.split("+")


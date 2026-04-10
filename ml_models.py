# ml_models.py — шаблон модуля
import json
import os
from functools import lru_cache

DICTIONARY_PATH = "dictionaries"
FALLBACK_DICT_PATH = "dictionaries/dictionaries"  # ru.json lives here
ROOTS_PATH = "roots.json"
AFFIXES_PATH = "affixes.json"

AZ_PREDICATIVE_SUFFIXES = ("dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür")
AZ_TAG_FEATURES = {
    "PRS": {"Tense": "Pres"},
    "FUT": {"Tense": "Fut"},
    "PAST": {"Tense": "Past"},
    "EVID": {"Evidentiality": "Evid"},
    "COND": {"Mood": "Cond"},
    "NEC": {"Mood": "Nec"},
    "NEG": {"Polarity": "Neg"},
    "NEG.AOR": {"Polarity": "Neg", "Aspect": "Aor"},
    "AOR": {"Aspect": "Aor"},
    "DAT": {"Case": "Dat"},
    "LOC": {"Case": "Loc"},
    "ABL": {"Case": "Abl"},
    "INSTR": {"Case": "Ins"},
    "POSS.1SG": {"Possessor": "1SG"},
    "POSS.2SG": {"Possessor": "2SG"},
    "POSS.3SG": {"Possessor": "3SG"},
    "POSS.1PL": {"Possessor": "1PL"},
    "POSS.2PL": {"Possessor": "2PL"},
    "POSS.3PL": {"Possessor": "3PL"},
    "PERS.3PL": {"Number": "Plur"},
    "CAUS": {"Voice": "Cau"},
    "PASS": {"Voice": "Pass"},
    "REFL": {"Voice": "Refl"},
}


def _normalize_lookup_key(word):
    return (word or "").strip().casefold()


def load_dictionary(lang_code="az"):
    """
    Load per-language dictionary. Handles both top-level and nested dictionaries/ path.
    Returns an empty dictionary when the requested language data does not exist.
    """
    candidates = [
        os.path.join(DICTIONARY_PATH, f"{lang_code}.json"),
        os.path.join(FALLBACK_DICT_PATH, f"{lang_code}.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


@lru_cache(maxsize=1)
def load_az_roots():
    if not os.path.exists(ROOTS_PATH):
        return {}
    with open(ROOTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_az_affixes():
    if not os.path.exists(AFFIXES_PATH):
        return {}
    with open(AFFIXES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _lookup_dictionary_entry(dictionary, word):
    key = _normalize_lookup_key(word)
    return dictionary.get(key)


def _build_result(word, pos, features=None):
    return {
        "word": word,
        "POS": pos or "UNK",
        "features": dict(features or {}),
    }


def _result_from_entry(word, entry, extra_features=None):
    features = dict(entry.get("Features", {}) or {})
    if extra_features:
        features.update(extra_features)
    return _build_result(word, entry.get("POS", "UNK"), features)


def _tags_to_features(tags):
    features = {}
    for tag in tags:
        features.update(AZ_TAG_FEATURES.get(tag, {"Tag": tag}))
    return features


def _peel_suffixes_to_entry(word, dictionary, max_depth=3):
    affixes = load_az_affixes()
    if not affixes:
        return None

    queue = [(word, [], 0)]
    seen = set()
    ordered_affixes = sorted(
        (
            (affix, meta) for affix, meta in affixes.items()
            if affix not in AZ_PREDICATIVE_SUFFIXES
        ),
        key=lambda item: (-len(item[0]), item[0])
    )

    while queue:
        current, tags, depth = queue.pop(0)
        if depth and _lookup_dictionary_entry(dictionary, current):
            entry = _lookup_dictionary_entry(dictionary, current)
            return _result_from_entry(word, entry, _tags_to_features(tags))

        if depth >= max_depth:
            continue

        for affix, meta in ordered_affixes:
            if current.endswith(affix) and len(current) - len(affix) >= 2:
                stem = current[:-len(affix)]
                state = (stem, tuple(tags + [meta.get("tag", affix)]))
                if state in seen:
                    continue
                seen.add(state)
                queue.append((stem, tags + [meta.get("tag", affix)], depth + 1))

    return None


def _analyze_az_predicative(word, dictionary):
    normalized = _normalize_lookup_key(word)
    for suffix in AZ_PREDICATIVE_SUFFIXES:
        if normalized.endswith(suffix) and len(normalized) - len(suffix) >= 2:
            stem = normalized[:-len(suffix)]
            entry = _lookup_dictionary_entry(dictionary, stem)
            if entry:
                return _result_from_entry(
                    word,
                    entry,
                    {"Predicate": "Yes", "Copula": "3SG"},
                )
    return None


def _analyze_az_by_roots(word):
    normalized = _normalize_lookup_key(word)
    roots = load_az_roots()
    affixes = load_az_affixes()
    ordered_affixes = sorted(affixes.items(), key=lambda item: (-len(item[0]), item[0]))

    for root, meta in sorted(roots.items(), key=lambda item: -len(item[0])):
        if not normalized.startswith(root):
            continue

        remaining = normalized[len(root):]
        tags = []
        while remaining:
            matched = False
            for affix, affix_meta in ordered_affixes:
                if remaining.startswith(affix):
                    tags.append(affix_meta.get("tag", affix))
                    remaining = remaining[len(affix):]
                    matched = True
                    break
            if not matched:
                break

        if not remaining:
            base_features = {"Lemma": root}
            base_features.update(_tags_to_features(tags))
            return _build_result(word, meta.get("pos", "VERB").upper(), base_features)

    return None


def analyze_word(word, lang_code="az"):
    dictionary = load_dictionary(lang_code)
    entry = _lookup_dictionary_entry(dictionary, word)
    if entry:
        return _result_from_entry(word, entry)

    if lang_code == "az":
        for fallback in (
            _analyze_az_predicative(word, dictionary),
            _peel_suffixes_to_entry(word, dictionary),
            _analyze_az_by_roots(word),
        ):
            if fallback:
                return fallback

    return _build_result(word, "UNK", {})
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


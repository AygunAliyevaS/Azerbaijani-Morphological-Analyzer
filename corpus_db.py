# corpus_db.py — storage utilities for the annotated corpus
import json
import os

CORPUS_PATH = "corpus/corpus.json"


def load_corpus():
    if not os.path.exists(CORPUS_PATH):
        return []
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_corpus(corpus):
    os.makedirs(os.path.dirname(CORPUS_PATH), exist_ok=True)
    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)


def add_entry(text, tokens):
    """Append a sentence with token analyses to the corpus."""
    corpus = load_corpus()
    entry = {"text": text, "tokens": tokens}
    corpus.append(entry)
    save_corpus(corpus)


def get_corpus():
    return load_corpus()

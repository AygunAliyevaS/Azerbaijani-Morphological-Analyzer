# export_corpus.py — экспорт корпуса в формат CoNLL-U

from corpus_db import get_corpus
import os

EXPORT_PATH = "corpus/corpus.conllu"

def export_to_conllu():
    corpus = get_corpus()
    with open(EXPORT_PATH, "w", encoding="utf-8") as f:
        for i, entry in enumerate(corpus):
            f.write(f"# sent_id = {i+1}\n")
            f.write(f"# text = {entry['text']}\n")
            for idx, tok in enumerate(entry["tokens"], 1):
                word = tok["word"]
                lemma = tok.get("lemma", word.lower())
                upos = tok["tags"][0] if tok["tags"] else "X"
                feats = "|".join(tok["tags"][1:]) if len(tok["tags"]) > 1 else "_"
                f.write(f"{idx}\t{word}\t{lemma}\t{upos}\t_\t{feats}\t_\t_\t_\t_\n")
            f.write("\n")
    return EXPORT_PATH

if __name__ == "__main__":
    path = export_to_conllu()
    print(f"Экспортировано в {path}")

    # export_excel.py

import pandas as pd
from corpus_db import get_corpus

def export_to_excel(path="corpus/corpus.xlsx"):
    corpus = get_corpus()
    data = []
    for entry in corpus:
        for tok in entry["tokens"]:
            word = tok["word"]
            lemma = tok.get("lemma", word.lower())
            tags = tok.get("tags", [])
            upos = tags[0] if tags else "X"
            feats = "|".join(tags[1:]) if len(tags) > 1 else "_"
            data.append({
                "sentence": entry["text"],
                "token": word,
                "lemma": lemma,
                "upos": upos,
                "features": feats
            })
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
    return path

if __name__ == "__main__":
    print("Экспортировано в", export_to_excel())

    # export_jsonl.py

import json
from corpus_db import get_corpus

def export_to_jsonl(path="corpus/corpus.jsonl"):
    corpus = get_corpus()
    with open(path, "w", encoding="utf-8") as f:
        for entry in corpus:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path

if __name__ == "__main__":
    print("Экспортировано в", export_to_jsonl())


# export_csv.py

import csv
from corpus_db import get_corpus

def export_to_csv(path="corpus/corpus.csv"):
    corpus = get_corpus()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sentence", "token", "lemma", "upos", "features"])
        for entry in corpus:
            for token in entry["tokens"]:
                word = token["word"]
                lemma = token.get("lemma", word.lower())
                tags = token.get("tags", [])
                upos = tags[0] if tags else "X"
                feats = "|".join(tags[1:]) if len(tags) > 1 else "_"
                writer.writerow([entry["text"], word, lemma, upos, feats])
    return path

if __name__ == "__main__":
    print("Экспортировано в", export_to_csv())


    #################

    # Добавим скрипты экспорта в папку проекта

export_csv = """
# export_csv.py

import csv
from corpus_db import get_corpus

def export_to_csv(path="corpus/corpus.csv"):
    corpus = get_corpus()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sentence", "token", "lemma", "upos", "features"])
        for entry in corpus:
            for token in entry["tokens"]:
                word = token["word"]
                lemma = token.get("lemma", word.lower())
                tags = token.get("tags", [])
                upos = tags[0] if tags else "X"
                feats = "|".join(tags[1:]) if len(tags) > 1 else "_"
                writer.writerow([entry["text"], word, lemma, upos, feats])
    return path

if __name__ == "__main__":
    print("Экспортировано в", export_to_csv())
"""

export_jsonl = """
# export_jsonl.py

import json
from corpus_db import get_corpus

def export_to_jsonl(path="corpus/corpus.jsonl"):
    corpus = get_corpus()
    with open(path, "w", encoding="utf-8") as f:
        for entry in corpus:
            f.write(json.dumps(entry, ensure_ascii=False) + "\\n")
    return path

if __name__ == "__main__":
    print("Экспортировано в", export_to_jsonl())
"""

export_excel = """
# export_excel.py

import pandas as pd
from corpus_db import get_corpus

def export_to_excel(path="corpus/corpus.xlsx"):
    corpus = get_corpus()
    data = []
    for entry in corpus:
        for tok in entry["tokens"]:
            word = tok["word"]
            lemma = tok.get("lemma", word.lower())
            tags = tok.get("tags", [])
            upos = tags[0] if tags else "X"
            feats = "|".join(tags[1:]) if len(tags) > 1 else "_"
            data.append({
                "sentence": entry["text"],
                "token": word,
                "lemma": lemma,
                "upos": upos,
                "features": feats
            })
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
    return path

if __name__ == "__main__":
    print("Экспортировано в", export_to_excel())
"""

# Сохраняем файлы
with open("/mnt/data/morpho_corpus_template/export_csv.py", "w", encoding="utf-8") as f:
    f.write(export_csv.strip())

with open("/mnt/data/morpho_corpus_template/export_jsonl.py", "w", encoding="utf-8") as f:
    f.write(export_jsonl.strip())

with open("/mnt/data/morpho_corpus_template/export_excel.py", "w", encoding="utf-8") as f:
    f.write(export_excel.strip())

# Обновим архив проекта
shutil.make_archive("/mnt/data/morpho_corpus_project", 'zip', "/mnt/data/morpho_corpus_template")
"/mnt/data/morpho_corpus_project.zip"




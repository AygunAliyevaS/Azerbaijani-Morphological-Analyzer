# annotator_ui.py — веб-интерфейс для морфоанализа с экспортом в CSV/JSON и CoNLL-U

import gradio as gr
import json
import csv
from datetime import datetime
import os

from morpho_engine import analyze_word
from exporter import export_to_conllu

EXPORT_PATH = "exports"

def save_result(word, results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{EXPORT_PATH}/analyze_{timestamp}"

    # JSON
    with open(base_filename + ".json", "w", encoding="utf-8") as jf:
        json.dump({"word": word, "results": results}, jf, indent=2, ensure_ascii=False)

    # CSV
    with open(base_filename + ".csv", "w", encoding="utf-8", newline="") as cf:
        writer = csv.writer(cf)
        writer.writerow(["word", "root", "gloss", "analysis", "tags"])
        for r in results:
            writer.writerow([word, r["root"], r["gloss"], r["analysis"], " + ".join(r["tags"])])

def analyze_input(word):
    results = analyze_word(word)
    if "error" in results[0]:
        return f"Ошибка: {results[0]['error']}", None
    # сохраняем JSON/CSV
    save_result(word, results)
    # сохраняем CoNLL-U: упакуем как единичное предложение
    sentence = {
        "text": word,
        "tokens": [
            {
                "word": word,
                "analysis": r["analysis"],
                "root": r["root"],
                "tags": r["tags"],
                # можно добавить UPOS при наличии
            }
            for r in results
        ]
    }
    # создаём папку и файл
    conllu_path = f"{EXPORT_PATH}/corpus.conllu"
    # если файла ещё нет, создаём чистый
    if not os.path.exists(conllu_path):
        open(conllu_path, "w", encoding="utf-8").close()
    # дописываем в общий корпус
    export_to_conllu([sentence], conllu_path)

    # Формируем вывод
    output = ""
    for r in results:
        output += f"Корень: {r['root']} ({r['gloss']})\n"
        output += f"Анализ: {r['analysis']}\n"
        output += f"Теги: {' + '.join(r['tags'])}\n\n"
    return output.strip(), f"Saved to {conllu_path}"

iface = gr.Interface(
    fn=analyze_input,
    inputs=gr.Textbox(label="Введите слово"),
    outputs=[
        gr.Textbox(label="Результат разбора"),
        gr.Textbox(label="Экспорт CoNLL-U")
    ],
    title="Морфологический разбор (Азербайджанский)",
    description="Агглютинативный морфоанализатор с экспортом в CSV/JSON и CoNLL-U"
)

if __name__ == "__main__":
    os.makedirs(EXPORT_PATH, exist_ok=True)
    iface.launch()
#################

# exporter.py — шаблон модуля
# Добавим модифицированный annotator_ui.py с возможностью экспорта результатов в CSV и JSON

annotator_ui_code = """
# annotator_ui.py — веб-интерфейс для морфоанализа с экспортом

import gradio as gr
import json
import csv
from datetime import datetime
from morpho_engine import analyze_word

EXPORT_PATH = "exports"

def save_result(word, results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{EXPORT_PATH}/analyze_{timestamp}"

    # Сохраняем как JSON
    with open(base_filename + ".json", "w", encoding="utf-8") as jf:
        json.dump({"word": word, "results": results}, jf, indent=2, ensure_ascii=False)

    # Сохраняем как CSV
    with open(base_filename + ".csv", "w", encoding="utf-8", newline="") as cf:
        writer = csv.writer(cf)
        writer.writerow(["word", "root", "gloss", "analysis", "tags"])
        for r in results:
            writer.writerow([word, r["root"], r["gloss"], r["analysis"], " + ".join(r["tags"])])

def analyze_input(word):
    results = analyze_word(word)
    if "error" in results[0]:
        return f"Ошибка: {results[0]['error']}"
    save_result(word, results)
    output = ""
    for r in results:
        output += f"Корень: {r['root']} ({r['gloss']})\\n"
        output += f"Анализ: {r['analysis']}\\n"
        output += f"Теги: {' + '.join(r['tags'])}\\n\\n"
    return output.strip()

iface = gr.Interface(
    fn=analyze_input,
    inputs=gr.Textbox(label="Введите слово"),
    outputs=gr.Textbox(label="Результат разбора"),
    title="Морфологический разбор (Азербайджанский)",
    description="Агглютинативный морфоанализатор с возможностью экспорта в CSV/JSON"
)

if __name__ == "__main__":
    import os
    os.makedirs(EXPORT_PATH, exist_ok=True)
    iface.launch()
"""

# Сохраним в файл
with open("/mnt/data/morpho_corpus_template/annotator_ui.py", "w", encoding="utf-8") as f:
    f.write(annotator_ui_code.strip())

"/mnt/data/morpho_corpus_template/annotator_ui.py"

# Создадим модуль exporter.py с функцией экспорта в формат CoNLL-U
exporter_code = """
# exporter.py — модуль для экспорта анализов корпуса в формат CoNLL-U

from typing import List, Dict
import os

def to_conllu_sentence(word: str, analysis: Dict, token_id: int = 1) -> str:
    \"\"\"Преобразует анализ одного слова в строку формата CoNLL-U.\"\"\"
    # В CoNLL-U: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC
    form = analysis['analysis'].replace('+', '')
    lemma = analysis['root']
    upos = analysis.get('upos', '_')
    xpos = '_'
    feats = '|'.join(analysis['tags']) if analysis.get('tags') else '_'
    head = '_'
    deprel = '_'
    deps = '_'
    misc = '_'
    return f\"{token_id}\\t{word}\\t{lemma}\\t{upos}\\t{xpos}\\t{feats}\\t{head}\\t{deprel}\\t{deps}\\t{misc}\"

def export_to_conllu(corpus: List[Dict], output_path: str):
    \"\"\"Экспортирует список анализов (corpus) в файл CoNLL-U.\"\"\"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for sentence in corpus:
            # sentence: {'text': str, 'tokens': [{'word': str, 'analysis': str, 'root': str, 'tags': List[str]}]}
            f.write(f\"# text = {sentence['text']}\\n\")
            for idx, token in enumerate(sentence['tokens'], start=1):
                conllu_line = to_conllu_sentence(token['word'], token)
                f.write(conllu_line + \"\\n\")
            f.write(\"\\n\")
"""

# Сохраним в файл
with open("/mnt/data/morpho_corpus_template/exporter.py", "w", encoding="utf-8") as f:
    f.write(exporter_code.strip())

"/mnt/data/morpho_corpus_template/exporter.py"


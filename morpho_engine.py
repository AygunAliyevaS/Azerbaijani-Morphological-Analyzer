# morpho_engine.py — шаблон модуля морфологического анализа

import json

# Загрузка словаря
with open("roots.json", encoding="utf-8") as f:
    ROOTS = json.load(f)

with open("affixes.json", encoding="utf-8") as f:
    AFFIXES = json.load(f)

def analyze_word(word):
    results = []
    for root in ROOTS:
        if word.startswith(root):
            remaining = word[len(root):]
            tags = []
            form = root
            while remaining:
                matched = False
                for affix in sorted(AFFIXES.keys(), key=lambda x: -len(x)):
                    if remaining.startswith(affix):
                        tags.append(AFFIXES[affix]["tag"])
                        form += "+" + affix
                        remaining = remaining[len(affix):]
                        matched = True
                        break
                if not matched:
                    break
            if not remaining:
                results.append({
                    "root": root,
                    "gloss": ROOTS[root]["gloss"],
                    "analysis": form,
                    "tags": tags
                })
    return results or [{"error": "Разбор не найден"}]

# morpho_engine.py — шаблон модуля
import gradio as gr
import graphviz
from PIL import Image
import io

# Морфологические данные
ROOTS = {"yaz": "write"}
AFFIXES = {
    "dır": "CAUS", "ıl": "PASS", "acaq": "FUT", "mış": "EVID"
}
VALID_CHAIN = ["CAUS", "PASS", "FUT", "EVID"]

def analyze_and_draw(word):
    for root in ROOTS:
        if word.startswith(root):
            remaining = word[len(root):]
            analysis = []
            while remaining:
                matched = False
                for affix, tag in AFFIXES.items():
                    if remaining.startswith(affix):
                        analysis.append((affix, tag))
                        remaining = remaining[len(affix):]
                        matched = True
                        break
                if not matched:
                    return f"Unrecognized part: '{remaining}'", None
            tags = [tag for (_, tag) in analysis]
            if tags != VALID_CHAIN:
                return f"Invalid affix sequence: {tags}", None

            # Построение графа
            dot = graphviz.Digraph()
            dot.attr(rankdir='LR')
            dot.node("root", f"{root}\n(ROOT)")
            previous = "root"
            for i, (affix, tag) in enumerate(analysis):
                node_id = f"affix_{i}"
                dot.node(node_id, f"{affix}\n({tag})")
                dot.edge(previous, node_id)
                previous = node_id

            # Конвертация в изображение
            img_bytes = dot.pipe(format="png")
            img = Image.open(io.BytesIO(img_bytes))
            return f"Root: {root}, Affixes: {analysis}", img
    return "Root not found", None

# Интерфейс Gradio
iface = gr.Interface(
    fn=analyze_and_draw,
    inputs=gr.Textbox(label="Введите слово"),
    outputs=[
        gr.Textbox(label="Результат анализа"),
        gr.Image(type="pil", label="Граф морфоанализа")
    ],
    title="Морфоанализ агглютинативного слова",
    description="Введите слово на азербайджанском (например, yazdırılacaqmış), чтобы увидеть его морфемную структуру и грамматические категории."
)

iface.launch()



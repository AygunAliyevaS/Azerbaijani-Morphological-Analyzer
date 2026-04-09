# train_ui.py — интерфейс запуска обучения модели тегов

import gradio as gr
from ml_models import train_tag_predictor

def train_model_interface():
    model = train_tag_predictor()
    if model is not None:
        return "Обучение завершено. Модель сохранена."
    else:
        return "Не удалось обучить модель. Возможно, корпус пуст."

iface = gr.Interface(
    fn=train_model_interface,
    inputs=[],
    outputs="text",
    title="Обучение морфологической модели",
    description="Нажмите кнопку для обучения модели морфологических тегов на текущем корпусе."
)

if __name__ == "__main__":
    iface.launch()



    #########
    
# После сброса среды пересоздаём файл train_ui.py

train_ui_code = """
# train_ui.py — интерфейс запуска обучения модели тегов

import gradio as gr
from ml_models import train_tag_predictor

def train_model_interface():
    model = train_tag_predictor()
    if model is not None:
        return "Обучение завершено. Модель сохранена."
    else:
        return "Не удалось обучить модель. Возможно, корпус пуст."

iface = gr.Interface(
    fn=train_model_interface,
    inputs=[],
    outputs="text",
    title="Обучение морфологической модели",
    description="Нажмите кнопку для обучения модели морфологических тегов на текущем корпусе."
)

if __name__ == "__main__":
    iface.launch()
"""

import os
os.makedirs("/mnt/data/morpho_corpus_template", exist_ok=True)
with open("/mnt/data/morpho_corpus_template/train_ui.py", "w", encoding="utf-8") as f:
    f.write(train_ui_code.strip())

"/mnt/data/morpho_corpus_template/train_ui.py"

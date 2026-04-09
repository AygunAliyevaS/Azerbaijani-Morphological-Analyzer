# Gradio UI for the multilingual morphological analyzer
import gradio as gr
from text_input import tokenize, normalize
from ml_models import analyze_word


LANG_OPTIONS = [
    ("Azerbaijani", "az"),
    ("Turkish", "tr"),
    ("Russian", "ru"),
]


def analyze_sentence(sentence: str, lang_code: str):
    tokens = [normalize(t) for t in tokenize(sentence)]
    table = []
    details = []
    spans = []
    for tok in tokens:
        result = analyze_word(tok, lang_code)
        pos = result.get("POS", "UNK")
        feats = result.get("features", {}) or {}
        feat_str = ", ".join(f"{k}={v}" for k, v in feats.items()) if feats else "—"
        table.append([tok, pos, feat_str])
        details.append(result)
        spans.append((tok, pos))
    return table, details, spans


with gr.Blocks(theme="soft") as demo:
    gr.Markdown("## Multilingual Morphological Analyzer")
    gr.Markdown(
        "Type a sentence and choose a language. Tokens are normalized and looked up in the dictionaries. "
        "Unknown words are marked with POS=UNK."
    )

    with gr.Row():
        sentence = gr.Textbox(
            label="Sentence",
            placeholder="Mətn daxil edin… / Enter a sentence…",
            lines=2,
        )
        lang = gr.Dropdown(
            choices=[code for _, code in LANG_OPTIONS],
            value="az",
            label="Language",
        )
    submit = gr.Button("Analyze", variant="primary")

    table = gr.Dataframe(
        headers=["Token", "POS", "Features"],
        datatype=["str", "str", "str"],
        wrap=True,
        label="Token analysis",
    )
    highlight = gr.HighlightedText(label="POS tags (UNK in red)", color_map={"UNK": "#e45757"})
    raw = gr.JSON(label="Raw results")

    gr.Examples(
        examples=[
            ["Bu kitab maraqlıdır və müəllif gəncdir.", "az"],
            ["Sən nə vaxt gələcəksən?", "az"],
            ["Bugün hava çok güzel ama biraz rüzgar var.", "tr"],
            ["Yeni bir kitap aldım ve hemen okumaya başladım.", "tr"],
            ["Сегодня погода холодная, но солнечная.", "ru"],
            ["Это простое предложение для проверки.", "ru"],
        ],
        inputs=[sentence, lang],
        label="Examples",
    )

    submit.click(analyze_sentence, [sentence, lang], [table, raw, highlight])


if __name__ == "__main__":
    # share=False to avoid public tunneling; toggle if localhost is blocked
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Blueprint, render_template, request
from text_input import tokenize, normalize
from ml_models import analyze_word

bp = Blueprint('sentence_analyzer', __name__)

def analyze_sentence(sentence, lang_code):
    tokens = [normalize(t) for t in tokenize(sentence)]
    table = []
    for tok in tokens:
        result = analyze_word(tok, lang_code)
        pos = result.get("POS", "UNK")
        feats = result.get("features", {}) or {}
        feat_str = ", ".join(f"{k}={v}" for k, v in feats.items()) if feats else "—"
        table.append([tok, pos, feat_str])
    return {"table": table}

@bp.route('/sentence-analyzer', methods=['GET', 'POST'])
def sentence_analyzer():
    result = None
    if request.method == 'POST':
        sentence = request.form.get('sentence', '')
        # Force Azerbaijani analysis to keep the analyzer single-language
        result = analyze_sentence(sentence, 'az')
    return render_template('sentence_analyzer.html', result=result)

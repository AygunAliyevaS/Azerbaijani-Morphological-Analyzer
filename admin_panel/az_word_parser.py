from flask import Blueprint, render_template, request
import json
import os

bp = Blueprint('az_word_parser', __name__)

# Simple Azerbaijani morpheme parser using roots and affixes
DATA_DIR = os.path.join(os.path.dirname(__file__), '..')
ROOTS_PATH = os.path.join(DATA_DIR, 'roots.json')
AFFIXES_PATH = os.path.join(DATA_DIR, 'affixes.json')

with open(ROOTS_PATH, encoding='utf-8') as f:
    ROOTS = json.load(f)
with open(AFFIXES_PATH, encoding='utf-8') as f:
    AFFIXES = json.load(f)

def parse_az_word(word):
    for root in ROOTS:
        if word.startswith(root):
            remaining = word[len(root):]
            parts = [root]
            tags = []
            while remaining:
                matched = False
                for affix in sorted(AFFIXES.keys(), key=lambda x: -len(x)):
                    if remaining.startswith(affix):
                        tags.append(AFFIXES[affix]["tag"])
                        parts.append(affix)
                        remaining = remaining[len(affix):]
                        matched = True
                        break
                if not matched:
                    break
            if not remaining:
                return {
                    "root": root,
                    "affixes": parts[1:],
                    "tags": tags
                }
    return {"error": "No analysis found"}

@bp.route('/az-word-parser', methods=['GET', 'POST'])
def az_word_parser():
    result = None
    word = ''
    if request.method == 'POST':
        word = request.form.get('word', '')
        result = parse_az_word(word)
    return render_template('az_word_parser.html', word=word, result=result)

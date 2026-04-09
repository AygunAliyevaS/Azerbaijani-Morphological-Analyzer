from flask import Blueprint, render_template, request, session, redirect, url_for
import os
import json
from pathlib import Path

bp = Blueprint('dashboard', __name__)

def parse_az_word(word, roots, affixes):
    for root in roots:
        if word.startswith(root):
            remaining = word[len(root):]
            parts = [root]
            tags = []
            while remaining:
                matched = False
                for affix in sorted(affixes.keys(), key=lambda x: -len(x)):
                    if remaining.startswith(affix):
                        tags.append(affixes[affix]["tag"])
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


@bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    stats = {}
    # Dictionary stats
    dict_dir = os.path.join(base_dir, 'dictionaries')
    stats['dictionaries'] = {}
    for lang in ['az', 'tr', 'ru']:
        path = os.path.join(dict_dir, f'{lang}.json')
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
                stats['dictionaries'][lang] = len(data)
        except Exception:
            stats['dictionaries'][lang] = 0
    # Affixes
    try:
        with open(os.path.join(base_dir, 'affixes.json'), encoding='utf-8') as f:
            stats['affixes'] = len(json.load(f))
    except Exception:
        stats['affixes'] = 0
    # Rules
    try:
        rules_path = os.path.join(base_dir, 'rules.json')
        all_rules = _load_rules_file(rules_path)
        stats['rules'] = sum(len(v) for v in all_rules.values() if isinstance(v, list))
    except Exception:
        all_rules = {}
        stats['rules'] = 0

    # Dictionary selection logic
    selected_dictionary = session.get('selected_dictionary', 'az')
    if request.method == 'POST':
        # If dictionary selection form was submitted
        if 'dictionary' in request.form:
            selected_dictionary = request.form['dictionary']
            session['selected_dictionary'] = selected_dictionary
            # Redirect to avoid form resubmission
            return redirect(url_for('dashboard.dashboard'))

    # Get rules for selected dictionary
    rules = all_rules.get(f'{selected_dictionary}_rules', [])

    # Morphological analyzer section
    word = ''
    result = None
    if request.method == 'POST' and 'word' in request.form:
        word = request.form.get('word', '').strip()
        try:
            with open(os.path.join(base_dir, 'roots.json'), encoding='utf-8') as f:
                roots = json.load(f)
            with open(os.path.join(base_dir, 'affixes.json'), encoding='utf-8') as f:
                affixes = json.load(f)
            result = parse_az_word(word, roots, affixes)
        except Exception as e:
            result = {"error": f"Error: {e}"}

    return render_template(
        'dashboard.html',
        stats=stats,
        word=word,
        result=result,
        selected_dictionary=selected_dictionary,
        rules=rules
    )


def _load_rules_file(rules_path):
    """Load rules.json tolerantly (ignores trailing debug blocks/comments)."""
    try:
        with open(rules_path, encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        try:
            raw = Path(rules_path).read_text(encoding='utf-8')
            head = raw.split('###########', 1)[0].strip()
            return json.loads(head) if head else {}
        except Exception:
            return {}
    except Exception:
        return {}

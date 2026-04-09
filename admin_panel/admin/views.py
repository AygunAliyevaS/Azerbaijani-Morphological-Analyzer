from flask import render_template, request, redirect, url_for, session
from . import bp
import json
import os
from pathlib import Path

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def _load_rules_file(rules_path):
    """Load rules.json tolerantly (ignores trailing debug blocks/comments)."""
    try:
        with open(rules_path, encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        try:
            raw = Path(rules_path).read_text(encoding='utf-8')
            # Ignore anything after a splitter line if present
            head = raw.split('###########', 1)[0].strip()
            return json.loads(head) if head else {}
        except Exception:
            return {}
    except Exception:
        return {}


def _collect_stats():
    """Return aggregate counts for dictionaries, affixes and rules."""
    stats = {'dictionaries': {}}
    dict_dir = os.path.join(BASE_DIR, 'dictionaries')
    for lang in ['az', 'tr', 'ru']:
        path = os.path.join(dict_dir, f'{lang}.json')
        try:
            with open(path, encoding='utf-8') as f:
                stats['dictionaries'][lang] = len(json.load(f))
        except Exception:
            stats['dictionaries'][lang] = 0

    try:
        with open(os.path.join(BASE_DIR, 'affixes.json'), encoding='utf-8') as f:
            stats['affixes'] = len(json.load(f))
    except Exception:
        stats['affixes'] = 0

    try:
        all_rules = _load_rules_file(os.path.join(BASE_DIR, 'rules.json'))
        stats['rules'] = sum(len(v) for v in all_rules.values() if isinstance(v, list))
    except Exception:
        stats['rules'] = 0

    return stats


@bp.route('/')
def admin_dashboard():
    stats = _collect_stats()
    return render_template('admin/dashboard.html', stats=stats)

@bp.route('/dictionaries', methods=['GET', 'POST'])
def manage_dictionaries():
    dict_path = os.path.join(BASE_DIR, 'dictionaries', 'az.json')
    entries = []
    data = {}
    if os.path.exists(dict_path):
        with open(dict_path, encoding='utf-8') as f:
            data = json.load(f)
            for word, entry in data.items():
                entries.append({'word': word, 'POS': entry.get('POS', ''), 'Features': entry.get('Features', {})})

    # Add entry
    if request.method == 'POST' and request.form.get('action') == 'add':
        word = request.form.get('word', '').strip()
        pos = request.form.get('POS', '').strip()
        features = request.form.get('Features', '').strip()
        try:
            features_dict = json.loads(features) if features else {}
        except Exception:
            features_dict = {}
        if word and pos:
            data[word] = {'POS': pos, 'Features': features_dict}
            with open(dict_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return redirect(url_for('.manage_dictionaries'))

    # Delete entry
    if request.method == 'POST' and request.form.get('action') == 'delete':
        word = request.form.get('word', '').strip()
        if word in data:
            del data[word]
            with open(dict_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return redirect(url_for('.manage_dictionaries'))

    return render_template('admin/dictionaries.html', entries=entries)

@bp.route('/affixes', methods=['GET', 'POST'])
def manage_affixes():
    affixes_path = os.path.join(BASE_DIR, 'affixes.json')
    affixes = []
    if os.path.exists(affixes_path):
        with open(affixes_path, encoding='utf-8') as f:
            data = json.load(f)
            affixes = [
                {'affix': k, 'tag': v.get('tag', ''), 'pos': v.get('pos', '')}
                for k, v in data.items()
            ]
    # Handle add
    if request.method == 'POST' and request.form.get('action') == 'add':
        affix = request.form.get('affix', '').strip()
        tag = request.form.get('tag', '').strip()
        pos = request.form.get('pos', '').strip()
        if affix and tag:
            data[affix] = {'tag': tag, 'pos': pos}
            with open(affixes_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return redirect(url_for('.manage_affixes'))
    # Handle delete
    if request.method == 'POST' and request.form.get('action', '') == 'delete':
        affix = request.form.get('affix', '').strip()
        if affix in data:
            del data[affix]
            with open(affixes_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return redirect(url_for('.manage_affixes'))
    return render_template('admin/affixes.html', affixes=affixes)

@bp.route('/rules', methods=['GET', 'POST'])
def manage_rules():
    rules_path = os.path.join(BASE_DIR, 'rules.json')
    rules = []
    rules_blob = _load_rules_file(rules_path) if os.path.exists(rules_path) else {}
    rules = rules_blob.get('az_rules', [])
    if request.method == 'POST':
        # Add new rule
        tag = request.form.get('tag', '').strip()
        desc = request.form.get('desc', '').strip()
        example = request.form.get('example', '').strip()
        if tag and desc:
            rules.append({'tag': tag, 'desc': desc, 'example': example})
            payload = {'az_rules': rules}
            # Preserve other keys (e.g., valid_order) if they existed
            for k, v in rules_blob.items():
                if k not in payload:
                    payload[k] = v
            with open(rules_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
    return render_template('admin/rules.html', rules=rules)

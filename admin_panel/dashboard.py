from flask import Blueprint, render_template, request, session, redirect, url_for
import os
import json

from models import DashboardStatsCollector, RuleManager, normalize_language

bp = Blueprint('dashboard', __name__)


@bp.before_request
def require_login():
    if 'user' not in session:
        return redirect(url_for('auth.login'))


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
    selected_dictionary = normalize_language(request.args.get('lang') or session.get('selected_dictionary', 'az'))
    if request.method == 'POST':
        if 'dictionary' in request.form:
            selected_dictionary = normalize_language(request.form['dictionary'])
            session['selected_dictionary'] = selected_dictionary
            return redirect(url_for('dashboard.dashboard', lang=selected_dictionary))

    stats = DashboardStatsCollector().collect(selected_dictionary)
    rules = RuleManager().get_rules(selected_dictionary)

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

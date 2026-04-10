from flask import render_template, request, redirect, url_for, session
from . import bp
import json
import os
from models import (
    AffixManager,
    DashboardStatsCollector,
    DictionaryManager,
    LANGUAGES,
    LANGUAGE_LABELS,
    RuleManager,
    normalize_language,
)


def _selected_language():
    selected_language = request.args.get('lang') or session.get('admin_language') or 'az'
    selected_language = normalize_language(selected_language)
    session['admin_language'] = selected_language
    return selected_language


@bp.route('/')
def admin_dashboard():
    selected_language = _selected_language()
    stats = DashboardStatsCollector().collect(selected_language)
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        selected_language=selected_language,
        language_labels=LANGUAGE_LABELS,
    )

@bp.route('/dictionaries', methods=['GET', 'POST'])
def manage_dictionaries():
    selected_language = _selected_language()
    dictionary_manager = DictionaryManager(selected_language)
    data = dictionary_manager.load()

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
            dictionary_manager.save(data)
            return redirect(url_for('.manage_dictionaries', lang=selected_language))

    if request.method == 'POST' and request.form.get('action') == 'delete':
        word = request.form.get('word', '').strip()
        if word in data:
            del data[word]
            dictionary_manager.save(data)
            return redirect(url_for('.manage_dictionaries', lang=selected_language))

    stats = DashboardStatsCollector().collect(selected_language)
    return render_template(
        'admin/dictionaries.html',
        entries=dictionary_manager.list_entries(),
        selected_language=selected_language,
        selected_language_label=LANGUAGE_LABELS[selected_language],
        available_languages=LANGUAGES,
        stats=stats,
    )

@bp.route('/affixes', methods=['GET', 'POST'])
def manage_affixes():
    selected_language = _selected_language()
    affix_manager = AffixManager()
    data = affix_manager.load()
    if request.method == 'POST' and request.form.get('action') == 'add':
        affix = request.form.get('affix', '').strip()
        tag = request.form.get('tag', '').strip()
        pos = request.form.get('pos', '').strip()
        if affix and tag:
            data[affix] = {'tag': tag, 'pos': pos}
            affix_manager.save(data)
            return redirect(url_for('.manage_affixes'))

    if request.method == 'POST' and request.form.get('action', '') == 'delete':
        affix = request.form.get('affix', '').strip()
        if affix in data:
            del data[affix]
            affix_manager.save(data)
            return redirect(url_for('.manage_affixes'))

    return render_template(
        'admin/affixes.html',
        affixes=affix_manager.list_affixes(),
        selected_language=selected_language,
    )

@bp.route('/rules', methods=['GET', 'POST'])
def manage_rules():
    selected_language = _selected_language()
    rule_manager = RuleManager()
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            try:
                rule_index = int(request.form.get('rule_index', '-1'))
            except ValueError:
                rule_index = -1
            rule_manager.delete_rule(selected_language, rule_index)
            return redirect(url_for('.manage_rules', lang=selected_language))

        tag = request.form.get('tag', '').strip()
        desc = request.form.get('desc', '').strip()
        example = request.form.get('example', '').strip()
        if tag and desc:
            rules = list(rule_manager.get_rules(selected_language))
            rules.append({'tag': tag, 'desc': desc, 'example': example})
            rule_manager.set_rules(selected_language, rules)
            return redirect(url_for('.manage_rules', lang=selected_language))

    stats = DashboardStatsCollector().collect(selected_language)
    return render_template(
        'admin/rules.html',
        rules=rule_manager.get_rules(selected_language),
        selected_language=selected_language,
        selected_language_label=LANGUAGE_LABELS[selected_language],
        available_languages=LANGUAGES,
        stats=stats,
    )

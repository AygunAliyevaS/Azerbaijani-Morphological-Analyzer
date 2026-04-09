from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import DictionaryManager, AffixManager, RuleManager

bp = Blueprint('crud', __name__)

@bp.route('/dictionaries/<lang>', methods=['GET', 'POST'])
def manage_dictionary(lang):
    manager = DictionaryManager(lang)
    if request.method == 'POST':
        data = request.form.get('data')
        try:
            items = json.loads(data)
            manager.save(items)
            flash('Dictionary updated successfully!')
        except Exception as e:
            flash(f'Error: {e}')
        return redirect(url_for('crud.manage_dictionary', lang=lang))
    items = manager.load()
    return render_template('dictionary.html', lang=lang, items=items)

@bp.route('/affixes', methods=['GET', 'POST'])
def manage_affixes():
    manager = AffixManager()
    if request.method == 'POST':
        data = request.form.get('data')
        try:
            items = json.loads(data)
            manager.save(items)
            flash('Affixes updated successfully!')
        except Exception as e:
            flash(f'Error: {e}')
        return redirect(url_for('crud.manage_affixes'))
    items = manager.load()
    return render_template('affixes.html', items=items)

@bp.route('/rules', methods=['GET', 'POST'])
def manage_rules():
    manager = RuleManager()
    if request.method == 'POST':
        data = request.form.get('data')
        try:
            items = json.loads(data)
            manager.save(items)
            flash('Rules updated successfully!')
        except Exception as e:
            flash(f'Error: {e}')
        return redirect(url_for('crud.manage_rules'))
    items = manager.load()
    return render_template('rules.html', items=items)

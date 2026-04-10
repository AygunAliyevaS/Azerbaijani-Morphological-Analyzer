import werkzeug  # Flask 2.2 expects werkzeug.__version__; missing in Werkzeug 3+
if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "patched"

from flask import Flask, render_template, redirect, url_for, request, session
from auth import bp as auth_bp
from crud import bp as crud_bp
from dashboard import bp as dashboard_bp
from az_word_parser import bp as az_word_parser_bp
from sentence_analyzer import bp as sentence_analyzer_bp
from flask_babel import Babel, gettext as _
from flask_admin import Admin
from flask_admin.base import AdminIndexView
from admin import bp as admin_panel_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['BABEL_DEFAULT_LOCALE'] = 'az'  # default to Azerbaijani

app.config['LANGUAGES'] = ['az', 'ru', 'tr', 'en']
def get_locale():
    # Prefer explicit lang query param, then session, fallback to default
    return request.args.get('lang') or session.get('lang', app.config['BABEL_DEFAULT_LOCALE'])

print('Initializing Babel')
babel = Babel(app, locale_selector=get_locale)
print('Registered Babel')
print('Registering auth_bp')
app.register_blueprint(auth_bp)
print('Registered auth_bp')
print('Registering crud_bp')
app.register_blueprint(crud_bp)
print('Registered crud_bp')
print('Registering dashboard_bp')
app.register_blueprint(dashboard_bp, url_prefix='/admin')
print('Registered dashboard_bp with /admin prefix')
print('Registering az_word_parser_bp')
app.register_blueprint(az_word_parser_bp)
print('Registered az_word_parser_bp')
print('Registering sentence_analyzer_bp')
app.register_blueprint(sentence_analyzer_bp)
print('Registered sentence_analyzer_bp')
print('Registering admin_panel_bp')
app.register_blueprint(admin_panel_bp)
print('Registered admin_panel_bp')
print('Initializing Admin')
admin = Admin(app, name='Morpho Admin', index_view=AdminIndexView(name=_('Dashboard')))
print('Registered Admin')


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')


@app.context_processor
def inject_get_locale():
    # Expose get_locale to Jinja templates
    return dict(get_locale=get_locale)

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in app.config['LANGUAGES']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)

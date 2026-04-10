from flask import Blueprint, redirect, session, url_for

bp = Blueprint('admin_panel', __name__, url_prefix='/admin')


@bp.before_request
def require_login():
    # TEMPORARILY DISABLED FOR DEVELOPMENT
    # if 'user' not in session:
    #     return redirect(url_for('auth.login'))
    pass


from . import views

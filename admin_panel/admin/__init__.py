from flask import Blueprint

bp = Blueprint('admin_panel', __name__, url_prefix='/admin')

from . import views

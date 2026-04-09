from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__)

# Dummy user for demonstration
users = {
    'admin': generate_password_hash('admin123')
}

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_hash = users.get(username)
        if user_hash and check_password_hash(user_hash, password):
            session['user'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))

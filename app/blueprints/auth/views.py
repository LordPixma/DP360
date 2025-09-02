from flask import Blueprint, render_template, redirect, url_for, request

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    return redirect(url_for('dashboard.index'))

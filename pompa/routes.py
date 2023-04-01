from functools import wraps
from flask import render_template, request, redirect, url_for, flash
from pompa import app, db
from pompa.forms import LoginForm, RegisterForm
from pompa import bcrpyt
from pompa.models import User, Permission
from flask_login import login_required, login_user, logout_user, current_user
import json


def login_only_for_guest(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if (current_user.email == 'Guest'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('dashboard'))
    return wrap


def check_permission(required_permissions):
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            if all(permission in current_user.get_all_permissions() for permission in required_permissions):
                return fun(*args, **kwargs)
            else:
                flash('Brak uprawnien!', 'error')
                return redirect(url_for('dashboard'))
        return wrapper
    return decorator


@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user, roles=current_user.get_all_permissions())


@app.route('/login', methods=['POST', 'GET'])
@login_only_for_guest
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.is_submitted():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if bcrpyt.check_password_hash(user.password, form.password.data):
                    login_user(user)
                    flash('Zalogowano', 'success')
                    return redirect(url_for('dashboard'))
            else:
                flash('Błędne dane logowania!', 'error')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
@login_only_for_guest
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.is_submitted():
            hashed_password = bcrpyt.generate_password_hash(form.password.data)
            new_user = User(email=form.email.data, sur_name=form.sur_name.data, name=form.name.data,
                            password=hashed_password, birth_date=form.birth_date.data)
            db.session.add(new_user)
            db.session.commit()
            new_user.submit_changes(new_user.id)
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    flash('Wylogowano', 'success')
    return redirect(url_for('login'))


@app.route('/profile/<id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    user = User.query.filter_by(id=id).first()
    # Change password
    if request.method == 'POST' and (request.form.get('current_operation') == 'password_change'):
        if request.form.get('current_password') and request.form.get('new_password') and request.form.get('password_confirm'):
            if bcrpyt.check_password_hash(user.password, request.form.get('current_password')):
                if request.form.get('new_password') == request.form.get('password_confirm'):
                    if request.form.get('new_password') != request.form.get('current_password'):
                        user.password = bcrpyt.generate_password_hash(
                            request.form.get('new_password'))
                        user.submit_changes(current_user.id)
                        flash('Hasło zmienione poprawnie', 'success')
                        return json.dumps({'response': 'success', 'redirect': url_for('profile', id=current_user.id)})
                    else:
                        return json.dumps({'wrongData': ['new_password', 'current_password'], 'response': 'error', 'message': 'Nowe hasło nie może być takie jak obecne'})
                else:
                    return json.dumps({'wrongData': ['new_password', 'password_confirm'], 'response': 'error', 'message': 'Hasła się nie zgadzają'})
            else:
                return json.dumps({'wrongData': ['current_password'], 'response': 'error', 'message': 'Błędne hasło'})
        else:
            return json.dumps({'wrongData': [item for item in request.form if request.form[item] == ""], 'response': 'error', 'message': 'Pole nie może być puste'})
    # End Change password
    if not user:
        flash('Nie ma takiego użytkownika', 'error')
        return redirect(url_for('dashboard'))
    return render_template('profile.html', user=current_user, viewed_user=user)

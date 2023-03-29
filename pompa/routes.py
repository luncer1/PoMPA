from functools import wraps
from flask import render_template, request, redirect, url_for, flash
from pompa import app, db
from pompa.forms import LoginForm, RegisterForm
from pompa import bcrpyt
from pompa.models import User
from flask_login import login_required, login_user, logout_user, current_user


def login_only_for_guest(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if (current_user.email == 'Guest'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('dashboard'))
    return wrap


@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name, roles=current_user.get_all_permissions())


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
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))

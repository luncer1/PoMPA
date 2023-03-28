from flask import render_template, request, redirect, url_for
import json
from pompa import app, db
from pompa.forms import LoginForm, RegisterForm
from pompa import bcrpyt
from pompa.models import User
from flask_login import login_required, login_user, logout_user, current_user


@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.is_submitted():  # TODO sprawdzić czemu nie dziala dla validate
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrpyt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))

    if (current_user.email == 'Guest'):  # TODO zobaczyć czy nie ma lepszego zabezpieczenia np decoratorem
        return render_template('login.html', form=form)
    else:
        return redirect(url_for('dashboard'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.is_submitted():  # TODO sprawdzić czemu nie dziala dla validate
        hashed_password = bcrpyt.generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, sur_name=form.sur_name.data, name=form.name.data,
                        password=hashed_password, birth_date=form.birth_date.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    if (current_user.email == 'Guest'):  # TODO zobaczyć czy nie ma lepszego zabezpieczenia np decoratorem
        return render_template('register.html', form=form)
    else:
        return redirect(url_for('dashboard'))


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))

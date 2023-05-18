from functools import wraps
from flask import render_template, request, redirect, url_for, flash, jsonify
from pompa import app, db
from pompa.forms import LoginForm, RegisterForm
from pompa import bcrpyt
from pompa.models import User, Permission, Role,Appointment
from flask_login import login_required, login_user, logout_user, current_user
import json
import time
import datetime

create_database = False


def login_only_for_guest(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if (current_user.email == 'Guest'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('dashboard'))
    return wrap


def check_permission(required_permissions):  # ALWAYS PASS LIST AS ARGUMENT
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            if all(permission in current_user.get_all_permissions() for permission in required_permissions):
                return fun(*args, **kwargs)
            else:
                flash('Brak uprawnień!', 'error')
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
    if create_database == True:
        pass
        # db.create_all()
        # db.session.commit()
        # db.session.add(Permission(name="Dodawanie",
        #                created_by=4, modified_by=4))
        # db.session.add(Permission(name="Usuwanie",
        #                created_by=4, modified_by=4))
        # db.session.commit()
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
@check_permission(['Dodawanie'])
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


@app.route('/role-management', methods=['GET'])
@login_required
def role_management():
    all_users = User.query.all()
    all_roles = Role.query.all()

    return render_template('role-management.html', user=current_user, all_users=all_users, all_roles=all_roles)

# ROLE MANAGEMENT API


@app.route('/role-management/user/save-role', methods=['POST'])
def api_role_management_user_save_role():
    if request.method == 'POST':
        selected_user = User.query.filter_by(
            id=request.form.get('user_id')).first()
        if request.form.get('roles') == "":
            selected_roles = ""
        else:
            selected_roles = request.form.get('roles').split(',')

        for role in selected_roles:
            role_object = Role.query.filter_by(name=role).first()
            if role_object not in selected_user.roles:
                selected_user.add_role(role_object)
        selected_user.submit_changes(current_user.id)
        for role in selected_user.roles[:]:
            if role.name not in selected_roles:
                selected_user.remove_role(role)
                selected_user.submit_changes(current_user.id)

        return json.dumps({'user_roles': [role.name for role in selected_user.roles],
                           'user_id': request.form.get('user_id')})


@app.route('/role-management/user/edit-role', methods=['POST'])
def api_role_management_user_edit_role():
    all_roles = Role.query.filter_by(is_active=1).all()
    if request.method == 'POST':
        selected_user = User.query.filter_by(
            id=request.form.get('user_id')).first()
        return json.dumps({'full_name': selected_user.name + " " + selected_user.sur_name,
                           'all_roles': [role.name for role in all_roles],
                           'user_roles': [role.name for role in selected_user.roles],
                           'user_id': request.form.get('user_id')})


@app.route('/role-management/add-role', methods=['POST'])
def api_role_management_add():
    if request.method == 'POST':
        if request.form.get('role_name') == "":
            return json.dumps({'result': 'error', 'message': 'Uzupełnij nazwę roli'})
        elif Role.query.filter_by(name=request.form.get('role_name')).first():
            return json.dumps({'result': 'error', 'message': 'Taka rola już istnieje'})
        else:
            return json.dumps({'result': 'success', 'message': 'Potwierdź'})


@app.route('/role-management/add-role-confirm', methods=['POST'])
def api_role_management_add_confirm():
    if request.method == 'POST':
        if request.form.get('role_name') == "":
            flash('Błąd podczas dodawania roli', 'error')
            return json.dumps({'result': 'error', 'message': 'Uzupełnij nazwę roli'})
        elif Role.query.filter_by(name=request.form.get('role_name')).first():
            flash('Błąd podczas dodawania roli', 'error')
            return json.dumps({'result': 'error', 'message': 'Taka rola już istnieje'})
        else:
            new_role = Role(name=request.form.get(
                'role_name'), is_active=1)
            db.session.add(new_role)
            db.session.commit()
            new_role.submit_changes(current_user.id)
            flash('Rola dodana', 'success')
            return json.dumps({'result': 'success', 'message': 'Potwierdź'})


@app.route('/role-management/edit-role', methods=['POST'])
def api_role_management_edit_role():
    if request.method == 'POST':
        selected_role = Role.query.filter_by(
            id=request.form.get('role_id')).first()
        if selected_role.name == "Admin":
            flash('Nie możesz edytować admina', 'error')
            return '', 400
        return json.dumps({'role': selected_role.name,
                           'is_active': selected_role.is_active,
                           'role_id': selected_role.id
                           })


@app.route('/role-management/save-role', methods=['POST'])
def api_role_management_save_role():
    if request.method == 'POST':
        return_json = {}
        selected_role = Role.query.filter_by(
            id=request.form.get('role_id')).first()
        if request.form.get('is_active') == 'false':
            if len(selected_role.asignees) != 0:
                return json.dumps({
                    'message': "Nie można wyłączyć roli, do której są przypisani użytkownicy", 'error_for': 'switch'}), 400
            else:
                selected_role.is_active = 0
                db.session.commit()
                selected_role.submit_changes(current_user.id)
                return_json['role_id'] = request.form.get('role_id')
                return_json['value'] = '0'
                return_json['role'] = selected_role.name
        if request.form.get('is_active') == 'true' and selected_role.is_active == 0:
            selected_role.is_active = 1
            db.session.commit()
            selected_role.submit_changes(current_user.id)
            return_json['role_id'] = request.form.get('role_id')
            return_json['value'] = '1'
            return_json['role'] = selected_role.name
        if request.form.get('role') != selected_role.name:
            for role in Role.query.all():
                if role.name == request.form.get('role'):
                    return json.dumps({
                        'message': "Nazwa roli musi być unikalna", 'error_for': 'change'}), 400
            selected_role.name = request.form.get('role')
            db.session.commit()
            selected_role.submit_changes(current_user.id)
            return_json['role_id'] = request.form.get('role_id')
            return_json['value'] = selected_role.is_active
            return_json['role'] = selected_role.name
        return json.dumps(return_json), 200


@app.route('/role-management/edit-role-permissions', methods=['POST'])
def api_role_management_edit_role_permissions():
    all_permissions = Permission.query.all()
    if request.method == 'POST':
        selected_role = Role.query.filter_by(
            id=request.form.get('role_id')).first()
        if selected_role.name == "Admin":
            flash('Nie możesz edytować admina', 'error')
            return '', 400
        return json.dumps({'role': selected_role.name,
                           'all_permissions': [permission.name for permission in all_permissions],
                           'role_permissions': [permission.name for permission in selected_role.permissions],
                           'role_id': selected_role.id
                           })


@app.route('/role-management/save-role-permissions', methods=['POST'])
def api_role_management_save_role_permissions():
    if request.method == 'POST':
        selected_role = Role.query.filter_by(
            id=request.form.get('role_id')).first()
        if request.form.get('permissions') == "":
            selected_permissions = ""
        else:
            selected_permissions = request.form.get('permissions').split(',')

        for permission in selected_permissions:
            permission_object = Permission.query.filter_by(
                name=permission).first()
            if permission_object not in selected_role.permissions:
                selected_role.add_permission(permission_object)
        selected_role.submit_changes(current_user.id)
        for permission in selected_role.permissions[:]:
            if permission.name not in selected_permissions:
                selected_role.remove_permission(permission)
                selected_role.submit_changes(current_user.id)
        flash('Prawa zapisane', 'success')
        return json.dumps({'role': 'asd'
                           }), 200

# THERAPISTS


@app.route('/therapists', methods=['GET', 'POST'])
@check_permission(['Dodawanie'])
def therapists():
    therapist = Role.query.filter_by(name="Terapeuta").first()
    therapists = []
    for user in User.query.all():
        if therapist in user.roles:
            therapists.append(user)
    return render_template('therapist_list.html', user=current_user, therapists=therapists)


@app.route('/calendar/<id>', methods=['GET', 'POST'])
@check_permission(['Dodawanie'])
def therapist_calendar(id):
    user = User.query.filter_by(id=id).first()
    appointments = []
    read_only = True
    if (current_user == user) or current_user.has_permission("Usuwanie"): #TODO: Dodać odpowiednie uprawnienie
        read_only = False
        for appointment in user.appointments:
            appointments.append({"event_date": f"{appointment.appointment_date.date()}",
                                 "event_id": f"{appointment.id}",
                                "event_time": f"{str(appointment.appointment_date.time())[:-3]}",
                                "event_name": f"{appointment.client_firstname}",
                                "event_surname": f"{appointment.client_lastname}",
                                "event_email": f"{appointment.client_email}",
                                "event_phone": f"{appointment.client_phone_number}",
                                "event_contact_way": f"{appointment.client_contact_form}",
                                "event_status": f"{appointment.status}",})
            
    else:
        for appointment in user.appointments:
            if appointment.client_firstname == "Wolny Termin":
                appointments.append({"event_date": f"{appointment.appointment_date.date()}",
                                     "event_id": f"{appointment.id}",
                                    "event_time": f"{str(appointment.appointment_date.time())[:-3]}",
                                    "event_name": f"{appointment.client_firstname}",
                                    "event_surname": f"{appointment.client_lastname}"})
    return render_template('therapist_calendar.html', user=current_user, viewed_user=user, appointments=appointments, read_only=read_only)

@app.route('/calendar/<id>/addevent', methods=['GET', 'POST'])
@check_permission(['Dodawanie'])
def calendar_api_add_event(id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        if (current_user == user) or current_user.has_permission("Usuwanie"): #TODO: Dodać odpowiednie uprawnienie
            cyclic = 1
            if request.form.get('event_cyclic') == "true":
                cyclic = 4
            cyclic_appointments = []
            for i in range(0,cyclic):
                new_appointment = Appointment(client_firstname=request.form.get('event_name'), client_lastname=request.form.get('event_surname'), client_email=request.form.get('event_email'),
                                    client_phone_number=request.form.get('event_phone'), client_contact_form=request.form.get('event_contact_way'), therapist_id=id,
                                    appointment_date=f"{request.form.get('event_date')} {request.form.get('event_time')}", appointment_location=request.form.get('event_location'),status=request.form.get('event_status'))
                new_appointment.appointment_date = str(datetime.datetime.strptime(new_appointment.appointment_date, '%Y-%m-%d %H:%M') + datetime.timedelta(days=(i*7)))
                if Appointment.query.filter_by(appointment_date=new_appointment.appointment_date, therapist_id=id).first() != None:
                    return json.dumps({'message': 'Juz masz spotkanie w tym terminie'}),400
                elif request.form.get('event_name') == "Wolny Termin" and datetime.datetime.strptime(request.form.get('event_date'),'%Y-%m-%d').date() < datetime.datetime.now().date():
                    return json.dumps({'message': 'Nie możesz dodać wolnego terminu w tym dniu'}),400 
                else:
                    cyclic_appointments.append(new_appointment)
            for item in cyclic_appointments:
                db.session.add(item)
                db.session.commit()
                item.submit_changes(current_user.id)
            return json.dumps({'message': 'Dodano termin', 'events_added': len(cyclic_appointments), 'event_id': [item.id for item in cyclic_appointments]}),200
        else:
            return json.dumps({'message': 'Nie możesz edytować tego kalendarza'}),400
        
        
@app.route('/calendar/<id>/editevent', methods=['GET', 'POST'])
@check_permission(['Dodawanie'])
def calendar_api_edit_event(id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        if (current_user == user) or current_user.has_permission("Usuwanie"): #TODO: Dodać odpowiednie uprawnienie
            appointment = Appointment.query.filter_by(id=request.form.get('event_id')).first()
            appointment.client_firstname = request.form.get('event_name')
            appointment.client_lastname = request.form.get('event_surname')
            appointment.client_email = request.form.get('event_email')
            appointment.client_phone_number = request.form.get('event_phone')
            appointment.client_contact_form = request.form.get('event_contact_way')
            appointment.appointment_date = f"{request.form.get('event_date')} {request.form.get('event_time')}"
            if len(Appointment.query.filter_by(appointment_date=appointment.appointment_date, therapist_id=id).all()) > 1:
                    return json.dumps({'message': 'Juz masz spotkanie w tym terminie'}),400
            appointment.status = request.form.get('event_status')
            appointment.submit_changes(current_user.id)
            return json.dumps({'message': 'Zapisano zmiany'}),200
        else:
            return json.dumps({'message': 'Nie możesz edytować tego kalendarza'}),400
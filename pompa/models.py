from datetime import datetime
from pompa import db
from flask_login import UserMixin

Model_Has_Role = db.Table('Model_Has_Role',
                          db.Column('role_id', db.Integer, db.ForeignKey(
                              'role.id'), primary_key=True, nullable=False),
                          db.Column('user_id', db.Integer, db.ForeignKey(
                              'user.id'), primary_key=True, nullable=False)
                          )
Model_Has_Permission = db.Table('Model_Has_Permission',
                                db.Column('permission_id', db.Integer, db.ForeignKey(
                                    'permission.id'), primary_key=True, nullable=False),
                                db.Column('user_id', db.Integer, db.ForeignKey(
                                    'user.id'), primary_key=True, nullable=False)
                                )
Role_Has_Permission = db.Table('Role_Has_Permission',
                               db.Column('role_id', db.Integer, db.ForeignKey(
                                   'role.id'), primary_key=True, nullable=False),
                               db.Column('permission_id', db.Integer, db.ForeignKey(
                                   'permission.id'), primary_key=True, nullable=False)
                               )


class Permission(db.Model):
    __tablename__ = 'permission'

    id = db.Column(db.Integer,
                   autoincrement='auto', primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column('create_date', db.DateTime,
                            default=datetime.now)
    last_update = db.Column('last_update', db.DateTime, default=datetime.now,
                            onupdate=datetime.now)
    roles = db.relationship(
        'Role', secondary=Role_Has_Permission, backref='permissions')

    def __repr__(self):
        return f"{str(self.name)}"

    def submit_changes(self, user_id):
        if self.created_by == None:
            self.created_by = user_id
        self.modified_by = user_id
        db.session.commit()


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer,
                   autoincrement='auto', primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column('create_date', db.DateTime,
                            default=datetime.now)
    last_update = db.Column('last_update', db.DateTime, default=datetime.now,
                            onupdate=datetime.now)

    def __repr__(self):
        return f"{str(self.name)}"

    def submit_changes(self, user_id):
        if self.created_by == None:
            self.created_by = user_id
        self.modified_by = user_id
        db.session.commit()

    def add_permission(self, permission: Permission):
        if permission not in self.permissions:
            self.permissions.append(permission)
            return 1
        else:
            return 0

    def remove_permission(self, permission: Permission):
        if permission in self.permissions:
            self.permissions.remove(permission)
            return 1
        else:
            return 0


class Note(db.Model):
    __tablename__ = 'note'

    id = db.Column(db.Integer,
                   autoincrement='auto', primary_key=True)
    content = db.Column(db.String(2000), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column('create_date', db.DateTime,
                            default=datetime.now)
    last_update = db.Column('last_update', db.DateTime, default=datetime.now,
                            onupdate=datetime.now)


class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer,
                   autoincrement='auto', primary_key=True)
    client_firstname = db.Column(db.String(50), nullable=False)
    client_lastname = db.Column(db.String(50), nullable=False)
    client_email = db.Column(db.String(200), nullable=False)
    client_phone_number = db.Column(db.Integer, nullable=False) #TODO: change as String(30)
    client_contact_form = db.Column(db.String(100), nullable=False)
    therapist_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    appointment_date = db.Column('appointment_date', db.DateTime)
    appointment_location = db.Column(db.Integer, db.ForeignKey('location.id'))
    status = db.Column(db.String(50), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column('create_date', db.DateTime,
                            default=datetime.now)
    last_update = db.Column('last_update', db.DateTime, default=datetime.now,
                            onupdate=datetime.now)
    
    def __repr__(self):
        return f"Appointment({self.id},{self.client_firstname},{self.client_lastname},{self.therapist})"
    
    def submit_changes(self, user_id):
        if self.created_by == None:
            self.created_by = user_id
        self.modified_by = user_id
        db.session.commit()

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer,
                   autoincrement='auto', primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    sur_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    # phone = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), default="Brak opisu.")
    located_at = db.Column(db.Integer, db.ForeignKey('location.id'))
    photo = db.Column(db.String(500), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column('create_date', db.DateTime,
                            default=datetime.now)
    last_update = db.Column('last_update', db.DateTime, default=datetime.now,
                            onupdate=datetime.now)
    roles = db.relationship(
        'Role', secondary=Model_Has_Role, backref='asignees')
    permissions = db.relationship(
        'Permission', secondary=Model_Has_Permission, backref='asignees')
    notes = db.relationship('Note', backref="user",
                            foreign_keys=[Note.created_by])
    appointments = db.relationship(
        'Appointment', backref='therapist', foreign_keys=[Appointment.therapist_id])

    def __repr__(self):
        return f"User({self.id},{self.name},{self.sur_name},{self.email})"

    def submit_changes(self, user_id):
        if self.created_by == None:
            self.created_by = user_id
        self.modified_by = user_id
        db.session.commit()

    def add_role(self, role: Role):
        if role not in self.roles:
            self.roles.append(role)
            return 1
        else:
            return 0

    def remove_role(self, role: Role):
        if role in self.roles:
            self.roles.remove(role)
            return 1
        else:
            return 0

    def add_permission(self, permission: Permission):
        if permission not in self.permissions:
            self.permissions.append(permission)
            return 1
        else:
            return 0

    def remove_permission(self, permission: Permission):
        if permission in self.permissions:
            self.permissions.remove(permission)
            return 1
        else:
            return 0

    def get_all_permissions(self):
        permissions = []
        for role in self.roles:
            for permission in role.permissions:
                if permission.name not in permissions:
                    permissions.append(permission.name)
        for permission in self.permissions:
            if permission.name not in permissions:
                permissions.append(permission.name)
        return permissions
    
    def has_permission(self, permission_name: str):
        permission = Permission.query.filter_by(name=permission_name).first()
        if permission.name in self.get_all_permissions():
            return True
        else:
            return False


class Location(db.Model):
    __tablename__ = 'location'

    id = db.Column(db.Integer,
                   autoincrement='auto', primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column('create_date', db.DateTime,
                            default=datetime.now)
    last_update = db.Column('last_update', db.DateTime, default=datetime.now,
                            onupdate=datetime.now)
    users = db.relationship('User', backref='location',
                            foreign_keys=[User.located_at])
    appointments = db.relationship('Appointment', backref='location')

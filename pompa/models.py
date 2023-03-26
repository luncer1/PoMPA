from datetime import datetime
from pompa import db

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
        return f"Permission({self.id},{self.name})"

    def submit_changes(self, user_id):
        if self.created_by == None:
            self.created_by = user_id
        self.modified_by = user_id
        db.session.commit()


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer,
                   autoincrement='auto', primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column('create_date', db.DateTime,
                            default=datetime.now)
    last_update = db.Column('last_update', db.DateTime, default=datetime.now,
                            onupdate=datetime.now)

    def __repr__(self):
        return f"Role({self.id},{self.name},Active:{self.is_active})"

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


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer,
                   autoincrement='auto', primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    sur_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
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
                if permission not in permissions:
                    permissions.append(permission)
        for permission in self.permissions:
            if permission not in permissions:
                permissions.append(permission)
        return permissions

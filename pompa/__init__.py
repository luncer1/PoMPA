from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, AnonymousUserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql7606803:eJVv2Ghdaa@sql7.freesqldatabase.com:3306/sql7606803'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sd$sdf45dR565er6DF65drtw43dft65uy8uji6576547'
app.config['SESSION_TYPE'] = 'memcache'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800
db = SQLAlchemy(app)
bcrpyt = Bcrypt(app)


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.email = 'Guest'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.anonymous_user = Anonymous

from pompa.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from pompa import routes

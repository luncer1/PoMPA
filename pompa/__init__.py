from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, AnonymousUserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ba4848ee1380b9:f1a6ce53@us-cdbr-east-06.cleardb.net/heroku_52e6f063e1d4265'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sd$sdf45dR565er6DF65drtw43dft65uy8uji6576547'
app.config['SESSION_TYPE'] = 'memcache'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
db = SQLAlchemy(app)
bcrpyt = Bcrypt(app)


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.email = 'Guest'
        self.name = 'Guest'

    def get_all_permissions(self):
        return {}


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.anonymous_user = Anonymous

from pompa.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from pompa import routes

from wtforms import StringField, PasswordField, SubmitField, DateField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError
from pompa.models import User
from pompa import db
from flask_wtf import FlaskForm
from pompa.models import User


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(
        min=4, max=100)], render_kw={'placeholder': 'Email'})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={'placeholder': 'Hasło'})
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = EmailField(validators=[InputRequired(), Length(
        min=4, max=100)], render_kw={'placeholder': 'Email'})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={'placeholder': 'Hasło'})
    name = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={'placeholder': 'Imie'})
    sur_name = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={'placeholder': 'Nazwisko'})
    birth_date = DateField(validators=[InputRequired()])
    submit = SubmitField('Register')

    def validate_username(self, email):
        existing_user = User.query.filter_by(email=email.data).first()

        if existing_user:
            raise ValidationError('Taki użytkownik już istnieje!')
        else:
            return 1

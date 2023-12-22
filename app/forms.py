from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    nombreUsuario = StringField('NombreUsuario', validators=[DataRequired()])
    contrasena = PasswordField('Contrasena', validators=[DataRequired()])
    recuerda_me = BooleanField('Recuerdame')
    enviar = SubmitField('Iniciar sesion')
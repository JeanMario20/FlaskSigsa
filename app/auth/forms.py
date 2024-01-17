from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flask_babel import _, lazy_gettext as _l
import sqlalchemy as sa
from app import db
from app.models import Usuario

class LoginForm(FlaskForm):
    nombreUsuario = StringField(_l('Usuario:'), validators=[DataRequired()])
    contrasena = PasswordField(_l('Contrasena:'), validators=[DataRequired()])
    recuerda_me = BooleanField(_l('Recuerdame'))
    enviar = SubmitField(_l('Iniciar sesion'))

class RegistrarForm(FlaskForm):
    nombreUsuario = StringField(_l('NombreUsuario'), validators=[DataRequired()])
    correo = StringField(_l('Correo'), validators=[DataRequired(), Email()])
    contrasena = PasswordField(_l('Contrasena'), validators=[DataRequired()])
    contrasena2 = PasswordField(_l('Repita la contraseña'), validators=[DataRequired(), EqualTo('contrasena')])
    enviar = SubmitField(_l('Crear cuenta'))

    def validar_nuevo_usuario(self, nombreUsuario):
        usuario = db.session.scalar(sa.select(Usuario).where(Usuario.nombreUsuario == nombreUsuario.data))
        if usuario is not None:
            raise ValidationError(_l('introduzca un nombre de usuario diferente'))
        
    def validar_correo(self,correo):
        usuario = db.session.scalar(sa.select(Usuario).where(Usuario.correo == correo.data))
        if usuario is not None:
            raise ValidationError(_l('introduzca un correo diferente'))
    

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('correo'), validators=[DataRequired(), Email()])
    enviar = SubmitField(_l('Confirmar reseteo de contraseña'))

class ResetPasswordForm(FlaskForm):
    contrasena = PasswordField(_l('Contraseña'), validators=[DataRequired()])
    contrasena2 = PasswordField(
        _l('Repite la contraseña'), validators=[DataRequired(), EqualTo('contrasena')])
    enviar = SubmitField(_l('Cambio de contraseña'))
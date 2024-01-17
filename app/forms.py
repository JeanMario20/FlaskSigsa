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
    
class EditarPerfilForm(FlaskForm):
    nombreUsuario = StringField(_l("Nombre de usuario "), validators=[DataRequired()])
    acerca_mis = TextAreaField(_l("Acerca de mi"), validators=[Length(min=0, max=140)])
    enviar = SubmitField(_l('Enviar'))

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validar_nombreUsuario(self, nombreUsuario):
        if nombreUsuario != self.original_username:
            usuario = db.session.scalar(sa.select(Usuario).where(Usuario.nombreUsuario == self.nombreUsuario.data))
            if usuario is not None:
                raise ValidationError(_l('el nombre de usuario ya esta en uso porfavor usa un nombre de usuario diferente'))

class EmptyForm(FlaskForm):
    enviar = SubmitField(_l('Enviar'))

class PostForm(FlaskForm):
    post = TextAreaField(_l("En que estas pensando ?") , validators=[DataRequired(), Length(min = 1, max = 140)])
    enviar = SubmitField(_l("Enviar"))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('correo'), validators=[DataRequired(), Email()])
    enviar = SubmitField(_l('Confirmar reseteo de contraseña'))

class ResetPasswordForm(FlaskForm):
    contrasena = PasswordField(_l('Contraseña'), validators=[DataRequired()])
    contrasena2 = PasswordField(
        _l('Repite la contraseña'), validators=[DataRequired(), EqualTo('contrasena')])
    enviar = SubmitField(_l('Cambio de contraseña'))
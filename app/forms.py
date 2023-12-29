from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
import sqlalchemy as sa
from app import db
from app.models import Usuario

class LoginForm(FlaskForm):
    nombreUsuario = StringField('Usuario:', validators=[DataRequired()])
    contrasena = PasswordField('Contrasena:', validators=[DataRequired()])
    recuerda_me = BooleanField('Recuerdame')
    enviar = SubmitField('Iniciar sesion')

class RegistrarForm(FlaskForm):
    nombreUsuario = StringField('NombreUsuario', validators=[DataRequired()])
    correo = StringField('Correo', validators=[DataRequired(), Email()])
    contrasena = PasswordField('Contrasena', validators=[DataRequired()])
    contrasena2 = PasswordField('Repita la contraseña', validators=[DataRequired(), EqualTo('contrasena')])
    enviar = SubmitField('Crear cuenta')

    def validar_nuevo_usuario(self, nombreUsuario):
        usuario = db.session.scalar(sa.select(Usuario).where(Usuario.nombreUsuario == nombreUsuario.data))
        if usuario is not None:
            raise ValidationError('introduzca un nombre de usuario diferente')
        
    def validar_correo(self,correo):
        usuario = db.session.scalar(sa.select(Usuario).where(Usuario.correo == correo.data))
        if usuario is not None:
            raise ValidationError('introduzca un correo diferente')
    
class EditarPerfilForm(FlaskForm):
    nombreUsuario = StringField("Nombre de usuario ", validators=[DataRequired()])
    acerca_mis = TextAreaField("Acerca de mi", validators=[Length(min=0, max=140)])
    enviar = SubmitField('Enviar')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validar_nombreUsuario(self, nombreUsuario):
        if nombreUsuario != self.original_username:
            usuario = db.session.scalar(sa.select(Usuario).where(Usuario.nombreUsuario == self.nombreUsuario.data))
            if usuario is not None:
                raise ValidationError('el nombre de usuario ya esta en uso porfavor usa un nombre de usuario diferente')
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
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
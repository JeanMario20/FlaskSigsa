from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
import sqlalchemy as sa
from flask_babel import _, lazy_gettext as _l
from app import db
from app.models import Usuario
from flask import request

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

class SearchForm(FlaskForm):
    q = StringField( _l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)
from typing import Optional
from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Usuario (UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    nombreUsuario: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,unique=True)
    correo: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    contrasena_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    #apunta a la llave foranea de la clase post
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates = 'autor')

    def __repr__(self):
        return '<usuario {}>' .format(self.nombreUsuario)
    
    def set_contrasena(self, contrasena):
        self.password_hash = generate_password_hash(contrasena)

    def check_contrasena_hash(self ,password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    contenido: so.Mapped[str] = so.mapped_column(sa.String(140))
    tiempo_publicado: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    #llave foranea apunta a la tabla usuarios estan conectados
    # one to many un usuario puede tener muchos posts
    usuario_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Usuario.id), index=True)
    autor: so.Mapped[Usuario] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>' .format(self.contenido) 
    
@login.user_loader
def cargar_usuario(id):
    return db.session.get(Usuario, int(id))
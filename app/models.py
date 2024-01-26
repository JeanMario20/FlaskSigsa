from typing import Optional
from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from flask_login import UserMixin
from flask import current_app
from hashlib import md5
from time import time
from app.search import add_to_index, remove_from_index, query_index
import jwt 

class SearchableMixin(object):
    @classmethod
    def search(cls, expression,page,per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id))
        return db.session.scalars(query), total
    
    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }
    
    @classmethod
    def after_commit(cls,session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None
    
    @classmethod
    def reindex(cls):
        for obj in db.session.scalars(sa.select(cls)):
            add_to_index(cls.__tablename__, obj)
    
db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('usuario.id'), primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('usuario.id'), primary_key=True)
)
class Usuario (UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    nombreUsuario: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,unique=True)
    correo: so.Mapped[str] = so.mapped_column(sa.String(170), index=True, unique=True)
    contrasena_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(170))
    #apunta a la llave foranea de la clase post
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates = 'autor')
    acerca_mi: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    ultima_conexion: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    following: so.WriteOnlyMapped['Usuario'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: so.WriteOnlyMapped['Usuario'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')

    def __repr__(self):
        return '<usuario {}>' .format(self.nombreUsuario)
    
    def set_contrasena(self, contrasena):
        self.contrasena_hash = generate_password_hash(contrasena)

    def check_contrasena(self, contrasena):
        return check_password_hash(self.contrasena_hash, contrasena)
    
    def avatar(self, size):
        digest = md5(self.correo.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def follow(self, usuario):
        self.is_following(usuario)
        self.following.add(usuario)


    def unfollow(self, usuario):
        if self.is_following(usuario):
            self.following.remove(usuario)

    def is_following(self, usuario):
        query = self.following.select().where(usuario.id == usuario.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)
    
    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)

    def following_posts(self):
        Autor = so.aliased(Usuario)
        Follower = so.aliased(Usuario)
        return (
            sa.select(Post)
            .join(Post.autor.of_type(Autor))
            .join(Autor.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Autor.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.tiempo_publicado.desc())
        )
    
    def get_reset_password_token(self, expires_in = 600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, current_app.app.config['SECRET_KEY'], algorithm = 'HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(Usuario, id)
    
class Post(SearchableMixin,db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    __searchable__ = ['contenido']
    contenido: so.Mapped[str] = so.mapped_column(sa.String(140))
    tiempo_publicado: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    #llave foranea apunta a la tabla usuarios estan conectados
    # one to many un usuario puede tener muchos posts
    usuario_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Usuario.id), index=True)
    autor: so.Mapped[Usuario] = so.relationship(back_populates='posts')
    Idioma: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))

    def __repr__(self):
        return '<Post {}>' .format(self.contenido) 
    
@login.user_loader
def cargar_usuario(id):
    return db.session.get(Usuario, int(id))
from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
from flask_babel import _
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrarForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import Usuario
from app.auth.email import send_password_reset_email 
import datetime
import pytz

@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        print('aqui')
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():

        usuario = db.session.scalar(sa.select(Usuario).where(Usuario.nombreUsuario == form.nombreUsuario.data))
        if usuario is None or not usuario.check_contrasena(form.contrasena.data):
            flash("nombre de usuario o contrasena invalida.")
            return redirect(url_for('login'))
        login_user(usuario, remember = form.recuerda_me.data)

        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
        #flash('inicio de sesion para el usuario {}, contrasena={}'.format
        #        (form.nombreUsuario.data, form.contrasena.data,form.recuerda_me.data))
        #return redirect(url_for('login'))
    return render_template('auth/login.html', title='Iniciar sesion', form=form)





@bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrarForm()
    if form.validate_on_submit():
        usuario = Usuario(nombreUsuario = form.nombreUsuario.data, correo = form.correo.data)
        usuario.set_contrasena(form.contrasena.data)
        print(form.nombreUsuario)
        form.validar_nuevo_usuario(form.nombreUsuario)
        db.session.add(usuario)
        db.session.commit()
        flash("felicitaciones, ahora eres un usuario registrado")
        return redirect(url_for('auth.login'))
    return render_template('auth/registrar.html', title="registrar", form = form)

@bp.route('/Cerrar_sesion')
def cerrar_sesion():
    logout_user()
    return redirect(url_for('main.index'))


@bp.before_request
def registrar_ultima_conexion():
    if current_user.is_authenticated:
        current_user.ultima_conexion = datetime.datetime.now(pytz.utc)
        db.session.commit()


@bp.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        usuario = db.session.scalar(
            sa.select(Usuario).where(Usuario.correo == form.email.data))
        if usuario:
            send_password_reset_email(usuario)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('auth/reset_password_request.html',
                            title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods = ['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    usuario = Usuario.verify_reset_password_token(token)
    if not usuario:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        usuario.set_contrasena(form.contrasena.data)
        db.session.commit()
        flash('Tu contraseña a sido cambiada.')
        return redirect(url_for('login'))
    return render_template('auth/reset_password.html', form = form)


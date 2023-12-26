from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.models import Usuario
from app.forms import LoginForm, RegistrarForm
from urllib.parse import urlsplit


@app.route('/')
@app.route('/index')
@login_required
def index():
    Posts = [
        {
            'autor': {'usuarioNombre': 'Hugo'},
            'contenido': 'Beautiful day in portland!'
        },
        {
            'autor': {'usuarioNombre': 'Pedro'},
            'contenido': 'the avengers movie was so cool'
        }
    ]
    return render_template('index.html', title='home', Posts=Posts)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():

        usuario = db.session.scalar(sa.select(Usuario).where(Usuario.nombreUsuario == form.nombreUsuario.data))
        if usuario is None or not usuario.check_password(form.password.data):
            flash("nombre de usuario o contrasena invalida.")
            return redirect(url_for('login'))
        login_user(usuario, recuerdame = form.recuerda_me.data)

        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    
        #flash('inicio de sesion para el usuario {}, contrasena={}'.format
        #        (form.nombreUsuario.data, form.contrasena.data,form.recuerda_me.data))
        #return redirect(url_for('login'))
    return render_template('login.html', title='Iniciar sesion', form=form)

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrarForm()
    if form.validate_on_submit():
        usuario = Usuario(nombreUsuario = form.nombreUsuario.data, correo = form.correo.data)
        usuario.set_contrasena(form.contrasena.data)
        db.session.add(usuario)
        db.session.commit()
        flash("felicitaciones, ahora eres un usuario registrado")
        return redirect(url_for('login'))
    return render_template('registrar.html', title="registrar", form = form)

@app.route('/Cerrar_sesion')
def cerrar_sesion():
    logout_user()
    return redirect(url_for('index'))



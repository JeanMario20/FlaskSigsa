from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.models import Usuario
from app.forms import LoginForm, RegistrarForm, EditarPerfilForm, EmptyForm
from urllib.parse import urlsplit
from datetime import datetime, timezone


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
            next_page = url_for('index')
        return redirect(next_page)
    
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
        form.validar_nuevo_usuario(form.nombreUsuario)
        db.session.add(usuario)
        db.session.commit()
        flash("felicitaciones, ahora eres un usuario registrado")
        return redirect(url_for('login'))
    return render_template('registrar.html', title="registrar", form = form)

@app.route('/Cerrar_sesion')
def cerrar_sesion():
    logout_user()
    return redirect(url_for('index'))

@app.route('/usuario/<nombreUsuario>')
@login_required
def usuario(nombreUsuario):
    
    usuario = db.first_or_404(sa.select(Usuario).where(Usuario.nombreUsuario == nombreUsuario))
    posts = [
        {'autor': usuario, 'contenido': 'Test post #1'},
        {'autor': usuario, 'contenido': 'Test post #2'}
    ]
    form = EmptyForm()
    return render_template('usuario.html', usuario=usuario, posts=posts, form = form)

@app.before_request
def registrar_ultima_conexion():
    if current_user.is_authenticated:
        current_user.ultima_conexion = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/editar_perfil', methods = ['GET','POST'])
@login_required
def editar_perfil():
    formulario = EditarPerfilForm(current_user.nombreUsuario)
    if formulario.validate_on_submit():
        current_user.nombreUsuario = formulario.nombreUsuario.data
        formulario.validar_nombreUsuario(formulario.nombreUsuario.data)
        current_user.acerca_mi = formulario.acerca_mis.data
        db.session.commit()
        flash("tus cambios han sido guardados ")
        return redirect(url_for('editar_perfil'))
    elif request.method =='GET':
        formulario.nombreUsuario.data = current_user.nombreUsuario
        formulario.acerca_mi = current_user.acerca_mi
    return render_template("editar_perfil.html", title="Editar perfil" , formulario = formulario)

@app.route('/follow/<nombreUsuario>', methods=['POST'])
@login_required
def follow(nombreUsuario):
    form = EmptyForm()
    if form.validate_on_submit():
        nombreUsuario = db.session.scalar(
            sa.select(Usuario).where(Usuario.nombreUsuario == nombreUsuario))
        if nombreUsuario is None:
            flash(f'usuario {nombreUsuario} not found.')
            return redirect(url_for('index'))
        if nombreUsuario == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('usuario', nombreUsuario=nombreUsuario))
        current_user.follow(nombreUsuario)
        db.session.commit()
        flash(f'You are following {nombreUsuario}!')
        return redirect(url_for('index', nombreUsuario=nombreUsuario))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<nombreUsuario>', methods=['POST'])
@login_required
def unfollow(nombreUsuario):
    form = EmptyForm()
    if form.validate_on_submit():
        nombreUsuario = db.session.scalar(
            sa.select(Usuario).where(Usuario.nombreUsuario == nombreUsuario))
        if nombreUsuario is None:
            flash(f'Usuario {nombreUsuario} not found.')
            return redirect(url_for('index'))
        if nombreUsuario == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', nombreUsuario=nombreUsuario))
        current_user.unfollow(nombreUsuario)
        db.session.commit()
        flash(f'You are not following {nombreUsuario}.')
        return redirect(url_for('index', nombreUsuario=nombreUsuario))
    else:
        return redirect(url_for('index'))

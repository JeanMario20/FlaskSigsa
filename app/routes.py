from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    usuario = {'nombre' : 'Jean'}
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
    return render_template('index.html', title='home', usuario=usuario, Posts=Posts)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('inicio de sesion para el usuario {}, contrasena={}'.format
                (form.nombreUsuario.data, form.contrasena.data,form.recuerda_me.data))
        return redirect(url_for('login'))
    return render_template('login.html', title='Iniciar sesion', form=form)


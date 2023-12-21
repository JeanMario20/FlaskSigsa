from flask import render_template
from app import app

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
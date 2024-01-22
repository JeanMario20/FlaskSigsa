from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, g, \
    current_app, g
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import sqlalchemy as sa
from langdetect import detect, LangDetectException
from app import db
from app.main.forms import EditarPerfilForm, EmptyForm, PostForm, SearchForm
from app.models import Usuario, Post
from app.translate import translate
from app.main import bp

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.ultima_conexion = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

@bp.route('/', methods = ['GET', 'POST'])
@bp.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            Idioma  = detect(form.post.data)
        except LangDetectException:
            Idioma  = ''
        post = Post(contenido = form.post.data, autor = current_user, Idioma  = Idioma )
        db.session.add(post)
        db.session.commit()
        flash("Tu contenido a sido subido ahora se muestra a todo el mundo")
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page = page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('index', page = posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page = posts.prev_num) \
        if posts.has_prev else None
    
    return render_template('index.html', title=_('Inicio'), form = form ,posts=posts.items, next_url = next_url, prev_url = prev_url)

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.tiempo_publicado.desc())
    posts = db.paginate(query, page = page, per_page = current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('main.explore', page = posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page = posts.prev_num) \
        if posts.has_prev else None
    
    return render_template('index.html', title = 'explore', posts = posts.items, next_url = next_url, prev_url = prev_url)

@bp.route('/usuario/<nombreUsuario>')
@login_required
def usuario(nombreUsuario):
    
    usuario = db.first_or_404(sa.select(Usuario).where(Usuario.nombreUsuario == nombreUsuario))
    page = request.args.get('page', 1, type = int)
    query = usuario.posts.select().order_by(Post.tiempo_publicado.desc())
    posts = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    
    next_url = url_for('main.usuario', nombreUsuario = usuario.nombreUsuario, page = posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.usuario', nombreUsuario = Usuario.nombreUsuario, page = posts.prev_num)  \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('usuario.html', usuario=usuario, posts=posts, next_url = next_url, prev_url=prev_url, form = form)

@bp.route('/editar_perfil', methods = ['GET','POST'])
@login_required
def editar_perfil():
    formulario = EditarPerfilForm(current_user.nombreUsuario)
    if formulario.validate_on_submit():
        current_user.nombreUsuario = formulario.nombreUsuario.data
        formulario.validar_nombreUsuario(formulario.nombreUsuario.data)
        current_user.acerca_mi = formulario.acerca_mis.data
        db.session.commit()
        flash(_("tus cambios han sido guardados "))
        return redirect(url_for('main.editar_perfil'))
    elif request.method =='GET':
        formulario.nombreUsuario.data = current_user.nombreUsuario
        formulario.acerca_mi = current_user.acerca_mi
    return render_template("editar_perfil.html", title=_("Editar perfil") , formulario = formulario)

@bp.route('/follow/<nombreUsuario>', methods=['POST'])
@login_required
def follow(nombreUsuario):
    form = EmptyForm()
    if form.validate_on_submit():
        nombreUsuario = db.session.scalar(
            sa.select(Usuario).where(Usuario.nombreUsuario == nombreUsuario))
        if nombreUsuario is None:
            flash(_(f'usuario {nombreUsuario} not found.'))
            return redirect(url_for('main.index'))
        if nombreUsuario == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.usuario', nombreUsuario=nombreUsuario))
        current_user.follow(nombreUsuario)
        db.session.commit()
        flash(f'You are following {nombreUsuario}!')
        return redirect(url_for('main.usuario', nombreUsuario=nombreUsuario))
    else:
        return redirect(url_for('main.index'))

@bp.route('/unfollow/<nombreUsuario>', methods=['POST'])
@login_required
def unfollow(nombreUsuario):
    form = EmptyForm()
    if form.validate_on_submit():
        nombreUsuario = db.session.scalar(
            sa.select(Usuario).where(Usuario.nombreUsuario == nombreUsuario))
        if nombreUsuario is None:
            flash(_(f'Usuario {nombreUsuario} no ha sido encontrado.'))
            return redirect(url_for('main.index'))
        if nombreUsuario == current_user:
            flash(_('No puedes seguirte a ti mismo!'))
            return redirect(url_for('main.usuario', nombreUsuario=nombreUsuario))
        current_user.unfollow(nombreUsuario)
        db.session.commit()
        flash(_(f'no estas siguiendo a{nombreUsuario}.'))
        return redirect(url_for('main.usuario', nombreUsuario=nombreUsuario))
    else:
        return redirect(url_for('main.index'))

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    data = request.get_json()
    return {'text': translate(data['text'], data['source_language'], data['dest_language'])}

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('buscador.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)
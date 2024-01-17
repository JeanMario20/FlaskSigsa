from flask import render_template, current_app
from flask_babel import _
from app.email import send_email



def send_password_reset_email(usuario):
    print(usuario.correo)
    token = usuario.get_reset_password_token()
    send_email(_('[SisgsaBlog] Reincia tu contraseña. '),
                sender=current_app.config['ADMINS'][0],
                recipients=[usuario.correo],
                text_body=render_template('email/reset_password.txt',
                                            usuario=usuario, token=token),
                html_body=render_template('email/reset_password.html',
                                            usuario=usuario, token=token))
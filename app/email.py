from flask_mail import Message
from app import mail, app
from flask import render_template 
from threading import Thread


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body    
    mail.send(msg)

def send_password_reset_email(usuario):
    print(usuario.correo)
    token = usuario.get_reset_password_token()
    send_email('[SisgsaBlog] Reincia tu contraseña. ',
                sender=app.config['ADMINS'][0],
                recipients=[usuario.correo],
                text_body=render_template('email/reset_password.txt',
                                            usuario=usuario, token=token),
                html_body=render_template('email/reset_password.html',
                                            usuario=usuario, token=token))
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from oasis_nourish import mail


def send_async_email(app, message):
    with app.app_context():
        mail.send(message)

def send_email(recipient, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['MAIL_SENDER'], recipients=[recipient])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return thread


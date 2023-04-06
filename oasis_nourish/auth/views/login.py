from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user
from .. import auth
from ..forms import LoginForm
from oasis_nourish.models import User


@auth.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_url = request.args.get('next')
            if next_url is None or next_url.startswith('/'):
                next_url = url_for('main.index')
            return redirect(next_url)
    return render_template('auth/login.html')

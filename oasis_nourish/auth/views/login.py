from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, current_user
from .. import auth
from ..forms import LoginForm
from oasis_nourish.models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged', 'info')
        return redirect(url_for('account.details'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_url = request.args.get('next')
            if next_url is None:
                next_url = url_for('main.home')
            return redirect(next_url)
        else:
            flash("Invalid login", "error")
    return render_template('auth/login.html', form=form, title='Login | Oasis Nourish')

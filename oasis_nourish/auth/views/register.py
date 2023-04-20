from flask_login import current_user
from ..forms import RegistrationForm
from oasis_nourish import db
from flask import render_template, redirect, url_for, flash
from oasis_nourish.models import User
from .. import auth
from oasis_nourish.email import send_email


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged', 'info')
        return redirect(url_for('account.details'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.home'))
    return render_template('auth/register.html', form=form, title="Register | Oasis Nourish")

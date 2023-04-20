from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash

from .. import account
from ..forms import EditPersonalDetailsForm, EditEmailForm, ChangePasswordForm
from oasis_nourish import db


@account.route("/details", methods=['GET', 'POST'])
@login_required
def details():
    personal_details_form = EditPersonalDetailsForm()
    email_form = EditEmailForm()
    password_form = ChangePasswordForm()

    if personal_details_form.validate_on_submit():
        current_user.first_name = personal_details_form.first_name.data
        current_user.last_name = personal_details_form.last_name.data
        current_user.phone = personal_details_form.phone.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("Personal details successfully updated", category='message')

    elif email_form.validate_on_submit():
        if current_user.verify_password(email_form.password.data):
            current_user.email = email_form.email.data
            db.session.add(current_user._get_current_object())
            db.session.commit()
            flash("Email successfully updated", category='message')
        else:
            flash("Error: password incorrect", category='error')

    elif password_form.validate_on_submit():
        if current_user.verify_password(password_form.password.data):
            current_user.password = password_form.new_password.data
            db.session.add(current_user._get_current_object())
            db.session.commit()
            flash("Password successfully updated")
        else:
            flash("Error: password incorrect", category='error')

    return render_template("account/my_account.html", title="Account Details | Oasis Nourish",
                           personal_form=personal_details_form,
                           email_form=email_form,
                           password_form=password_form)

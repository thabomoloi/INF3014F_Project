from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash

from .. import account
from ..forms import EditPersonalDetailsForm, EditEmailForm
from oasis_nourish import db, User


@account.route("/edit", methods=['GET', 'POST'])
@login_required
def edit():
    personal_details_form = EditPersonalDetailsForm()
    if personal_details_form.validate_on_submit():
        current_user.first_name = personal_details_form.first_name.data
        current_user.last_name = personal_details_form.last_name.data
        current_user.phone = personal_details_form.phone.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("Personal details successfully updated", category='message')

    email_form = EditEmailForm()
    if email_form.validate_on_submit():
        if current_user.verify_password(email_form.password.data):
            current_user.email = email_form.email.data
            flash("Email successfully updated", category='message')
        else:
            flash("Error: password incorrect", category='error')

    return render_template("account/edit.html", title="Edit Account",
                           personal_form=personal_details_form,
                           email_form=email_form)

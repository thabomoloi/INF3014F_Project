from .. import auth
from flask_login import logout_user, login_required
from flask import flash, url_for, redirect


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.home'))

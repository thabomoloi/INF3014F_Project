from flask_login import login_required
from flask import render_template

from .. import account


@login_required
@account.route('/dashboard')
def dashboard():
    return render_template('account/dashboard.html', title='Dashboard')

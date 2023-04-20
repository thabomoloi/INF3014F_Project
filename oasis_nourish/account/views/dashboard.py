from flask_login import login_required
from flask import render_template

from .. import account


@account.route('/dashboard')
@account.route('/')
@login_required
def dashboard():
    return render_template('account/dashboard.html', title='Dashboard')

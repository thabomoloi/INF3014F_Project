from .. import account
from flask_login import login_required, current_user


@account.route('/orders')
@login_required
def orders():
    return "Orders"

@account.route('/cards')
@login_required
def cards():
    return "Credit Cards"

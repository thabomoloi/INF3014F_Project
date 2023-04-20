from oasis_nourish.main import main
from flask_login import login_required, current_user


@main.route('/orders')
@login_required
def orders():
    return "Orders";
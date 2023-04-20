from flask_login import login_required
from flask import render_template

from .. import account


@account.route("/edit", methods=['GET', 'POST'])
@login_required
def edit():

    return render_template("account/edit.html", title="Edit Account")

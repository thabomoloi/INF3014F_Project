from flask_login import login_required
from flask import render_template

from .. import account
from ... import db
from ...models import Product
from ...permision_decorators import admin_required


@account.route('/dashboard')
@login_required
@admin_required
def dashboard():
    categories = db.session.query(Product.category.distinct()).all()
    return render_template('account/dashboard.html', title='Dashboard', categories=categories)

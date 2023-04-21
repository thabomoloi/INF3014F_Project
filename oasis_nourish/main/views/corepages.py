from flask import render_template, request, redirect, url_for

from .. import main
from oasis_nourish.models import *


@main.route('/')
def home():
    products = Product.query.all()
    return render_template('corepages/index.html', products=products)


@main.route('/')
def index():
    products = Product.query.all()
    return render_template('corepages/index.html', products=products)


@main.route('/search', methods=['GET'])
def search():
    if request.method == 'GET':
        query = request.args.get('query')

        if query:
            return '<h1></h1>'

    return redirect(url_for('main.home'))

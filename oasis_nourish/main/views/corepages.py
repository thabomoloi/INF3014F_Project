from flask import render_template, request, redirect, url_for, current_app, flash

from oasis_nourish.email import send_email
from .. import main
from oasis_nourish.models import *


@main.route('/')
def home():
    return index()


@main.route('/')
def index():
    products = Product.query.all()
    categories = db.session.query(Product.category.distinct()).all()

    fresh_foods = Product.query.filter(Product.category.like('%' + 'Fresh Foods' + '%')).limit(6).all()
    top_rated = Product.query.order_by(Product.average_ratings.desc()).limit(6).all()
    return render_template('corepages/index.html', products=products, categories=categories, fresh_foods=fresh_foods,
                           top_rated=top_rated, title="Oasis Nourish")


@main.route("/about")
def about():
    categories = db.session.query(Product.category.distinct()).all()
    return render_template("about.html", categories=categories, title="About | Oasis Nourish")


@main.route("/terms-of-use")
def terms():
    categories = db.session.query(Product.category.distinct()).all()
    return render_template("terms.html", categories=categories, title="Terms of use | Oasis Nourish")


@main.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        app = current_app._get_current_object()

        send_email(app.config["OASIS_NOURISH_ADMIN"], "New Message", "auth/email/message", name=name, message=message, email=email)
        flash("Our team will get back to you shortly.", category="info")

    categories = db.session.query(Product.category.distinct()).all()
    return render_template("contact.html", categories=categories, title="Contact | Oasis Nourish")


@main.route("/privacy-policy")
def privacy():
    categories = db.session.query(Product.category.distinct()).all()
    return render_template("privacy.html", categories=categories, title="Privacy Policy | Oasis Nourish")


@main.route('/search', methods=['GET'])
def search():
    categories = db.session.query(Product.category.distinct()).all()
    if request.method == 'GET':
        query = request.args.get('query')

        if query:
            products = Product.query.filter(
                Product.name.like('%' + query + '%') | Product.category.like('%' + query + '%')).all()
            return render_template('index.html', page_title=f"Search results for {query}...",
                                   products=products, title="Search results", categories=categories, query=query)

    return redirect(url_for('main.home'))

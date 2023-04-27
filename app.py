import os

import random
from threading import Thread

from flask import render_template, redirect, url_for, request, session, flash, current_app
from flask_login import login_required, current_user, logout_user, login_user

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

from config import config

config_name = "production" if os.environ.get("IS_HEROKU") else "default"

app = Flask(__name__)

app.config.from_object(config[config_name])
config[config_name].init_app(app)

mail = Mail(app)
db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from forms import AddressForm, RegistrationForm, LoginForm, ChangePasswordForm, EditEmailForm, EditPersonalDetailsForm
from models import Order, Product, photos, Address, AddToCart, Order_Item, handle_cart, Checkout, User, Role, AddProduct
from permision_decorators import admin_required
from populate_products import populate


@app.before_request
def create_tables():
    db.create_all()
    Role.insert_roles()
    if Product.query.count() == 0:
        populate(db, Product)


@app.route('/orders')
@login_required
def orders():
    return "Orders"


@app.route('/cards')
@login_required
def cards():
    return "Credit Cards"


@app.route("/address", methods=["GET", "POST"])
@login_required
def address():
    form = AddressForm()
    if form.validate_on_submit():
        new_address = Address(
            street=form.street.data,
            suburb=form.suburb.data,
            city=form.city.data,
            postal_code=form.postal_code.data,
            user_id=current_user.id
        )
        db.session.add(new_address)
        db.session.commit()

        return redirect(request.referrer)

    addr = Address.query.filter_by(user_id=current_user.id).first()
    mode = "add" if addr is None else "view"
    categories = db.session.query(Product.category.distinct()).all()

    return render_template("account/address.html", mode=mode, address_form=form, address=addr, categories=categories)


@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    categories = db.session.query(Product.category.distinct()).all()
    return render_template('account/dashboard.html', title='Dashboard', categories=categories)


@app.route("/details", methods=['GET', 'POST'])
@login_required
def details():
    categories = db.session.query(Product.category.distinct()).all()

    personal_details_form = EditPersonalDetailsForm()
    email_form = EditEmailForm()
    password_form = ChangePasswordForm()

    if personal_details_form.validate_on_submit():
        current_user.first_name = personal_details_form.first_name.data
        current_user.last_name = personal_details_form.last_name.data
        current_user.phone = personal_details_form.phone.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("Personal details successfully updated", category='message')

    elif email_form.validate_on_submit():
        if current_user.verify_password(email_form.password.data):
            current_user.email = email_form.email.data
            db.session.add(current_user._get_current_object())
            db.session.commit()
            flash("Email successfully updated", category='message')
        else:
            flash("Error: password incorrect", category='error')

    elif password_form.validate_on_submit():
        if current_user.verify_password(password_form.password.data):
            current_user.password = password_form.new_password.data
            db.session.add(current_user._get_current_object())
            db.session.commit()
            flash("Password successfully updated")
        else:
            flash("Error: password incorrect", category='error')

    return render_template("account/my_account.html", title="Account Details | Oasis Nourish",
                           personal_form=personal_details_form,
                           email_form=email_form,
                           password_form=password_form,
                           Address=Address, categories=categories)


@app.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('home'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('home'))


@app.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('home'))
    return render_template('auth/unconfirmed.html')


@app.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged', 'info')
        return redirect(url_for('details'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_url = request.args.get('next')
            if next_url is None:
                next_url = url_for('home')
            return redirect(next_url)
        else:
            flash("Invalid login", "error")
    return render_template('auth/login.html', form=form, title='Login | Oasis Nourish')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged', 'info')
        return redirect(url_for('details'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            password=form.password.data
        )
        if user.email.strip() == current_app.config['OASIS_NOURISH_ADMIN'].strip():
            role = Role.query.filter_by(name='Administrator').first()
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                password=form.password.data,
                role_id=role.id
            )
        else:
            role = Role.query.filter_by(default=True).first()
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                password=form.password.data,
                role_id=role.id
            )

        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('home'))
    return render_template('auth/register.html', form=form, title="Register | Oasis Nourish")


@app.route('/')
def home():
    return index()


@app.route('/')
def index():
    products = Product.query.all()
    categories = db.session.query(Product.category.distinct()).all()

    fresh_foods = Product.query.filter(Product.category.like('%' + 'Fresh Foods' + '%')).limit(6).all()
    top_rated = Product.query.order_by(Product.average_ratings.desc()).limit(6).all()
    return render_template('corepages/index.html', products=products, categories=categories, fresh_foods=fresh_foods,
                           top_rated=top_rated, title="Oasis Nourish")


@app.route("/about")
def about():
    categories = db.session.query(Product.category.distinct()).all()
    return render_template("about.html", categories=categories, title="About | Oasis Nourish")


@app.route("/terms-of-use")
def terms():
    categories = db.session.query(Product.category.distinct()).all()
    return render_template("terms.html", categories=categories, title="Terms of use | Oasis Nourish")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        send_email(app.config["OASIS_NOURISH_ADMIN"], "New Message", "auth/email/message", name=name, message=message,
                   email=email)
        flash("Our team will get back to you shortly.", category="info")

    categories = db.session.query(Product.category.distinct()).all()
    return render_template("contact.html", categories=categories, title="Contact | Oasis Nourish")


@app.route("/privacy-policy")
def privacy():
    categories = db.session.query(Product.category.distinct()).all()
    return render_template("privacy.html", categories=categories, title="Privacy Policy | Oasis Nourish")


@app.route('/search', methods=['GET'])
def search():
    categories = db.session.query(Product.category.distinct()).all()
    if request.method == 'GET':
        query = request.args.get('query')

        if query:
            products = Product.query.filter(
                Product.name.like('%' + query + '%') | Product.category.like('%' + query + '%')).all()
            return render_template('index.html', page_title=f"Search results for {query}...",
                                   products=products, title="Search results", categories=categories, query=query)

    return redirect(url_for('home'))


@app.route('/products/<cat>', methods=['GET'])
def products_by_cat(cat):
    categories = db.session.query(Product.category.distinct()).all()

    if cat == 'all':
        products = Product.query.all()

        return render_template('index.html', page_title="Products",
                               products=products, categories=categories, title="Products")
    else:
        products = Product.query.filter_by(category=cat)
        return render_template('index.html', page_title=cat.capitalize(),
                               products=products, title=cat, category=cat, categories=categories)


@app.route('/products', methods=['GET'])
def products():
    return products_by_cat('all')


@app.route('/product/<name>')
def product(name):
    product = Product.query.filter_by(name=name).first()
    categories = db.session.query(Product.category.distinct()).all()

    form = AddToCart()
    if (product is None):
        flash(f"Cannot find product {name}", category="error")
        return redirect(url_for("products", cat="all"))
    return render_template('view-product.html', product=product, form=form, title=product.name, categories=categories)


@app.route('/quick-add/<id>')
def quick_add(id):
    add_item_to_cart(id=id)
    return redirect(request.referrer)


def add_item_to_cart(id, quantity=1):
    shopping_cart = session.get('cart', [])
    in_cart = False

    for index, item in enumerate(shopping_cart):
        if item['id'] == id:
            in_cart = True
            shopping_cart[index]['quantity'] = int(item['quantity']) + quantity

    if not in_cart:
        shopping_cart.append({'id': id, 'quantity': quantity})

    session['cart'] = shopping_cart
    session.modified = True


def update_cart(id, quantity):
    shopping_cart = session.get('cart', [])
    for index, item in enumerate(shopping_cart):
        if item['id'] == id:
            shopping_cart[index]['quantity'] = quantity
    session['cart'] = shopping_cart
    session.modified = True


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    form = AddToCart()

    if form.validate_on_submit():
        add_item_to_cart(id=form.id.data, quantity=form.quantity.data)

    return redirect(url_for('products'))


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    categories = db.session.query(Product.category.distinct()).all()

    return render_template('cart.html', products=products, grand_total=grand_total,
                           grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total,
                           Product=Product, title="Shopping Cart", categories=categories)


@app.route('/remove-from-cart/<index>')
def remove_from_cart(index):
    del session['cart'][int(index)]
    session.modified = True
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = Checkout()

    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    address = Address.query.filter_by(user_id=current_user.id).first()

    if address is None:
        flash("Please enter address before continuing to checkout.", category="info")
        return redirect(url_for("address"))

    if form.validate_on_submit():

        order = Order()
        form.populate_obj(order)
        order.reference = ''.join([random.choice('ABCDE') for _ in range(5)])
        order.status = 'PENDING'
        order.street = address.street
        order.city = address.city
        order.suburb = address.suburb
        order.postal_code = address.postal_code

        for product in products:
            order_item = Order_Item(
                quantity=product['quantity'], product_id=product['id'])
            order.items.append(order_item)

            product = Product.query.filter_by(id=product['id']).update(
                {'stock': Product.stock - product['quantity']})

        db.session.add(order)
        db.session.commit()

        send_email(current_user.email, "Your order has been placed successfully", "order_placed", products=products,
                   grand_total=grand_total)
        session['cart'] = []
        session.modified = True
        flash("Your order has been placed successfully")

        return redirect(url_for('home'))
    categories = db.session.query(Product.category.distinct()).all()

    return render_template('checkout.html', form=form, grand_total=grand_total,
                           grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total,
                           address=address, title="Checkout | Oasis Nourish", categories=categories)


@app.route('/admin')
@admin_required
def admin():
    products = Product.query.all()
    products_in_stock = Product.query.filter(Product.stock > 0).count()

    orders = Order.query.all()

    return render_template('admin/index.html', admin=True, products=products, products_in_stock=products_in_stock,
                           orders=orders)


@app.route('/admin/add', methods=['GET', 'POST'])
@admin_required
def add():
    form = AddProduct()

    if form.validate_on_submit():
        image_url = "images/" + photos.save(form.image.data)

        new_product = Product(name=form.name.data, price=form.price.data,
                              stock=form.stock.data, description=form.description.data,
                              category=form.category.data, brand=form.brand.data,
                              average_ratings=form.average_ratings.data,
                              ratings_count=form.ratings_count.data, image=image_url)

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('admin'))

    return render_template('admin/add-product.html', admin=True, form=form, title="Add New Product | Oasis Nourish")


@app.route('/admin/order/<order_id>')
@admin_required
def order(order_id):
    order_ = Order.query.filter_by(id=int(order_id)).first()

    return render_template('admin/view-order.html', order=order_, admin=True)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


def send_async_email(app_, message):
    with app_.app_context():
        mail.send(message)


def send_email(recipient, subject, template, **kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + " " + subject, sender=app.config['MAIL_SENDER'],
                  recipients=[recipient])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return thread

from flask import flash, request, jsonify
from flask_login import login_required

from oasis_nourish.email import send_email
from .. import main
from oasis_nourish.models import *
from oasis_nourish.permision_decorators import *


@main.route('/products/<cat>', methods=['GET'])
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


@main.route('/products', methods=['GET'])
def products():
    return products_by_cat('all')


@main.route('/product/<name>')
def product(name):
    product = Product.query.filter_by(name=name).first()
    categories = db.session.query(Product.category.distinct()).all()

    form = AddToCart()
    if (product is None):
        flash(f"Cannot find product {name}", category="error")
        return redirect(url_for("main.products", cat="all"))
    return render_template('view-product.html', product=product, form=form, title=product.name, categories=categories)


@main.route('/quick-add/<id>')
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


@main.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    form = AddToCart()

    if form.validate_on_submit():
        add_item_to_cart(id=form.id.data, quantity=form.quantity.data)

    return redirect(url_for('main.products'))


@main.route('/cart', methods=['GET', 'POST'])
def cart():
    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    categories = db.session.query(Product.category.distinct()).all()

    return render_template('cart.html', products=products, grand_total=grand_total,
                           grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total, Product=Product, title="Shopping Cart", categories=categories)

@main.route('/remove-from-cart/<index>')
def remove_from_cart(index):
    del session['cart'][int(index)]
    session.modified = True
    return redirect(url_for('main.cart'))


@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = Checkout()

    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    address = Address.query.filter_by(user_id=current_user.id).first()

    if address is None:
        flash("Please enter address before continuing to checkout.", category="info")
        return redirect(url_for("account.address"))

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

        send_email(current_user.email, "Your order has been placed successfully", "order_placed", products=products)
        session['cart'] = []
        session.modified = True

        return redirect(url_for('main.home'))
    categories = db.session.query(Product.category.distinct()).all()

    return render_template('checkout.html', form=form, grand_total=grand_total,
                           grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total,
                           address=address, title="Checkout | Oasis Nourish", categories=categories)


@main.route('/admin')
@admin_required
def admin():
    products = Product.query.all()
    products_in_stock = Product.query.filter(Product.stock > 0).count()

    orders = Order.query.all()

    return render_template('admin/index.html', admin=True, products=products, products_in_stock=products_in_stock,
                           orders=orders)


@main.route('/admin/add', methods=['GET', 'POST'])
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

        return redirect(url_for('main.admin'))

    return render_template('admin/add-product.html', admin=True, form=form, title="Add New Product | Oasis Nourish")


@main.route('/admin/order/<order_id>')
@admin_required
def order(order_id):
    order = Order.query.filter_by(id=int(order_id)).first()

    return render_template('admin/view-order.html', order=order, admin=True)

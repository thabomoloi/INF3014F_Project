import json

from flask import Flask, render_template, redirect, url_for, session
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import StringField, IntegerField, TextAreaField, HiddenField, SelectField, FloatField
from flask_wtf.file import FileField, FileAllowed
import random
from oasis_nourish import db

photos = UploadSet('photos', IMAGES)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Integer)  # in cents
    stock = db.Column(db.Integer)
    description = db.Column(db.String(500))
    category = db.Column(db.String(50))
    average_ratings = db.Column(db.Float)
    ratings_count = db.Column(db.Integer)
    brand = db.Column(db.String(50))
    image = db.Column(db.String(100))

    orders = db.relationship('Order_Item', backref='product', lazy=True)

    def in_stock(self):
        if session:
            item = {}
            try:
                item = session['cart'][self.id]
            except:
                pass
            if len(item) > 0:
                return self.stock - item['quantity']
            else:
                return self.stock
        else:
            return self.stock

    def json(self):
        prod = {
            "id": self.id,
            "name": self.name,
            "stock": self.stock,
            "description": self.description,
            "category": self.category,
            "average_ratings": self.average_ratings,
            "ratings_count": self.ratings_count,
            "brand": self.brand,
            "image": self.image
        }
        return json.dumps(prod)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(5))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    phone_number = db.Column(db.Integer)
    email = db.Column(db.String(50))
    street = db.Column(db.String(100))
    suburb = db.Column(db.String(100))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(4))
    status = db.Column(db.String(10))
    payment_type = db.Column(db.String(10))
    items = db.relationship('Order_Item', backref='order', lazy=True)

    def order_total(self):
        return db.session.quey(db.func.sum(Order_Item.quantity * Product.price)).join(Product).filter(Order_Item.order_id == self.id).scalar() + 1000

    def quantity_total(self):
        return db.session.query(db.func.sum(Order_Item.quantity)).filter(Order_Item.order_id == self.id).scalar()


class Order_Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)


class AddProduct(FlaskForm):
    name = StringField('Name')
    price = IntegerField('Price')
    stock = IntegerField('Stock')
    description = TextAreaField('Description')
    category = StringField('Category')
    brand = StringField("Brand")
    average_ratings = FloatField("Rating")
    ratings_count = IntegerField("Ratings count")
    image = FileField('Image')


class AddToCart(FlaskForm):
    quantity = IntegerField('Quantity')
    id = HiddenField('ID')


class Checkout(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone_number = StringField('Number')
    email = StringField('Email')
    payment_type = SelectField('Payment Type', choices=[
                               ('CK', 'Check'), ('WT', 'Wire Transfer')])


def handle_cart():
    products = []
    grand_total = 0
    index = 0
    quantity_total = 0

    for item in session['cart']:
        product = Product.query.filter_by(id=item['id']).first()

        quantity = int(item['quantity'])
        total = quantity * product.price
        grand_total += total

        quantity_total += quantity

        products.append({'id': product.id, 'name': product.name, 'price':  product.price,
                         'image': product.image, 'quantity': quantity, 'total': total, 'index': index})
        index += 1

    grand_total_plus_shipping = grand_total + 10000

    return products, grand_total, grand_total_plus_shipping, quantity_total


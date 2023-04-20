from .. import db


class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(64))
    suburb = db.Column(db.String(64))
    city = db.Column(db.String(64))
    postal_code = db.Column(db.String(4))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __int__(self, **kwargs):
        super(Address, self).__init__(**kwargs)


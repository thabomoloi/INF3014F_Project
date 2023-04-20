from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, EmailField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


class AddressForm(FlaskForm):
    street = StringField("Street", validators=[DataRequired(), Length(4)])
    suburb = StringField("Suburb", validators=[DataRequired(), Length(1)])
    city = StringField("City", validators=[DataRequired(), Length(1)])
    postal_code = StringField("Postal code", validators=[DataRequired(), Length(4, 4), Regexp("\d{4}", message="Postal code must be 4 digits")])

    submit = SubmitField("Submit")
    

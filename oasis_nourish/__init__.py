from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_uploads import configure_uploads

mail = Mail()
db = SQLAlchemy()
bootstrap = Bootstrap5()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

from .models import Role, User, photos, Product
from populate_products import populate

def create_app(config_name):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config[config_name])
        config[config_name].init_app(app)
        mail.init_app(app)
        db.init_app(app)
        login_manager.init_app(app)
        bootstrap.init_app(app)

        configure_uploads(app, photos)
        Role.insert_roles()
        db.create_all()
        populate(db=db, Product=Product)

        # Blueprints registrations
        from .main import main as main_blueprint
        app.register_blueprint(main_blueprint)

        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')

        from .account import account as account_blueprint
        app.register_blueprint(account_blueprint, url_prefix='/account')


    return app


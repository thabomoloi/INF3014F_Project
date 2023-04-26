import os

from flask import Flask
from flask_migrate import Migrate
from oasis_nourish import create_app, db, User, Role, Product



app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Time</h1>"

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

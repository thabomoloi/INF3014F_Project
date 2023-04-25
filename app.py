import os
from flask_migrate import Migrate
from oasis_nourish import create_app, db, User, Role, Product


app = create_app("production")


migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

import os
from app import create_app, db
from app.model.models import Flat, Rating, User, Like
from flask_migrate import Migrate




app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db, render_as_batch=True)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Like=Like, Flat=Flat, Rating=Rating)

@app.cli.command()
def test():
    """Run unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
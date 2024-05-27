import unittest
from app.models import User, Flat, Like, Rating, FlatError
from app import db, create_app

class FlatModelCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_average_rating(self):
        flat1 = Flat(id = 1)

        db.session.add(flat1)

        rating1 = Rating(flat_id=flat1.id, rating = 1)
        rating2 = Rating(flat_id=flat1.id, rating = 2)
        rating3 = Rating(flat_id=flat1.id, rating = 3)

        db.session.add_all([rating1, rating2, rating3])

        self.assertEqual( flat1.average_rating(), (1 + 2 + 3) / 3) 

    def test_no_rating(self):
        flat1 = Flat(id = 1)
        db.session.add(flat1)

        with self.assertRaises(FlatError):
            flat1.average_rating()

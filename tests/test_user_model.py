import unittest
from app.model.models import User, Flat, Like, Rating
from app import db, create_app
import pandas as pd

class UserModelPasswordTestCase(unittest.TestCase):
    def test_password_setter(self):
        user = User(password = 'football')
        self.assertTrue(user.password_hash is not None)
    
    def test_no_password_getter(self):
        user = User(password = 'football')
        with self.assertRaises(AttributeError):
            user.password
    
    def test_verify_password(self):
        user = User(password = 'football')
        self.assertTrue(user.verify_password('football'))
        self.assertFalse(user.verify_password('soccer'))
    
    def test_password_hashing(self):
        user = User(password = 'football')
        user2 = User(password = 'soccer')
        self.assertTrue(user.password_hash != user2.password_hash)


class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User()
        self.flat = Flat()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_like_new_flat(self):
        self.user.like_flat(self.flat)
        self.assertIsNotNone(Like.query.filter_by(user_id=self.user.id, flat_id=self.flat.id).first())

    def test_double_like_flat(self):
        self.user.like_flat(self.flat)
        self.user.like_flat(self.flat)
        self.assertTrue(len(Like.query.filter_by(user_id=self.user.id, flat_id=self.flat.id).all()) == 1)
    
    def test_unlike_liked_flat(self):
        self.user.like_flat(self.flat)
        self.user.unlike_flat(self.flat)
        self.assertIsNone(Like.query.filter_by(user_id=self.user.id, flat_id=self.flat.id).first())

    def test_unlike_new_flat(self):
        self.user.unlike_flat(self.flat)
        self.assertIsNone(Like.query.filter_by(user_id=self.user.id, flat_id=self.flat.id).first())
    
    def test_rate_flat(self):
        """
        Test if rating a flat is added to the db.
        EXPECTED: added to the db
        """
        rating = 9
        self.user.rate_flat(self.flat, score=rating)
        self.assertTrue(Rating.query.filter_by(user_id=self.user.id, flat_id=self.flat.id, rating=rating).count() == 1)

    def test_double_rate_flat(self):
        """
        Test if rating a flat that has been rated already is going to modify the original rating.
        EXPECTED: the flat rating is modified, there's no duplicate rating with old rating
        """
        first_rating = 9
        self.user.rate_flat(self.flat, score=first_rating)
        second_rating = 1
        self.user.rate_flat(self.flat, score=second_rating)
        self.assertTrue(Rating.query.filter_by(user_id=self.user.id, flat_id=self.flat.id, rating=second_rating).count() == 1)
        self.assertTrue(Rating.query.filter_by(user_id=self.user.id, flat_id=self.flat.id, rating=first_rating).count() == 0)

    def test_get_best_flat(self):
        flats_data = [
            [1, 100, 2, 200],
            [2, 101, 2, 201],
            [3, 200, 3, 400]
        ]
        flats = pd.DataFrame(flats_data, columns=['flat_id', 'price', 'rooms', 'sqm'])

        ratings_data = [
            [1, 100, 2, 100, 9.9]
        ]
        rated_flats = pd.DataFrame(ratings_data, columns=['flat_id', 'price', 'rooms', 'sqm', 'rating'])

        best_flat_id = self.user.compute_best_flat(rated_flats=rated_flats, flats=flats)

        self.assertEqual(best_flat_id, 2)
    
    def test_best_flat_if_no_rating(self):
        self.assertTrue(self.user.rated.count() == 0)
        flat = self.user.get_best_flat()
        self.assertEqual(Flat.query.first(), flat)
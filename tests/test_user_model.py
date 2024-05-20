import unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):
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



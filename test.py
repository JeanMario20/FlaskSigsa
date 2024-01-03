import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timezone, timedelta
import unittest
from app import db, app  
from app.models import Usuario, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = Usuario(nombreUsuario='susan', correo='susan@example.com')
        u.set_contrasena('cat')
        self.assertFalse(u.check_contrasena('dog'))
        self.assertTrue(u.check_contrasena('cat'))

    def test_avatar(self):
        u = Usuario(nombreUsuario='john', correo='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = Usuario(nombreUsuario='john', correo='john@example.com')
        u2 = Usuario(nombreUsuario='susan', correo='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        following = db.session.scalars(u1.following.select()).all()
        followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(following, [])
        self.assertEqual(followers, [])

        u1.follow(u2)
        print(u1.following_count())
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 1)
        self.assertEqual(u2.followers_count(), 1)
        u1_following = db.session.scalars(u1.following.select()).all()
        u2_followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(u1_following[0].nombreUsuario, 'susan')
        self.assertEqual(u2_followers[0].nombreUsuario, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 0)
        self.assertEqual(u2.followers_count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = Usuario(nombreUsuario='john5', correo='1john@example.com')
        u2 = Usuario(nombreUsuario='susan5', correo='susa3n@example.com')
        u3 = Usuario(nombreUsuario='mary', correo='mary@example.com')
        u4 = Usuario(nombreUsuario='david', correo='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.now(timezone.utc)
        p1 = Post(contenido="post from john5", autor=u1, tiempo_publicado=now + timedelta(seconds=1))
        p2 = Post(contenido="post from susan5", autor=u2, tiempo_publicado=now + timedelta(seconds=4))
        p3 = Post(contenido="post from mary", autor=u3, tiempo_publicado=now + timedelta(seconds=3))
        p4 = Post(contenido="post from david", autor=u4, tiempo_publicado=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u1_following = db.session.scalars(u1.following.select()).all()
        print(u1_following)
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        #db.session.commit()

        # check the following posts Sof each user
        f1 = db.session.scalars(u1.following_posts()).all()
        f2 = db.session.scalars(u2.following_posts()).all()
        f3 = db.session.scalars(u3.following_posts()).all()
        f4 = db.session.scalars(u4.following_posts()).all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

if __name__ == '__main__':
    unittest.main()
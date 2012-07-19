from google.appengine.ext import db
from utils import valid_pw, make_pw_hash

class User(db.Model):
    name = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        return cls.all().filter('name = ', name).get()

    @classmethod
    def login(cls, name, password):
        user = cls.by_name(name)
        if user and valid_pw(name, password, user.password_hash):
            return user

    @classmethod
    def register(cls, name, password, email=None):
        pw_hash = make_pw_hash(name, password)
        return User(name = name,
                    password_hash = pw_hash,
                    email = email)
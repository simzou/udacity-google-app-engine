import os
import re
import hmac
import random
import webapp2
import jinja2
import string
import hashlib
from main import Handler
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

SECRET = "code"

class User(db.Model):
    name = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    email = db.StringProperty()

    @classmethod
    def by_id(self, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_name(self, name):
        return User.all().filter('name = ', name).get()

class BlogHandler(Handler):
    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.set_secure_cookie('user_id', '')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

class SignUpHandler(BlogHandler):
    def get(self):
        self.render('signup.html')
        
    def post(self):
        params = {}
        have_error = False
        
        params['username'] = user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verify   = self.request.get('verify')
        params['email']    = user_email    = self.request.get('email')
                
        valid_user = valid_username(user_username)
        valid_pass = valid_password(user_password)
        valid_mail = valid_email(user_email)
        
        if not valid_user:
            have_error = True
            params['error_username'] = 'That was not a valid username'
        if User.by_name(user_username):
            have_error = True
            params['error_username'] = 'Username already exists'
        if not valid_password:
            have_error = True
            params['error_password'] = 'Not a valid password'
        if user_password != user_verify:
            have_error = True
            params['error_verify'] = "Your passwords didn't match"
        if not valid_mail:
            have_error = True
            params['error_email'] = 'That was not a valid e-mail'

        if have_error:
            self.render('signup.html', **params)
        else:
            new_user = User(name=user_username, password_hash=make_pw_hash(user_username, user_password), email=user_email)
            new_user.put()
            self.user = new_user
            self.login(self.user)
            self.redirect('/welcome')

class WelcomeHandler(BlogHandler):
    def get(self):
        if self.user:
            visits = self.get_visits()
            self.render('welcome.html', user=self.user, visits=visits)
        else:
            self.redirect('/signup')

class LoginHandler(Handler):
    def get(self):
        self.render('login.html')
    
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        params = {}
        
        if username_exists(username):
            user = User.all().filter('name = ', username).get()
            user_id = user.key().id()
            if valid_pw(username, password, user.password_hash):
                self.response.headers.add_header('Set-Cookie', 'ID|Hash=%s; Path=/' % make_secure_val(str(user_id)))
                self.redirect('/welcome')
                return
            else:
                params['password_error'] = 'Invalid password'
        else:
            params['username_error'] = "Username doesn't exist"
            
        self.render('login.html', **params)

class LogoutHandler(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'ID|Hash=; Path=/')
        self.redirect('/signup')
        
def valid_username(username):
    user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return (username if user_re.match(username) else False)
    
def valid_password(password):
    password_re = re.compile(r"^.{3,20}$")
    return (password if password_re.match(password) else False)
    
def valid_email(email):
    email_re = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    return (True if email == '' else email_re.match(email))

def make_salt(): 
    return ''.join(random.choice(string.letters) for _ in xrange(5))
    
def make_pw_hash(name, pw, salt=None):
    if not salt: salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '{},{}'.format(h, salt)

def hash_str(s):
        return hmac.new(SECRET,s).hexdigest()

def make_secure_val(s):
        return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
        val = h.split('|')[0]
        if h == make_secure_val(val):
                return val
                
def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)
    
def username_exists(name):
    return User.all().filter('name = ', name).get()
    
app = webapp2.WSGIApplication([('/signup',SignUpHandler),
                               ('/welcome',WelcomeHandler),
                               ('/login', LoginHandler),
                               ('/logout', LogoutHandler)], 
                                debug=True)

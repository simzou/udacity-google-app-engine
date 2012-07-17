import os
import hmac
import json
import hashlib
import webapp2
import jinja2 
import random
import string
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates') 
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

SECRET = "code"

def hash_str(s):
        return hmac.new(SECRET,s).hexdigest()

def make_secure_val(s):
        return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
        val = h.split('|')[0]
        if h == make_secure_val(val):
                return val
def make_salt(): 
    return ''.join(random.choice(string.letters) for _ in xrange(5))
    
def make_pw_hash(name, pw, salt=None):
    if not salt: salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '{},{}'.format(h, salt)
               
def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)

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
        
class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
    	self.response.out.write(*args, **kwargs)
    	
    def render_str(self, template, **params):
    	t = jinja_environment.get_template(template)
        params['user'] = self.user
    	return t.render(params)

    def render(self, template, **kwargs):
    	self.write(self.render_str(template,**kwargs))
    	
    def set_secure_cookie(self, name, val):
    	cookie_val = make_secure_val(val)
    	self.response.headers.add_header(
    		'Set-Cookie', 
    		'%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self,name):
    	cookie_val = self.request.cookies.get(name)
    	return cookie_val and check_secure_val(cookie_val)

    def get_visits(self):
		visits = str(self.read_secure_cookie('visits')) # for isdigit()
		return (int(visits) + 1 if visits.isdigit() else 0)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


class MainPage(Handler):

    def get(self):
        # self.response.headers['Content-Type'] = 'text/plain'
        visits = self.get_visits()
        self.set_secure_cookie('visits', str(visits))
        self.render("index.html", visits=visits)

class JSONBlog(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC')
        jsonlist = []
        for post in posts:
            d = {}
            d['subject'] = post.subject
            d['content'] = post.content
            jsonlist.append(d)
        self.write(json.dumps(jsonlist))

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/?\.json', JSONBlog)], 
                                debug=True)

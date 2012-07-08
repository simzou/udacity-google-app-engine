#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
import random
import webapp2
import jinja2
import string
import hashlib
from main import Handler
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

class User(db.Model):
    name = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    email = db.StringProperty()

class SignUpHandler(Handler):
    def get(self):
        self.render('signup.html')
        
    def post(self):
        params = {}
        
        params['username'] = user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verify   = self.request.get('verify')
        params['email']    = user_email    = self.request.get('email')
        
        if username_exists(user_username):
            params['username_error'] = 'Username already exists'
            self.render('signup.html', **params)
            return
        
        valid_user = valid_username(user_username)
        valid_pass = valid_password(user_password)
        valid_mail = valid_email(user_email)
        
        if (valid_user and valid_pass and user_password == user_verify and valid_mail):
            
            new_user = User(name=user_username, password_hash=make_pw_hash(user_username, user_password), email=user_email)
            new_user.put()
            new_id = new_user.key().id()
            self.response.headers.add_header('Set-Cookie', 'ID|Hash=%s; Path=/' % make_secure_val(str(new_id)))
            
            # self.redirect('/welcome?username=%s' % user_username)
            self.redirect('/welcome')
        if not valid_user:
            params['username_error'] = 'That was not a valid username'
        if not valid_pass:
            params['password_error'] = 'Not a valid password'
        if (user_password != user_verify):
            params['verify_error'] = "Your passwords didn't match"
        if not valid_mail:
            params['email_error'] = 'That was not a valid e-mail'
       
        self.render('signup.html', **params)
                
class WelcomeHandler(Handler):
    def get(self):
        # username = self.request.get('username')
        cookie = self.request.cookies.get('ID|Hash')
        if cookie and check_secure_val(cookie):
            user_id, id_hash = cookie.split('|')
            username = User.get_by_id(int(user_id))
            self.response.out.write("Welcome, %s" % username.name)
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
        return hashlib.md5(s).hexdigest()

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

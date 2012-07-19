import re

from handlers.base import Handler
from models.user import User

class UserHandler(Handler):

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))
        self.user = user

    def logout(self):
        self.response.delete_cookie('user_id')
        self.response.delete_cookie('visits')
        
class LoginPage(UserHandler):

    def get(self):
        self.render('login.html')
    
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        self.user = User.login(username, password)

        params = {}
		
        if self.user:
            self.login(self.user)
            self.redirect('/welcome')
        else: 
            params['error'] = 'Invalid login'        
            self.render('login.html', **params)
						
class LogoutPage(UserHandler):
    def get(self):
        self.logout()
        self.redirect('/signup')
 
class SignUpPage(UserHandler):

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
        if not valid_pass:
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
            new_user = User.register(user_username, user_password, user_email)
            new_user.put()
            self.user = new_user
            self.login(self.user)
            self.redirect('/welcome')
            
class WelcomePage(UserHandler):

    def get(self):
        if self.user:
            visits = self.get_visits()
            self.render('welcome.html', user=self.user, visits=visits)
        else:
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

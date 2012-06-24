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
import webapp2
import re, string
import cgi
import jinja2
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

def escape_html(s):
    return cgi.escape(s, quote=True)

signup_form="""
    <h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">
            Username
          </td>
          <td>
            <input type="text" name="username" value="%(username)s">
          </td>
          <td class="error">
            <div style="color: red">%(username_error)s</div>
          </td>
        </tr>

        <tr>
          <td class="label">
            Password
          </td>
          <td>
            <input type="password" name="password" value="">
          </td>
          <td class="error">
            <div style="color: red">%(password_error)s</div>
          </td>
        </tr>

        <tr>
          <td class="label">
            Verify Password
          </td>
          <td>
            <input type="password" name="verify" value="">
          </td>
          <td class="error">
            <div style="color: red">%(verify_error)s</div>
          </td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value="%(email)s">
          </td>
          <td class="error">
            <div style="color: red">%(email_error)s</div>
          </td>
        </tr>
      </table>

      <input type="submit">
    </form>
"""
class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)
    
    def render_str(self, template, **params):
        t = jinja_environment.get_template(template)
        return t.render(params)
        
    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))
        
        
class SignUpHandler(webapp2.RequestHandler):
    
    def get(self):
        write_form(self)
        
    def post(self):
        user_username = escape_html(self.request.get('username'))
        user_password = escape_html(self.request.get('password'))
        user_verify   = escape_html(self.request.get('verify'))
        user_email    = escape_html(self.request.get('email'))
        
        valid_user = valid_username(user_username)
        valid_pass = valid_password(user_password)
        valid_mail = valid_email(user_email)
        
        username_error = ''
        password_error = ''
        verify_error   = ''
        email_error    = ''
        
        if (valid_user and valid_pass and user_password == user_verify and valid_mail):
            self.redirect('/welcome?username=%s' % user_username)
            self.response.out.write('Welcome, %s' % user_username)
        if not valid_user:
            username_error = 'That was not a valid username'
        if not valid_pass:
            password_error = 'Not a valid password'
        if (user_password != user_verify):
            verify_error = "Your passwords didn't match"
        if not valid_mail:
            email_error = 'That was not a valid e-mail'
            
        write_form(self, username=user_username,
                         email=user_email,
                         user_error=username_error, 
                         password_error=password_error, 
                         email_error=email_error, 
                         verify_error=verify_error)

class SignUpHandler(Handler):
    def get(self):
        self.render('signup.html')
                         
def write_form(self, username='', password='', email='', 
               user_error ='', password_error='', verify_error='', email_error=''):

    self.response.out.write(signup_form % { "username": username,                                        
                                        "password": password,
                                        "email": email,
                                        "username_error": user_error,
                                        "verify_error": verify_error,
                                        "password_error": password_error,
                                        "email_error": email_error})                
def valid_username(username):
    user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return (username if user_re.match(username) else False)
    
def valid_password(password):
    password_re = re.compile(r"^.{3,20}$")
    return (password if password_re.match(password) else False)
    
def valid_email(email):
    email_re = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    return (True if email == '' else email_re.match(email))
            
class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        username = self.request.get('username')
        self.response.out.write("Welcome, %s" % username)

app = webapp2.WSGIApplication([('/signup',SignUpHandler),
                               ('/welcome',WelcomeHandler)], 
                                debug=True)

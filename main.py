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

import handlers.blog as blog
import handlers.signup as signup
import handlers.rot13 as rot13

app = webapp2.WSGIApplication([('/', blog.MainPage),
                               ('/?\.json', blog.JSONBlog),
							   ('/blog/?', blog.MainPage),
                               ('/blog/?\.json', blog.JSONBlog),

                               ('/newpost', blog.NewPostPage),
                               ('/blog/newpost', blog.NewPostPage),
							   
                               ('/blog/post/(\d+)', blog.PostPage),
                               ('/blog/post/(\d+)/?\.json', blog.JSONPost),
							   
                               ('/flush/?', blog.FlushCache),
							   ('/signup', signup.SignUpPage),
                               ('/welcome', signup.WelcomePage),
                               ('/login', signup.LoginPage),
                               ('/logout', signup.LogoutPage),
							   
							   ('/rot13', rot13.ROT13Page)],
                                debug=True)

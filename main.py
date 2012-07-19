import os
import webapp2
import jinja2 
import logging

template_dir = os.path.join(os.path.dirname(__file__), 'templates') 
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                                       autoescape=True)

app = webapp2.WSGIApplication([
                               ('/', 'handlers.blog.MainPage'),
                               ('/?\.json', 'handlers.blog.JSONBlog'),
							   ('/blog/?', 'handlers.blog.MainPage'),
                               ('/blog/?\.json', 'handlers.blog.JSONBlog'),

                               ('/newpost', 'handlers.blog.NewPostPage'),
                               ('/blog/newpost', 'handlers.blog.NewPostPage'),
							   
                               ('/blog/post/(\d+)', 'handlers.blog.PostPage'),
                               ('/blog/post/(\d+)/?\.json', 'handlers.blog.JSONPost'),
							   
                               ('/flush/?', 'handlers.blog.FlushCache'),
                               
							   ('/signup', 'handlers.signup.SignUpPage'),
                               ('/welcome', 'handlers.signup.WelcomePage'),
                               ('/login', 'handlers.signup.LoginPage'),
                               ('/logout', 'handlers.signup.LogoutPage'),
							   
							   ('/rot13', 'handlers.rot13.ROT13Page')
                               
                               ],
                                debug=True)

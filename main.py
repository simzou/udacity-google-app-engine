import os
import webapp2
import jinja2 
import logging

template_dir = os.path.join(os.path.dirname(__file__), 'templates') 
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                                       autoescape=True)

PAGE_RE = r'/((?:[a-zA-Z0-9_-]+/?)*)'

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
                               
                               ('/rot13', 'handlers.rot13.ROT13Page'),

                               ('/wiki/signup', 'handlers.signup.SignUpPage'),
                               ('/wiki/welcome', 'handlers.signup.WelcomePage'),
                               ('/wiki/login', 'handlers.signup.LoginPage'),
                               ('/wiki/logout', 'handlers.signup.LogoutPage'),

                               #('/wiki/?', 'handlers.wiki.FrontPage'),
                               ('/wiki/_edit' + PAGE_RE, 'handlers.wiki.EditPage'),
                               ('/wiki/_history' + PAGE_RE, 'handlers.wiki.HistoryPage'),
                               ('/wiki' + PAGE_RE, 'handlers.wiki.WikiPage'),
                               ],
                                debug=True)

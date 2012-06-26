import webapp2
import jinja2 
import os
from google.appengine.ext import db
from main import Handler

template_dir = os.path.join(os.path.dirname(__file__), 'templates') 
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
		
    
class MainPage(Handler):

    def get(self):
        posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC')
        self.render('blog.html', posts=posts)
		
class NewPostPage(Handler):
        
    def get(self):
		self.render('newpost.html')
        
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        
        if subject and content:
            post = Post(subject=subject, content=content)
            post.put()
            id = post.key().id()
            self.redirect('/blog/post/' + str(id))
        else:
            error = "Need both subject and content"
            self.render('newpost.html', subject=subject,content=content,error=error)
        
class PostPage(Handler):
    def get(self,post_id):
        post = Post.get_by_id(int(post_id))
        self.render("post.html", subject=post.subject, content=post.content)
		
app = webapp2.WSGIApplication([('/blog/?', MainPage),
                               ('/blog/newpost', NewPostPage),
                               ('/blog/post/(\d+)', PostPage)], 
                               debug=True)

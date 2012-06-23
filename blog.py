import webapp2
import jinja2 
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates') 
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Blog(db.Model):
    subject = db.StringProperty()
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class Handler(webapp2.RequestHandler):
	def write(self, *args, **kwargs):
		self.response.out.write(*args, **kwargs)
		
	def render_str(self, template, **params):
		t = jinja_environment.get_template(template)
		return t.render(params)

	def render(self, template, **kwargs):
		self.write(self.render_str(template,**kwargs))
		
class MainPage(Handler):

    def get(self):
        posts = db.GqlQuery('SELECT * FROM Blog ORDER BY created DESC')
        self.render('blog.html', posts=posts)
		
class NewPostPage(Handler):

    def render_page(self, subject='', content='', error=''):
        self.render('newpost.html', subject=subject, content=content, error=error)
        
    def get(self):
		self.render_page()
        
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        
        if subject and content:
            blog = Blog(subject=subject, content=content)
            blog.put()
            id = int(blog.key().id())
            self.redirect('/unit3/blog/' + str(id))
        else:
            error = "Need both subject and content"
            self.render_page(subject=subject,content=content,error=error)
        
class PostPage(Handler):
    def get(self,post_id):
        post = Blog.get_by_id(int(post_id))
        self.render("post.html", subject=post.subject, content=post.content)
		
app = webapp2.WSGIApplication([('/unit3/blog', MainPage),
                               ('/unit3/blog/newpost', NewPostPage),
                               ('/unit3/blog/(\d+)', PostPage)], 
                               debug=True)

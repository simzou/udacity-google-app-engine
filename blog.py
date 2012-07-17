import os
import json
import webapp2
import jinja2 
from google.appengine.ext import db
from main import Handler

template_dir = os.path.join(os.path.dirname(__file__), 'templates') 
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

def render_str(template, **params):
    t = jinja_environment.get_template(template)
    return t.render(params)

class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
		
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post-content.html", post=self)
    
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
            post_id = post.key().id()
            self.redirect('/blog/post/%s' % post_id)
        else:
            error = "Need both subject and content"
            self.render('newpost.html', subject=subject,content=content,error=error)
        
class PostPage(Handler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.render("post.html", post=post)
		
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

class JSONPost(Handler):
    def get(self, post_id):
        self.response.headers['Content-Type'] = 'application/json'
        d = {}
        post = Post.get_by_id(int(post_id))
        d['subject'] = post.subject
        d['content'] = post.content
        self.write(json.dumps(d))


app = webapp2.WSGIApplication([('/blog/?', MainPage),
                               #('/blog/newpost', NewPostPage),
                               ('/newpost', NewPostPage),
                               ('/blog/post/(\d+)', PostPage),
                               ('/blog/?\.json', JSONBlog),
                               ('/?\.json', JSONBlog),
                               ('/', MainPage),
                               ('/blog/post/(\d+)/?\.json', JSONPost)], 
                               debug=True)

import os
import time
import json

import webapp2
import jinja2 

from google.appengine.ext import db
from google.appengine.api import memcache

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

    def as_dict(self):
        time_fmt = '%c'
        d = {'subject': self.subject,
             'content': self.content, 
             'created': self.created.strftime(time_fmt),
             'last_modified': self.last_modified.strftime(time_fmt)}
        return d
    
class MainPage(Handler):

    def get(self):
        key = 'front_page'
        time_key = 'front_queried'
        posts = memcache.get(key)
        queried = memcache.get(time_key)
        if posts and queried: pass
        else: 
            posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC')
            memcache.set(key, posts)
            queried = time.time()
            memcache.set(time_key, queried)
        last_queried = '%0.2f' % (time.time() - queried)
        self.render('blog.html', posts=posts, last_queried=last_queried)
		
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
        post = memcache.get(post_id)
        time_key = '%s_queried' % post_id
        queried = memcache.get(time_key)

        if post and queried: pass
        else:
            queried = time.time()
            post = Post.get_by_id(int(post_id))
            memcache.set(post_id, post)
            memcache.set(time_key, queried)

        last_queried = '%0.2f' % (time.time() - queried)
        self.render("post.html", post=post, last_queried=last_queried)
		
class JSONBlog(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC')
        self.write(json.dumps([p.as_dict() for p in posts]))

class JSONPost(Handler):
    def get(self, post_id):
        self.response.headers['Content-Type'] = 'application/json'
        post = Post.get_by_id(int(post_id))
        self.write(json.dumps(post.as_dict()))

class FlushCache(Handler):
    def get(self):
        memcache.flush_all()
        self.redirect('/')

app = webapp2.WSGIApplication([('/blog/?', MainPage),
                               #('/blog/newpost', NewPostPage),
                               ('/newpost', NewPostPage),
                               ('/blog/post/(\d+)', PostPage),
                               ('/blog/?\.json', JSONBlog),
                               ('/?\.json', JSONBlog),
                               ('/', MainPage),
                               ('/blog/post/(\d+)/?\.json', JSONPost),
                               ('/flush/?', FlushCache)], 
                               debug=True)

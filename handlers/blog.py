import time
import json

from google.appengine.api import memcache
from google.appengine.ext import db

from handlers.base import Handler
from models.post import Post

from main import template_dir, jinja_environment
    
class MainPage(Handler):

    def get(self):
        key = 'front_page'
        time_key = 'front_queried'
        posts = memcache.get(key)
        queried = memcache.get(time_key)
        if posts and queried: pass
        else: 
            posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC')
            posts = list(posts)
            memcache.set(key, posts)
            queried = time.time()
            memcache.set(time_key, queried)
        last_queried = 'Queried %0.2fs ago' % (time.time() - queried)
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

        last_queried = 'Queried %0.2fs ago' % (time.time() - queried)
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


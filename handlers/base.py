import webapp2

from utils import check_secure_val, make_secure_val
from models.user import User

from main import template_dir, jinja_environment

class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
    	self.response.out.write(*args, **kwargs)
    	
    def render_str(self, template, **params):
    	t = jinja_environment.get_template(template)
        params['user'] = self.user
    	return t.render(params)

    def render(self, template, **kwargs):
    	self.write(self.render_str(template,**kwargs))
    	
    def set_secure_cookie(self, name, val):
    	cookie_val = make_secure_val(val)
    	self.response.headers.add_header(
    		'Set-Cookie', 
    		'%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self,name):
    	cookie_val = self.request.cookies.get(name)
    	return cookie_val and check_secure_val(cookie_val)

    def get_visits(self):
		visits = str(self.read_secure_cookie('visits')) # for isdigit()
		if not visits.isdigit(): 
			visits = 0
		visits = str(int(visits) + 1)
		self.set_secure_cookie('visits', visits)
		return visits

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def check_login(self):
        if not self.user:
            self.redirect('/signup')

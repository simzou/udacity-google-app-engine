import webapp2
import jinja2
import os
from main import Handler

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

class ROT13Page(Handler):
    def get(self):
        self.render('rot13.html')
    def post(self):
        user_text = self.request.get('text').encode('rot13')
        text_map = {'text': user_text}
        self.render('rot13.html', **text_map)
        
app = webapp2.WSGIApplication([('/rot13',ROT13Page)], 
                                debug=True)

from google.appengine.ext import db
from main import template_dir, jinja_environment

def render_str(template, **params):
    t = jinja_environment.get_template(template)
    return t.render(params)

class Page(db.Model):
    name    = db.StringProperty()
    content = db.TextProperty()
    history = []
    
    @classmethod
    def by_name(cls, name):
        return cls.all().filter('name = ', name).get()

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        #return render_str("wiki.html")

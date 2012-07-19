from google.appengine.ext import db

from main import template_dir, jinja_environment

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
from collections import namedtuple

from google.appengine.ext import db

from handler.base import Handler

Entry = namedtuple('Entry', ('date', 'content'))

class Page(db.Model):
    name    = db.StringProperty()
    content = db.TextProperty()
    history = db.ListProperty(Entry)
    

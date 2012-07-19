import time
import datetime

from collections import namedtuple

from handlers.base import Handler
from models.page import Page

Entry = namedtuple('Entry', ('date', 'content', 'user'))

class WikiPage(Handler):
    
    def get(self, name):
        params={}
        params['title'] = name
        # page = Page(name='test', content='testing content\nnewline')
        page = Page.by_name(name)
        if not page:
            self.redirect('/wiki/_edit/'+name)
        else:
            page.render()
            params['page'] = page
            self.render('wiki.html', **params)
        
class EditPage(Handler):
    
    def get(self, name):
        self.check_login()

        params = {}
        # page = Page(name='test', content='testing content')
        page = Page.by_name(name)
        params['title'] = name
        if page:
            params['content'] = page.content
        self.render('wiki-form.html', **params)
    
    def post(self, name):
        self.check_login()
        page = Page.by_name(name)
        content = self.request.get('content')

        time_fmt = '%a %c'
        curr_time = datetime.datetime.today().strftime(time_fmt)
        entry = Entry(curr_time, content, self.user.name)
        if page:
            page.content=content
            page.put()
        else:
            page = Page(name=name, content=content, history=[])
            page.put()
        page.history.append(entry)
        self.redirect('/wiki/'+name)


            # get page by name
            # update page content
            # render wiki.html with new content


class HistoryPage(Handler):

    def get(self, name):
        params = {}
        params['title'] = name
        page = Page.by_name(name)
        if not page:
            self.redirect('/wiki/_edit/'+name)
            return

        # get page by name
        # pass history into template
        # page1 = Page(name='page1', content='page1content')
        # entry1 = Entry('date1', 'content1', 'name1')
        # entry2 = Entry('date2', 'content2', 'name2')
        # entry3 = Entry('date3', 'content3', 'name3')
        # page1.history.append(entry1)
        # page1.history.append(entry2)
        # page1.history.append(entry3)

        params['history'] = page.history
        self.render('wiki-history.html', **params)
    
import os
import webapp2
import jinja2
from webapp2 import uri_for
from google.appengine.ext import ndb
from models import Paste



JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Handler(webapp2.RequestHandler):
    def render(self, name, **values):
        template = JINJA_ENVIRONMENT.get_template(name)
        self.response.write(template.render(values))


class MainPage(Handler):
    def get(self):
        pastes = Paste.query()
        self.render('index.html', pastes=pastes)


class CreatePaste(Handler):
    def get(self):
        self.render('create.html')

    def post(self):
        paste = Paste()
        if self.request.get('title', None):
            paste.title = self.request.get('title', None)
        if self.request.get('content', None):
            paste.content = self.request.get('content', None)
        paste.put()

        self.redirect(uri_for('view_paste', key=paste.key.id()))


class ViewPaste(Handler):
    def get(self, key):
        paste = Paste.get_by_id(int(key))
        self.render('view.html', paste=paste)


handlers = [
    ('/', MainPage),
    ('/paste/create', CreatePaste),
    webapp2.Route(r'/paste/view/<key:\d+>', ViewPaste, name='view_paste')
]

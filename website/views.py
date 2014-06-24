import os
import webapp2
import jinja2
import logging

from webapp2 import uri_for
from webapp2_extras import sessions
from google.appengine.api import users
from google.appengine.ext import ndb

from models import Paste
from models import UserRef
from models import Tag


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def login_required(handler):
    def check_login(self, *args, **kwargs):
        if not users.get_current_user():
            self.redirect('/login')
        return handler(self, *args, **kwargs)
    return check_login


def get_user_dict(user_ref):
    return {'email': user_ref.user.email(),
            'nickname': user_ref.nickname}


class Handler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def render(self, name, **values):
        template = JINJA_ENVIRONMENT.get_template(name)
        values['users'] = users
        user = users.get_current_user()
        if not user:
            self.session['user'] = None
        values['user'] = self.session['user']
        values['uri_for'] = webapp2.uri_for
        self.response.write(template.render(values))


class MainPage(Handler):
    def get(self):
        pastes = Paste.query()
        self.render('index.html', pastes=pastes)


class LoginPage(Handler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_ref = UserRef.query(UserRef.user == user).get()
            if user_ref:
                self.session['user'] = get_user_dict(user_ref)
                self.redirect('/')
            else:
                self.redirect('/register')
        else:
            self.render('login.html')


class RegisterPage(Handler):
    def get(self):
        self.render('register.html')

    def post(self):
        nickname = self.request.get('nickname', None)
        if nickname:
            user_ref = UserRef()
            user_ref.user = users.get_current_user()
            user_ref.nickname = nickname
            user_ref.put()
            self.session['user'] = get_user_dict(user_ref)
            self.redirect('/')


class CreatePaste(Handler):
    @login_required
    def get(self):
        self.render('create.html')

    @login_required
    def post(self):
        paste = Paste()
        if self.request.get('title', None):
            paste.title = self.request.get('title', None)
        if self.request.get('content', None):
            paste.content = self.request.get('content', None)
        if self.request.get('tags', None):
            tags = self.request.get('tags').split()
            for tag in tags:
                tag_obj = Tag.query(Tag.name == tag).get()
                if tag_obj:
                    tag_obj.counts += 1
                    tag_obj.put()
                else:
                    tag_obj = Tag(name=tag)
                    tag_obj.put()
                paste.tags.append(tag_obj)
        paste.user = users.get_current_user()
        paste.put()

        self.redirect(uri_for('view_paste', key=paste.key.id()))


class ViewPaste(Handler):
    def get(self, key):
        paste = Paste.get_by_id(int(key))
        self.render('view.html', paste=paste)


class TagsPage(Handler):
    def get(self):
        self.render('tags.html', tags=Tag.query())


class ViewTag(Handler):
    def get(self, name):
        tag = Tag.query(Tag.name == name).get()
        pastes = Paste.query(Paste.tags.IN([tag]))
        self.render('tag_view.html', tag=tag, pastes=pastes)


class RankPage(Handler):
    def get(self):
        most_visited_pastes = Paste.query()
        self.render('rank.html', most_visited_pastes=most_visited_pastes)


class ViewUser(Handler):
    def get(self, slug):
        self.response.write("NOT finished")


handlers = [
    ('/', MainPage),
    ('/login', LoginPage),
    ('/register', RegisterPage),
    ('/paste/create', CreatePaste),
    ('/rank', RankPage),
    webapp2.Route(r'/paste/<key:\d+>', ViewPaste, name='view_paste'),
    ('/tags', TagsPage),
    webapp2.Route(r'/tag/<name>', ViewTag, name='view_tag'),
    webapp2.Route(r'/user/<slug>', ViewUser, name='view_user'),
]

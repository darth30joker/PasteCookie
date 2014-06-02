from google.appengine.ext import ndb


class Paste(ndb.Model):
    title = ndb.StringProperty(indexed=False)
    content = ndb.TextProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now_add=True)

    @property
    def id(self):
        return self.key.id()

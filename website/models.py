from google.appengine.ext import ndb


class UserRef(ndb.Model):
    user = ndb.UserProperty()
    nickname = ndb.StringProperty()

    @property
    def id(self):
        return self.key.id()


class Paste(ndb.Model):
    user = ndb.UserProperty()
    title = ndb.StringProperty(indexed=False)
    content = ndb.TextProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now_add=True)

    @property
    def id(self):
        return self.key.id()

    @property
    def user_ref(self):
        return UserRef.query(UserRef.user == self.user).get()

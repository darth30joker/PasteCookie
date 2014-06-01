import webapp2
from views import handlers

application = webapp2.WSGIApplication(handlers, debug=True)

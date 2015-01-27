# -*- coding: utf-8 -*-
__author__ = 'KAPRAL'

from google.appengine.api import users
import cgi
import webapp2
import nsuemScheduleParser

# constants

HEADER_HTML = """\
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
  </head>
  <body>
"""

FOOTER_HTML = """\
  </body>
</html>
"""

WHITESPACE = '<br /><br />'

GROUP_SELECTION_FORM = """\
<form action="/dothemagic" method="post">
<select name="group-selector" style="width:100px; margin-bottom:10px">
<option name="1761" value="1761">1761</option>
<option name="1762" value="1762">1762</option>
<option name="2761" value="2761">2761</option>
</select>
<div><input type="submit" value="Ду зе мэджик"></div>
</form>
"""

# end of constants

class GroupSelectionPage(webapp2.RequestHandler):

    def get(self):

        user = users.get_current_user()

        if user:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(HEADER_HTML)

            self.response.write('Hello, ' + user.nickname() + WHITESPACE)
            self.response.write(GROUP_SELECTION_FORM)
            self.response.write(FOOTER_HTML)

        else:
            self.redirect(users.create_login_url(self.request.uri))

class DoTheMagic(webapp2.RequestHandler):

    def get(self):
        self.response.write("please go back and do this properly")


    def post(self):
        # Checks for active Google account session
        user = users.get_current_user()

        group = cgi.escape(self.request.get('group-selector'))

        if user:

            schedule = nsuemScheduleParser.getEventsList(group)
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(HEADER_HTML)
            self.response.write('magic for  ' + group + WHITESPACE)
            for event in schedule:
                for key in event:
                    self.response.write("%s : %s" % (key, event[key]))
                self.response.write(WHITESPACE)
            self.response.write(FOOTER_HTML)

        else:
            self.response.write("please go back and do this properly")


application = webapp2.WSGIApplication([
    ('/', GroupSelectionPage),
    ('/dothemagic', DoTheMagic),
], debug=True)